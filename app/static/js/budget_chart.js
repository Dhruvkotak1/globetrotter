// GlobeTrotter - Budget Visualizations with Chart.js

function initBudgetCharts(tripId, categoryData, dailyData) {
    // 1. Category Breakdown Donut Chart
    const categoryCtx = document.getElementById('categoryPieChart');
    if (categoryCtx) {
        new Chart(categoryCtx, {
            type: 'doughnut',
            data: {
                labels: ['Transport', 'Stay/Hotel', 'Activities', 'Meals & Dining', 'Other Expenses'],
                datasets: [{
                    data: [
                        categoryData.transport || 0,
                        categoryData.stay || 0,
                        categoryData.activities || 0,
                        categoryData.meals || 0,
                        categoryData.other || 0
                    ],
                    backgroundColor: [
                        '#4f46e5', // Indigo
                        '#06b6d4', // Cyan
                        '#10b981', // Emerald
                        '#f59e0b', // Amber
                        '#8b5cf6'  // Purple
                    ],
                    borderWidth: 2,
                    borderColor: '#ffffff',
                    hoverOffset: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            font: { family: 'Plus Jakarta Sans', size: 12 },
                            padding: 16,
                            usePointStyle: true
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                let label = context.label || '';
                                let val = context.raw || 0;
                                return ` ${label}: $${Number(val).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                            }
                        }
                    }
                },
                cutout: '68%'
            }
        });
    }

    // 2. Daily Spend Bar Chart
    const dailyCtx = document.getElementById('dailySpendBarChart');
    if (dailyCtx) {
        new Chart(dailyCtx, {
            type: 'bar',
            data: {
                labels: dailyData.labels || [],
                datasets: [{
                    label: 'Daily Estimated Cost ($)',
                    data: dailyData.costs || [],
                    backgroundColor: 'rgba(79, 70, 229, 0.85)',
                    hoverBackgroundColor: '#4338ca',
                    borderRadius: 8,
                    borderSkipped: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: { color: '#f1f5f9' },
                        ticks: {
                            callback: function(value) {
                                return '$' + value;
                            },
                            font: { family: 'Plus Jakarta Sans' }
                        }
                    },
                    x: {
                        grid: { display: false },
                        ticks: { font: { family: 'Plus Jakarta Sans' } }
                    }
                },
                plugins: {
                    legend: { display: false },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                return ` Cost: $${Number(context.raw).toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
                            }
                        }
                    }
                }
            }
        });
    }
}
