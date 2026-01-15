// WESTINGEN Dashboard Auto-Refresh
let temperatureChart = null;

function formatTimestamp(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString();
}

function updateKPIs(stats, latest) {
    document.getElementById('total-records').textContent = stats.total_records || 0;
    
    if (latest && latest.readings && latest.readings.length > 0) {
        const temp = latest.readings[0].temperature_c.toFixed(1);
        document.getElementById('latest-temp').textContent = temp + ' °C';
        document.getElementById('last-update').textContent = formatTimestamp(latest.readings[0].created_at);
    } else {
        document.getElementById('latest-temp').textContent = '-';
        document.getElementById('last-update').textContent = '-';
    }
}

function updateChart(readings) {
    if (!readings || readings.length === 0) return;
    
    const sorted = [...readings].sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
    const labels = sorted.map(r => {
        const date = new Date(r.created_at);
        return date.toLocaleTimeString();
    });
    const temps = sorted.map(r => r.temperature_c);
    
    const ctx = document.getElementById('temperatureChart').getContext('2d');
    
    if (temperatureChart) {
        temperatureChart.destroy();
    }
    
    temperatureChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Temperature (°C)',
                data: temps,
                borderColor: 'rgb(44, 62, 80)',
                backgroundColor: 'rgba(44, 62, 80, 0.1)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: false
                }
            }
        }
    });
}

function updateTable(readings) {
    const tbody = document.getElementById('readings-table');
    
    if (!readings || readings.length === 0) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center">No data available</td></tr>';
        return;
    }
    
    tbody.innerHTML = readings.map(r => `
        <tr>
            <td>${formatTimestamp(r.created_at)}</td>
            <td>${r.device_id}</td>
            <td>${r.temperature_c.toFixed(2)}</td>
            <td>${r.accel_x.toFixed(3)}</td>
            <td>${r.accel_y.toFixed(3)}</td>
            <td>${r.accel_z.toFixed(3)}</td>
            <td>${r.latitude.toFixed(4)}</td>
            <td>${r.longitude.toFixed(4)}</td>
        </tr>
    `).join('');
}

async function fetchData() {
    try {
        const [statsRes, latestRes] = await Promise.all([
            fetch('/api/stats'),
            fetch('/api/latest?limit=50')
        ]);
        
        const stats = await statsRes.json();
        const latest = await latestRes.json();
        
        updateKPIs(stats, latest);
        updateChart(latest.readings || []);
        updateTable(latest.readings || []);
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Initial load
fetchData();

// Auto-refresh every 5 seconds
setInterval(fetchData, 5000);
