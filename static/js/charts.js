document.addEventListener('DOMContentLoaded', function() {
    const statsCtx = document.getElementById('statsChart').getContext('2d');
    const historyCtx = document.getElementById('historyChart').getContext('2d');
    const categoryCtx = document.getElementById('categoryChart').getContext('2d');

    const barColors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40', '#C9CBCF'];
    const lineColors = ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0'];

    fetch('/api/stats')
        .then(response => response.json())
        .then(data => {
            createStatsChart(data);
            createHistoryChart(data);
            createCategoryChart(data);
        })
        .catch(error => {
            console.error('Error loading chart data:', error);
            document.querySelectorAll('.chart-container').forEach(container => {
                container.innerHTML = '<p class="error">Unable to load chart data</p>';
            });
        });

    function createStatsChart(data) {
        new Chart(statsCtx, {
            type: 'bar',
            data: {
                labels: data.categories || [],
                datasets: [{
                    label: 'Files per Category',
                    data: data.category_counts || [],
                    backgroundColor: barColors,
                    borderColor: barColors.map(color => color.replace('0.8', '1')),
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }

    function createHistoryChart(data) {
        const history = data.history || [];
        const dates = history.map(item => item.date);
        const counts = history.map(item => item.count);

        new Chart(historyCtx, {
            type: 'line',
            data: {
                labels: dates,
                datasets: [{
                    label: 'Files Organized',
                    data: counts,
                    borderColor: lineColors[0],
                    backgroundColor: lineColors[0].replace(')', ', 0.1)'),
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }

    function createCategoryChart(data) {
        const pieData = data.category_counts || [];
        new Chart(categoryCtx, {
            type: 'doughnut',
            data: {
                labels: data.categories || [],
                datasets: [{
                    data: pieData,
                    backgroundColor: barColors,
                    borderColor: '#ffffff',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'right'
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const value = context.raw;
                                const percentage = Math.round((value / total) * 100);
                                return `${context.label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    window.refreshCharts = function() {
        fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                Chart.getChart(statsCtx).destroy();
                Chart.getChart(historyCtx).destroy();
                Chart.getChart(categoryCtx).destroy();
                createStatsChart(data);
                createHistoryChart(data);
                createCategoryChart(data);
            })
            .catch(error => {
                console.error('Error refreshing charts:', error);
            });
    };

    setInterval(window.refreshCharts, 30000);
});