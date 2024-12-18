// Ana sayfa main.js'den filtreleme fonksiyonlarını kopyalayıp,
// performQuery fonksiyonunu grafik oluşturacak şekilde güncelleyelim:

async function performQuery() {
    try {
        const tableName = document.getElementById('tableSelect').value;
        if (!tableName) {
            showError('Lütfen bir tablo seçiniz');
            return;
        }
        
        // Filtreleri topla
        const filters = {};
        const selects = document.querySelectorAll('#filterContainer select');
        selects.forEach(select => {
            if (select.value) {
                filters[select.name] = select.value;
            }
        });
        
        const queryString = new URLSearchParams(filters).toString();
        const response = await fetch(`/api/${tableName}/grafik-veriler?${queryString}`);
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || 'Bilinmeyen bir hata oluştu');
        }
        
        if (result.data && result.data.length > 0) {
            // Grafikleri göster
            document.getElementById('chartsCard').style.display = 'block';
            
            // Yıllara göre trend grafiği
            createYearlyTrendChart(result.data);
            
            // İl karşılaştırma grafiği
            createCityComparisonChart(result.data);
            
            showSuccess(`${result.data.length} adet veri görselleştirildi`);
        } else {
            showError('Seçilen kriterlere uygun sonuç bulunamadı');
        }
        
    } catch (error) {
        console.error('Sorgu hatası:', error);
        showError('Sorgu yapılırken bir hata oluştu: ' + error.message);
    }
}

function createYearlyTrendChart(data) {
    const ctx = document.getElementById('yearlyTrendChart').getContext('2d');
    
    // Yıllara göre verileri grupla
    const yearlyData = {};
    data.forEach(item => {
        if (!yearlyData[item.yil]) {
            yearlyData[item.yil] = 0;
        }
        yearlyData[item.yil] += item.kisi_sayisi;
    });
    
    const years = Object.keys(yearlyData).sort();
    const values = years.map(year => yearlyData[year]);
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: years,
            datasets: [{
                label: 'Kişi Sayısı',
                data: values,
                borderColor: 'rgb(75, 192, 192)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'Yıllara Göre Değişim'
                }
            }
        }
    });
}

function createCityComparisonChart(data) {
    const ctx = document.getElementById('cityComparisonChart').getContext('2d');
    
    // İllere göre verileri grupla
    const cityData = {};
    data.forEach(item => {
        if (!cityData[item.il]) {
            cityData[item.il] = 0;
        }
        cityData[item.il] += item.kisi_sayisi;
    });
    
    // En yüksek 10 ili al
    const sortedCities = Object.entries(cityData)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 10);
    
    const cities = sortedCities.map(([city]) => city);
    const values = sortedCities.map(([,value]) => value);
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: cities,
            datasets: [{
                label: 'Kişi Sayısı',
                data: values,
                backgroundColor: 'rgb(54, 162, 235)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: 'İllere Göre Dağılım (İlk 10)'
                }
            }
        }
    });
}

// Tabloları yükleme fonksiyonu
async function loadTables() {
    try {
        const response = await fetch('/api/tablolar');
        const tables = await response.json();
        
        const tableSelect = document.getElementById('tableSelect');
        tableSelect.innerHTML = '<option value="">Tablo Seçiniz</option>';
        
        tables.forEach(table => {
            const option = document.createElement('option');
            option.value = table.id;
            option.textContent = table.ad;
            tableSelect.appendChild(option);
        });
        
        $(tableSelect).trigger('change');
        
    } catch (error) {
        console.error('Tablolar yüklenirken hata:', error);
        showError('Tablolar yüklenirken bir hata oluştu');
    }
}

// Filtreleri yükleme fonksiyonu
async function loadTableFilters(tableName) {
    try {
        const filterContainer = document.getElementById('filterContainer');
        filterContainer.innerHTML = '';
        
        const kolonResponse = await fetch(`/api/${tableName}/kolonlar`);
        const kolonlar = await kolonResponse.json();
        
        for (const kolonAdi of kolonlar) {
            const formGroup = document.createElement('div');
            formGroup.className = 'form-group';
            
            const label = document.createElement('label');
            label.className = 'form-label';
            label.textContent = kolonAdi;
            
            const select = document.createElement('select');
            select.className = 'form-select';
            
            // Kolon adını API için hazırla
            const columnMappings = {
                'Yaş': 'yas',
                'Yıl': 'yil',
                'Ceza Türü': 'ceza_turu',
                'Suç Türü': 'suc_turu',
                'Eğitim Durumu': 'egitim_durumu',
                'İş Durumu': 'is_durumu',
                'Medeni Durum': 'medeni_durum',
                'İnfaza Davet Şekli': 'infaza_davet_sekli',
                'Yerleşim Yeri': 'yerlesim_yeri',
                'Yerleşim Yeri (Ülke)': 'yerlesim_yeri_ulke',
                'Cinsiyet': 'cinsiyet',
                'İl': 'il',
                'Uyruk': 'uyruk'
            };
            
            const columnName = columnMappings[kolonAdi] || kolonAdi
                .toLowerCase()
                .normalize("NFD")
                .replace(/[\u0300-\u036f]/g, "")
                .replace(/\s+/g, '_');
            
            select.name = columnName;
            select.innerHTML = '<option value="">Tümü</option>';
            
            try {
                const response = await fetch(`/api/${tableName}/unique-values/${columnName}`);
                const values = await response.json();
                
                if (Array.isArray(values)) {
                    values.sort((a, b) => {
                        if (columnName === 'yil' || columnName === 'yas') {
                            return Number(a) - Number(b);
                        }
                        return String(a).localeCompare(String(b), 'tr');
                    });
                    
                    values.forEach(value => {
                        if (value !== null && value !== '') {
                            const option = document.createElement('option');
                            option.value = value;
                            option.textContent = value;
                            select.appendChild(option);
                        }
                    });
                }
            } catch (error) {
                console.error(`${kolonAdi} için değerler yüklenirken hata:`, error);
            }
            
            formGroup.appendChild(label);
            formGroup.appendChild(select);
            filterContainer.appendChild(formGroup);
            
            $(select).select2({
                placeholder: 'Seçiniz',
                allowClear: true,
                width: '100%',
                language: {
                    noResults: function() {
                        return "Sonuç bulunamadı";
                    }
                }
            });
        }
        
    } catch (error) {
        console.error('Filtreler yüklenirken hata:', error);
        throw error;
    }
}

// DOM yüklendiğinde
document.addEventListener('DOMContentLoaded', function() {
    // Select2'yi initialize et
    $('#tableSelect').select2({
        placeholder: 'Tablo Seçiniz',
        allowClear: true,
        width: '100%',
        language: {
            noResults: function() {
                return "Sonuç bulunamadı";
            }
        }
    });

    // Tabloları yükle
    loadTables();
    
    // Event listener'ları ekle
    const tableSelect = document.getElementById('tableSelect');
    const showFiltersBtn = document.getElementById('showFilters');
    const filterSection = document.getElementById('filterSection');
    
    // Tablo seçimi değiştiğinde
    $(tableSelect).on('change', function() {
        const selectedValue = this.value;
        showFiltersBtn.disabled = !selectedValue;
        
        if (!selectedValue) {
            filterSection.style.display = 'none';
            document.getElementById('filterContainer').innerHTML = '';
        }
    });
    
    // Filtreleri göster butonu
    showFiltersBtn.addEventListener('click', async function() {
        const selectedTable = tableSelect.value;
        if (selectedTable) {
            try {
                await loadTableFilters(selectedTable);
                filterSection.style.display = 'block';
                filterSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } catch (error) {
                console.error('Filtreler yüklenirken hata:', error);
                showError('Filtreler yüklenirken bir hata oluştu');
            }
        }
    });
    
    // Form submit
    document.getElementById('queryForm').addEventListener('submit', function(e) {
        e.preventDefault();
        performQuery();
    });

    // Sidebar toggle fonksiyonu
    const toggleButton = document.querySelector('.toggle-sidebar');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    toggleButton.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('expanded');
    });

    // Sıfırlama butonu için event listener
    document.getElementById('resetFilters').addEventListener('click', function() {
        // Tablo seçimini sıfırla
        const tableSelect = document.getElementById('tableSelect');
        tableSelect.value = '';
        
        // Select2'yi güncelle
        $(tableSelect).val('').trigger('change');
        
        // Filtre bölümünü gizle
        const filterSection = document.getElementById('filterSection');
        filterSection.style.display = 'none';
        
        // Filtre container'ı temizle
        document.getElementById('filterContainer').innerHTML = '';
        
        // Grafik kartını gizle
        document.getElementById('chartsCard').style.display = 'none';
        
        // Varsa alert'i kaldır
        const oldAlert = document.querySelector('.alert');
        if (oldAlert) {
            oldAlert.remove();
        }
        
        // Başarı mesajını göster
        showSuccess('Filtreler başarıyla sıfırlandı');
        
        // Filtre butonunu deaktif et
        document.getElementById('showFilters').disabled = true;
    });
});

// Hata ve başarı mesajları için yardımcı fonksiyonlar
function showError(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show mt-3';
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const oldAlert = document.querySelector('.alert');
    if (oldAlert) {
        oldAlert.remove();
    }
    
    document.querySelector('.content-wrapper').insertBefore(alertDiv, document.getElementById('chartsCard'));
}

function showSuccess(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show mt-3';
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const oldAlert = document.querySelector('.alert');
    if (oldAlert) {
        oldAlert.remove();
    }
    
    document.querySelector('.content-wrapper').insertBefore(alertDiv, document.getElementById('chartsCard'));
} 