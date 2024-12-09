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
    
    // Sıfırlama butonu için event listener ekle
    document.getElementById('resetFilters').addEventListener('click', function() {
        // Tablo seçimini sıfırla
        const tableSelect = document.getElementById('tableSelect');
        tableSelect.value = '';
        
        // Select2'yi güncelle
        if ($(tableSelect).data('select2')) {
            $(tableSelect).val('').trigger('change');
        }
        
        // Filtre container'ı temizle
        document.getElementById('filterContainer').innerHTML = '';
        
        // Sonuçlar kartını gizle
        document.getElementById('resultsCard').style.display = 'none';
        
        // Başarı mesajını göster
        showSuccess('Filtreler başarıyla sıfırlandı');
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

// Başarı mesajı gösterme fonksiyonu
function showSuccess(message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = 'alert alert-success alert-dismissible fade show mt-3';
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        <i class="bi bi-check-circle-fill me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Varsa eski alert'i kaldır
    const oldAlert = document.querySelector('.alert');
    if (oldAlert) {
        oldAlert.remove();
    }
    
    // Yeni alert'i ekle
    document.querySelector('.filter-card').insertAdjacentElement('afterend', alertDiv);
    
    // 3 saniye sonra alert'i otomatik kaldır
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
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

        // Başlıkları al
        const headers = Array.from(table.querySelectorAll('thead th')).map(th => th.textContent);
        
        // Verileri al
        const rows = Array.from(table.querySelectorAll('tbody tr')).map(row => {
            return Array.from(row.querySelectorAll('td')).map(cell => cell.textContent.trim());
        });

        // PDF oluştur
        const doc = new jspdf.jsPDF();
        
        // Başlık ekle
        doc.setFontSize(16);
        doc.text('Suç Analiz Raporu', 14, 15);
        doc.setFontSize(10);
        doc.text(`Oluşturulma Tarihi: ${new Date().toLocaleDateString('tr-TR')}`, 14, 22);

        // Tabloyu ekle
        doc.autoTable({
            head: [headers],
            body: rows,
            startY: 30,
            theme: 'grid',
            styles: {
                fontSize: 8,
                cellPadding: 2,
                overflow: 'linebreak',
                halign: 'center'
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