document.addEventListener('DOMContentLoaded', function() {
    // Tabloları yükle
    loadTables();
    
    // Form submit olayını dinle
    document.getElementById('queryForm').addEventListener('submit', function(e) {
        e.preventDefault();
        performQuery();
    });
    
    // Tablo seçimi değiştiğinde
    const tableSelect = document.getElementById('tableSelect');
    tableSelect.addEventListener('change', async function() {
        const selectedValue = this.value;
        console.log('Seçilen tablo ID:', selectedValue);  // Seçilen değeri görelim
        
        if (selectedValue) {
            try {
                await loadTableFilters(selectedValue);
            } catch (error) {
                console.error('Filtreler yüklenirken hata:', error);
                showError('Filtreler yüklenirken bir hata oluştu');
            }
        } else {
            document.getElementById('filterContainer').innerHTML = '';
        }
    });
});

// Tabloları yükleme fonksiyonu
async function loadTables() {
    try {
        const response = await fetch('/api/tablolar');
        const tables = await response.json();
        console.log('Yüklenen tablolar:', tables); // Debug için
        
        const tableSelect = document.getElementById('tableSelect');
        tableSelect.innerHTML = '<option value="">Tablo Seçiniz</option>';
        
        tables.forEach(table => {
            const option = document.createElement('option');
            option.value = table.id;
            option.textContent = table.ad;
            tableSelect.appendChild(option);
        });
    } catch (error) {
        console.error('Tablolar yüklenirken hata:', error);
        showError('Tablolar yüklenirken bir hata oluştu');
    }
}

// Hata gösterme fonksiyonu
function showError(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-danger alert-dismissible fade show mt-3';
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Varsa eski hata mesajını kaldır
    const oldAlert = document.querySelector('.alert');
    if (oldAlert) {
        oldAlert.remove();
    }
    
    document.querySelector('.container').prepend(alertDiv);
}

// Filtreleri yükleme fonksiyonu
async function loadTableFilters(tableName) {
    try {
        console.log('loadTableFilters çağrıldı:', tableName);
        
        const filterContainer = document.getElementById('filterContainer');
        filterContainer.innerHTML = '';
        
        // Tablo kolonlarını al
        const kolonResponse = await fetch(`/api/${tableName}/kolonlar`);
        const kolonlar = await kolonResponse.json();
        
        if (!Array.isArray(kolonlar)) {
            throw new Error('Kolonlar alınamadı');
        }
        
        // Filtre container'ı oluştur
        const filterRow = document.createElement('div');
        filterRow.className = 'row g-3';
        
        // Her kolon için filtre oluştur
        for (const kolonAdi of kolonlar) {
            const col = document.createElement('div');
            col.className = 'col-md-3';
            
            const formGroup = document.createElement('div');
            formGroup.className = 'form-group';
            
            const label = document.createElement('label');
            label.className = 'form-label';
            label.textContent = kolonAdi.replace(/_/g, ' ').toUpperCase();
            
            const select = document.createElement('select');
            select.className = 'form-select';
            select.name = kolonAdi;
            
            // Varsayılan seçenek
            select.innerHTML = '<option value="">Seçiniz</option>';
            
            // Filtre değerlerini yükle
            try {
                const response = await fetch(`/api/${tableName}/unique-values/${kolonAdi}`);
                const values = await response.json();
                
                if (Array.isArray(values)) {
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
            col.appendChild(formGroup);
            filterRow.appendChild(col);
        }
        
        filterContainer.appendChild(filterRow);
        
    } catch (error) {
        console.error('Filtreler yüklenirken hata:', error);
        showError('Filtreler yüklenirken bir hata oluştu: ' + error.message);
    }
}

// Sorgu yapma fonksiyonu
async function performQuery() {
    showLoading();
    try {
        const tableName = document.getElementById('tableSelect').value;
        if (!tableName) {
            showError('Lütfen bir tablo seçiniz');
            return;
        }
        
        // Tüm select elementlerinden filtreleri topla
        const filters = {};
        const selects = document.querySelectorAll('#filterContainer select');
        selects.forEach(select => {
            if (select.value) {
                filters[select.name] = select.value;
            }
        });
        
        // Filtreleri query string'e dönüştür
        const queryString = new URLSearchParams(filters).toString();
        const response = await fetch(`/api/${tableName}/veriler?${queryString}`);
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || 'Bilinmeyen bir hata oluştu');
        }
        
        if (result.data && result.data.length > 0) {
            displayResults(result);
        } else {
            showError('Seçilen kriterlere uygun sonuç bulunamadı');
        }
        
    } catch (error) {
        console.error('Sorgu hatası:', error);
        showError('Sorgu yapılırken bir hata oluştu: ' + error.message);
    } finally {
        hideLoading();
        // Butonu tekrar aktif hale getir
        document.querySelector('button[type="submit"]').disabled = false;
    }
}

// Sonuçları görüntüleme fonksiyonu
function displayResults(data) {
    const resultsCard = document.getElementById('resultsCard');
    const table = document.getElementById('resultsTable');
    const thead = table.querySelector('thead');
    const tbody = table.querySelector('tbody');
    
    if (data.data && data.data.length > 0) {
        // Kişi sayısını en sona al
        const headers = Object.keys(data.data[0]).filter(h => h !== 'kisi_sayisi');
        headers.push('kisi_sayisi'); // Kişi sayısını en sona ekle
        
        thead.innerHTML = `
            <tr>
                ${headers.map(header => `<th>${header.replace(/_/g, ' ').toUpperCase()}</th>`).join('')}
            </tr>
        `;
        
        tbody.innerHTML = data.data.map(row => `
            <tr>
                ${headers.map(header => `
                    <td>${header === 'kisi_sayisi' ? 
                        `<strong>${row[header]}</strong>` : 
                        row[header]}</td>
                `).join('')}
            </tr>
        `).join('');
        
        resultsCard.style.display = 'block';
    } else {
        tbody.innerHTML = '<tr><td colspan="100%">Sonuç bulunamadı</td></tr>';
    }
}

function showLoading() {
    // ... loading göstergesi kodu ...
}

function hideLoading() {
    // ... loading göstergesi kodu ...
} 