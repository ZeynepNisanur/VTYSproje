document.addEventListener('DOMContentLoaded', function() {
    // Dashboard verilerini yükle
    loadDashboardData();
    
    // Grafikleri yükle
    loadCharts();

    // Sidebar toggle fonksiyonu
    const toggleButton = document.querySelector('.toggle-sidebar');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    toggleButton.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        mainContent.classList.toggle('expanded');
    });
});

async function loadDashboardData() {
    try {
        const response = await fetch('/api/dashboard/summary');
        const data = await response.json();
        
        // Özet kartlarını güncelle
        document.getElementById('totalPeople').textContent = data.total_people.toLocaleString();
        document.getElementById('totalCities').textContent = data.total_cities;
        document.getElementById('yearRange').textContent = `${data.min_year}-${data.max_year}`;
        document.getElementById('totalCategories').textContent = data.total_categories;
        
    } catch (error) {
        console.error('Dashboard verileri yüklenirken hata:', error);
    }
}

async function loadCharts() {
    try {
        // Yıllara göre suç dağılımı grafiği
        const yearlyData = await fetch('/api/dashboard/yearly-distribution').then(res => res.json());
        createYearlyChart(yearlyData);
        
        // İllere göre suç dağılımı grafiği
        const citiesData = await fetch('/api/dashboard/cities-distribution').then(res => res.json());
        createCitiesChart(citiesData);
        
        // Cinsiyet dağılımı grafiği
        const genderData = await fetch('/api/dashboard/gender-distribution').then(res => res.json());
        createGenderChart(genderData);
        
        // Eğitim durumu dağılımı grafiği
        const educationData = await fetch('/api/dashboard/education-distribution').then(res => res.json());
        createEducationChart(educationData);
        
    } catch (error) {
        console.error('Grafikler yüklenirken hata:', error);
    }
}

function createYearlyChart(data) {
    const ctx = document.getElementById('yearlyChart').getContext('2d');
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Suç Sayısı',
                data: data.values,
                borderColor: '#3949ab',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                    align: 'end'
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        maxTicksLimit: 5
                    }
                }
            }
        }
    });
}

function createCitiesChart(data) {
    const ctx = document.getElementById('citiesChart').getContext('2d');
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Suç Sayısı',
                data: data.values,
                backgroundColor: '#43a047'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        maxTicksLimit: 5
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
}

function createGenderChart(data) {
    const ctx = document.getElementById('genderChart').getContext('2d');
    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: ['#3949ab', '#e53935']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right'
                }
            }
        }
    });
}

function createEducationChart(data) {
    const ctx = document.getElementById('educationChart').getContext('2d');
    new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.values,
                backgroundColor: [
                    '#3949ab', '#43a047', '#fb8c00', 
                    '#e53935', '#8e24aa', '#0097a7'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        padding: 10
                    }
                }
            }
        }
    });
} 