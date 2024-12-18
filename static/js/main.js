document.addEventListener('DOMContentLoaded', function() {
    // Gerekli elementleri seç
    const tableSelect = document.getElementById('tableSelect');
    const showFiltersBtn = document.getElementById('showFilters');
    const filterSection = document.getElementById('filterSection');
    
    // Select2'yi initialize et
    $(tableSelect).select2({
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
    
    // Tablo seçimi değiştiğinde
    $(tableSelect).on('change', function() {
        const selectedValue = this.value;
        console.log('Seçilen tablo:', selectedValue);
        
        // Filtre butonunu aktifleştir/deaktifleştir
        showFiltersBtn.disabled = !selectedValue;
        
        // Eğer seçim kaldırıldıysa filtreleri gizle
        if (!selectedValue) {
            filterSection.style.display = 'none';
            document.getElementById('filterContainer').innerHTML = '';
        }
    });
    
    // Filtreleri göster butonu tıklandığında
    showFiltersBtn.addEventListener('click', async function() {
        const selectedTable = tableSelect.value;
        
        if (selectedTable) {
            try {
                // Filtreleri yükle
                await loadTableFilters(selectedTable);
                
                // Filtre bölümünü göster
                filterSection.style.display = 'block';
                
                // Smooth scroll to filters
                filterSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } catch (error) {
                console.error('Filtreler yüklenirken hata:', error);
                showError('Filtreler yüklenirken bir hata oluştu');
            }
        }
    });
    
    // Form submit olayını dinle
    document.getElementById('queryForm').addEventListener('submit', function(e) {
        e.preventDefault();
        performQuery();
    });

    // Excel dışa aktarma butonu
    document.getElementById('exportExcel').addEventListener('click', exportToExcel);
    
    // PDF dışa aktarma butonu
    document.getElementById('exportPDF').addEventListener('click', exportToPDF);
    
    // Grafik gösterme butonu için event listener
    document.getElementById('showChart').addEventListener('click', showChartModal);
    
    // Grafik tipi değiştiğinde
    document.getElementById('chartType').addEventListener('change', function() {
        updateChart(this.value);
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
        
        // Sonuçlar kartını gizle
        document.getElementById('resultsCard').style.display = 'none';
        
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

    // Sidebar toggle fonksiyonu
    const toggleButton = document.querySelector('.toggle-sidebar');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    toggleButton.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('expanded');
    });
});

let currentChart = null; // Global chart değişkeni

function showChartModal() {
    const table = document.getElementById('resultsTable');
    if (!table) {
        showError('Görselleştirilecek veri bulunamadı');
        return;
    }

    // Modal'ı göster
    const chartModal = new bootstrap.Modal(document.getElementById('chartModal'));
    chartModal.show();

    // İlk grafik tipini çiz
    updateChart('bar');
}

function updateChart(chartType) {
    console.log('Grafik güncelleme başladı. Tip:', chartType);
    
    // Eski grafik varsa temizle
    if (currentChart) {
        console.log('Eski grafik temizleniyor');
        currentChart.destroy();
    }

    const table = document.getElementById('resultsTable');
    console.log('Tablo elementi:', table);
    
    const data = getDataFromTable(table);
    console.log('Grafik için hazırlanan veri:', data);

    const ctx = document.getElementById('dataChart').getContext('2d');
    
    const chartConfig = {
        type: chartType,
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Kişi Sayısı',
                data: data.values,
                backgroundColor: generateColors(data.values.length),
                borderColor: chartType === 'line' ? '#3949ab' : generateColors(data.values.length),
                borderWidth: chartType === 'line' ? 2 : 1,
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: chartType === 'pie' ? 'right' : 'top',
                },
                title: {
                    display: true,
                    text: 'Yıllara Göre Kişi Sayısı Dağılımı'
                }
            },
            scales: chartType !== 'pie' ? {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Kişi Sayısı'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Yıl'
                    }
                }
            } : {}
        }
    };
    
    console.log('Grafik konfigürasyonu:', chartConfig);
    currentChart = new Chart(ctx, chartConfig);
}

function getDataFromTable(table) {
    // Debug logları ekleyelim
    console.log('Tablo içeriği:', table);
    
    const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent);
    console.log('Bulunan başlıklar:', headers);
    
    const rows = Array.from(table.querySelectorAll('tbody tr'));
    console.log('Bulunan satırlar:', rows);
    
    // Yıl sütununun indeksini bul
    const yilIndex = headers.findIndex(header => 
        header.toLowerCase().includes('yil') || 
        header.toLowerCase().includes('yıl')
    );
    console.log('Yıl sütunu indeksi:', yilIndex);
    
    // Kişi sayısı sütununun indeksini bul (farklı formatları kontrol et)
    const kisiSayisiIndex = headers.findIndex(header => 
        header.toLowerCase().includes('kisi_sayisi') ||
        header.toLowerCase().includes('kişi sayısı') ||
        header.toLowerCase().includes('kisı_sayisi') ||
        header.toLowerCase().includes('kisi sayisi')
    );
    console.log('Kişi sayısı sütunu indeksi:', kisiSayisiIndex);
    
    // Eğer kişi sayısı sütunu bulunamadıysa son sütunu kullan
    const effectiveKisiSayisiIndex = kisiSayisiIndex === -1 ? headers.length - 1 : kisiSayisiIndex;
    console.log('Kullanılan kişi sayısı sütunu indeksi:', effectiveKisiSayisiIndex);
    
    // Eğer yıl sütunu bulunamazsa
    if (yilIndex === -1) {
        console.error('Yıl sütunu bulunamadı');
        return { labels: [], values: [] };
    }

    // Yıllara göre kişi sayılarını topla
    const yilData = rows.reduce((acc, row) => {
        const yil = row.cells[yilIndex].textContent.trim();
        const kisiSayisi = parseInt(row.cells[effectiveKisiSayisiIndex].textContent.trim());
        
        console.log(`İşlenen veri - Yıl: ${yil}, Kişi Sayısı: ${kisiSayisi}`);
        
        if (!acc[yil]) {
            acc[yil] = 0;
        }
        acc[yil] += kisiSayisi;
        return acc;
    }, {});
    
    console.log('Toplanan yıl verileri:', yilData);

    // Yıllara göre sırala
    const sortedYears = Object.keys(yilData).sort();
    const result = {
        labels: sortedYears,
        values: sortedYears.map(yil => yilData[yil])
    };
    
    console.log('Grafik için hazırlanan veri:', result);
    return result;
}

function generateColors(count) {
    const colors = [
        '#3949ab', '#43a047', '#fb8c00', '#e53935', '#8e24aa', 
        '#0097a7', '#689f38', '#f4511e', '#6d4c41', '#1e88e5'
    ];
    
    // Renk sayısı yetmezse döngüsel olarak kullan
    return Array(count).fill().map((_, i) => colors[i % colors.length]);
}

// Tabloları yükleme fonksiyonu
async function loadTables() {
    try {
        const response = await fetch('/api/tablolar');
        const tables = await response.json();
        console.log('Yüklenen tablolar:', tables);
        
        const tableSelect = document.getElementById('tableSelect');
        tableSelect.innerHTML = '<option value="">Tablo Seçiniz</option>';
        
        tables.forEach(table => {
            const option = document.createElement('option');
            option.value = table.id;
            option.textContent = table.ad;
            tableSelect.appendChild(option);
        });

        // Select2'yi güncelle
        $(tableSelect).trigger('change');
        
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

// Filtreleri yükleme fonksiyonu güncellendi
async function loadTableFilters(tableName) {
    try {
        const filterContainer = document.getElementById('filterContainer');
        filterContainer.innerHTML = '';
        
        // Tablo kolonlarını al
        const kolonResponse = await fetch(`/api/${tableName}/kolonlar`);
        const kolonlar = await kolonResponse.json();
        
        console.log('Alınan kolonlar:', kolonlar);
        
        // Her kolon için filtre oluştur
        for (const kolonAdi of kolonlar) {
            const formGroup = document.createElement('div');
            formGroup.className = 'form-group';
            
            const label = document.createElement('label');
            label.className = 'form-label';
            label.textContent = kolonAdi;
            
            const select = document.createElement('select');
            select.className = 'form-select';
            
            // Kolon adını API için hazırla
            let columnName;
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

            columnName = columnMappings[kolonAdi] || kolonAdi
                .toLowerCase()
                .normalize("NFD")
                .replace(/[\u0300-\u036f]/g, "")
                .replace(/\s+/g, '_');

            console.log(`Kolon adı dönüşümü: ${kolonAdi} -> ${columnName}`);
            
            select.name = columnName;
            select.id = `filter_${columnName}`;
            select.innerHTML = '<option value="">Tümü</option>';
            
            console.log(`${kolonAdi} için API çağrısı:`, `/api/${tableName}/unique-values/${columnName}`);
            
            try {
                const response = await fetch(`/api/${tableName}/unique-values/${columnName}`);
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                const values = await response.json();
                console.log(`${kolonAdi} için değerler:`, values);
                
                if (Array.isArray(values)) {
                    // Sayısal değerler için özel sıralama
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
            
            // Her select için Select2'yi initialize et
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

// Sorgu yapma fonksiyonu
async function performQuery() {
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
        console.log('Filtreler:', filters);  // Debug için
        
        const response = await fetch(`/api/${tableName}/veriler?${queryString}`);
        const result = await response.json();
        
        if (!result.success) {
            throw new Error(result.error || 'Bilinmeyen bir hata oluştu');
        }
        
        if (result.data && result.data.length > 0) {
            displayResults(result);
            document.getElementById('resultsCard').style.display = 'block';
        } else {
            showError('Seçilen kriterlere uygun sonuç bulunamadı');
        }
        
    } catch (error) {
        console.error('Sorgu hatası:', error);
        showError('Sorgu yapılırken bir hata oluştu: ' + error.message);
    }
}

// Sonuçları görüntüleme fonksiyonu
function displayResults(data) {
    const resultsCard = document.getElementById('resultsCard');
    const table = document.getElementById('resultsTable');
    const thead = table.querySelector('thead');
    const tbody = table.querySelector('tbody');
    
    if (data.data && data.data.length > 0) {
        // Sonuç sayısını göster
        showSuccess(`${data.data.length} adet sonuç bulundu`);
        
        // Kişi sayısını en sona al
        const headers = Object.keys(data.data[0]).filter(h => h !== 'kisi_sayisi');
        headers.push('kisi_sayisi');
        
        // Başlık dönüşüm haritası
        const headerMappings = {
            'id': 'ID',
            'suc_turu': 'SUÇ TÜRÜ',
            'suc_turu_id': 'SUÇ TÜRÜ ID',
            'ceza_turu': 'CEZA TÜRÜ',
            'ceza_turu_id': 'CEZA TÜRÜ ID',
            'cinsiyet': 'CİNSİYET',
            'yil': 'YIL',
            'il': 'İL',
            'il_id': 'İL ID',
            'yas': 'YAŞ',
            'egitim_durumu': 'EĞİTİM DURUMU',
            'egitim_durumu_id': 'EĞİTİM DURUMU ID',
            'is_durumu': 'İŞ DURUMU',
            'is_durumu_id': 'İŞ DURUMU ID',
            'medeni_durum': 'MEDENİ DURUM',
            'medeni_durum_id': 'MEDENİ DURUM ID',
            'infaza_davet_sekli': 'İNFAZA DAVET ŞEKLİ',
            'infaza_davet_id': 'İNFAZA DAVET ID',
            'yerlesim_yeri': 'YERLEŞİM YERİ',
            'yerlesim_yeri_id': 'YERLEŞİM YERİ ID',
            'yerlesim_yeri_ulke': 'YERLEŞİM YERİ (ÜLKE)',
            'uyruk': 'UYRUK',
            'kisi_sayisi': 'KİŞİ SAYISI'
        };
        
        thead.innerHTML = `
            <tr>
                ${headers.map(header => `<th>${headerMappings[header] || header.toUpperCase()}</th>`).join('')}
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
        showError('Seçilen kriterlere uygun sonuç bulunamadı');
    }
}

function showLoading() {
    // ... loading göstergesi kodu ...
}

function hideLoading() {
    // ... loading göstergesi kodu ...
}

// Başarı mesajı gösterme fonksiyonu
function showSuccess(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show mt-3';
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Varsa eski alert'i kaldır
    const oldAlert = document.querySelector('.alert');
    if (oldAlert) {
        oldAlert.remove();
    }
    
    // Alert'i sayfaya ekle
    document.querySelector('.content-wrapper').insertBefore(alertDiv, document.getElementById('resultsCard'));
}

// Excel'e aktarma fonksiyonu
function exportToExcel() {
    try {
        const table = document.getElementById('resultsTable');
        if (!table) {
            showError('Dışa aktarılacak veri bulunamadı');
            return;
        }

        // Başlıkları al
        const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent);
        
        // Verileri al
        const rows = Array.from(table.querySelectorAll('tbody tr')).map(row => {
            return Array.from(row.querySelectorAll('td')).map(cell => cell.textContent.trim());
        });

        // Workbook oluştur
        const worksheet = XLSX.utils.aoa_to_sheet([headers, ...rows]);
        const workbook = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(workbook, worksheet, "Veriler");

        // Dosyayı indir
        const date = new Date().toISOString().slice(0,10);
        XLSX.writeFile(workbook, `suc_analiz_${date}.xlsx`);
        
        showSuccess('Veriler Excel dosyasına aktarıldı');
    } catch (error) {
        console.error('Excel dışa aktarma hatası:', error);
        showError('Excel dışa aktarma işlemi başarısız oldu');
    }
}

// PDF'e aktarma fonksiyonu
function exportToPDF() {
    try {
        const table = document.getElementById('resultsTable');
        if (!table) {
            showError('Dışa aktarılacak veri bulunamadı');
            return;
        }

        // Başlıkları al ve Türkçe karakterleri düzelt
        const headers = Array.from(table.querySelectorAll('thead th')).map(th => {
            return th.textContent
                .replace('KISI_SAYISI', 'KİŞİ SAYISI')
                .replace('YIL', 'YIL')
                .replace('IL', 'İL')
                .replace('_', ' ');
        });
        
        // Verileri al
        const rows = Array.from(table.querySelectorAll('tbody tr')).map(row => {
            return Array.from(row.querySelectorAll('td')).map(cell => cell.textContent.trim());
        });

        // PDF oluştur
        const doc = new jspdf.jsPDF('l', 'pt'); // Yatay (landscape) format
        
        // Başlık ekle
        doc.setFontSize(16);
        doc.text('Suç Analiz Raporu', 40, 40);
        
        // Tarih ekle
        doc.setFontSize(10);
        doc.text(`Oluşturulma Tarihi: ${new Date().toLocaleDateString('tr-TR')}`, 40, 60);

        // Tabloyu ekle
        doc.autoTable({
            head: [headers],
            body: rows,
            startY: 70,
            theme: 'grid',
            styles: {
                fontSize: 8,
                cellPadding: 2,
                overflow: 'linebreak',
                halign: 'center',
                font: 'helvetica'
            },
            headStyles: {
                fillColor: [57, 73, 171],
                textColor: 255,
                fontSize: 8,
                fontStyle: 'bold',
                halign: 'center'
            },
            alternateRowStyles: {
                fillColor: [245, 245, 245]
            },
            margin: { top: 70, right: 30, bottom: 30, left: 30 },
            didDrawPage: function(data) {
                // Sayfa numarası ekle
                doc.setFontSize(8);
                doc.text(
                    'Sayfa ' + data.pageNumber,
                    data.settings.margin.left,
                    doc.internal.pageSize.height - 20
                );
            }
        });

        // Dosyayı indir
        const date = new Date().toISOString().slice(0,10);
        doc.save(`suc_analiz_${date}.pdf`);
        
        showSuccess('Veriler PDF dosyasına aktarıldı');
    } catch (error) {
        console.error('PDF dışa aktarma hatası:', error);
        showError('PDF dışa aktarma işlemi başarısız oldu');
    }
}

// Select2 inicializasyonu
$(document).ready(function() {
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
});

// Filtre select'leri için select2
function initializeFilterSelects() {
    $('.form-select').select2({
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