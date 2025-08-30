/**
 * Interactive Data Visualization System
 * Umoor Sehhat Healthcare Management
 * Using Chart.js and custom visualizations
 */

// ============================================
// CHART CONFIGURATION
// ============================================

// Load Chart.js if not already loaded
if (!window.Chart) {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js';
    script.onload = () => {
        console.log('Chart.js loaded successfully');
        if (window.chartManager) {
            window.chartManager.init();
        }
    };
    document.head.appendChild(script);
}

// ============================================
// CHART MANAGER
// ============================================

class ChartManager {
    constructor() {
        this.charts = new Map();
        this.colors = {
            primary: '#2563eb',
            secondary: '#64748b',
            success: '#10b981',
            warning: '#f59e0b',
            error: '#ef4444',
            info: '#06b6d4',
            purple: '#8b5cf6',
            pink: '#ec4899',
            indigo: '#6366f1',
            teal: '#14b8a6'
        };
        this.gradients = {};
        this.defaultOptions = this.getDefaultOptions();
    }

    init() {
        if (typeof Chart !== 'undefined') {
            this.setupChartDefaults();
            this.createGradients();
            this.initializeCharts();
        }
    }

    setupChartDefaults() {
        try {
            if (typeof Chart === 'undefined') {
                console.warn('Chart.js not available');
                return;
            }
            
            Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
            Chart.defaults.font.size = 12;
            Chart.defaults.color = '#64748b';
            Chart.defaults.borderColor = '#e2e8f0';
            Chart.defaults.backgroundColor = 'rgba(37, 99, 235, 0.1)';
            
            // Register plugins (check if registerables exists first)
            try {
                if (Chart.registerables && Array.isArray(Chart.registerables) && Chart.registerables.length > 0) {
                    Chart.register(...Chart.registerables);
                } else if (Chart.defaults) {
                    // Chart.js is loaded but registerables not available - likely newer version
                    // Most components are auto-registered in newer versions
                    console.log('Chart.js components auto-registered');
                }
            } catch (error) {
                console.warn('Chart.js registration failed:', error);
            }
        } catch (error) {
            console.error('Chart.js setup failed:', error);
        }
    }

    createGradients() {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        
        // Primary gradient
        this.gradients.primary = ctx.createLinearGradient(0, 0, 0, 400);
        this.gradients.primary.addColorStop(0, 'rgba(37, 99, 235, 0.8)');
        this.gradients.primary.addColorStop(1, 'rgba(37, 99, 235, 0.1)');
        
        // Success gradient
        this.gradients.success = ctx.createLinearGradient(0, 0, 0, 400);
        this.gradients.success.addColorStop(0, 'rgba(16, 185, 129, 0.8)');
        this.gradients.success.addColorStop(1, 'rgba(16, 185, 129, 0.1)');
        
        // Warning gradient
        this.gradients.warning = ctx.createLinearGradient(0, 0, 0, 400);
        this.gradients.warning.addColorStop(0, 'rgba(245, 158, 11, 0.8)');
        this.gradients.warning.addColorStop(1, 'rgba(245, 158, 11, 0.1)');
    }

    getDefaultOptions() {
        return {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                intersect: false,
                mode: 'index'
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top',
                    labels: {
                        usePointStyle: true,
                        padding: 20,
                        font: {
                            size: 12,
                            weight: '500'
                        }
                    }
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#374151',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: true,
                    titleFont: {
                        size: 14,
                        weight: '600'
                    },
                    bodyFont: {
                        size: 12
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                },
                y: {
                    grid: {
                        color: '#f1f5f9',
                        drawBorder: false
                    },
                    ticks: {
                        font: {
                            size: 11
                        }
                    }
                }
            }
        };
    }

    initializeCharts() {
        // Auto-initialize charts with data attributes
        document.querySelectorAll('[data-chart]').forEach(element => {
            const chartType = element.dataset.chart;
            const chartData = element.dataset.chartData;
            
            if (chartData) {
                try {
                    const data = JSON.parse(chartData);
                    this.createChart(element, chartType, data);
                } catch (error) {
                    console.error('Error parsing chart data:', error);
                }
            }
        });
    }

    createChart(element, type, data, options = {}) {
        const ctx = element.getContext('2d');
        const chartId = element.id || `chart-${Date.now()}`;
        
        // Merge options with defaults
        const mergedOptions = this.mergeDeep(this.defaultOptions, options);
        
        // Create chart based on type
        let chartConfig;
        
        switch (type) {
            case 'line':
                chartConfig = this.createLineChart(data, mergedOptions);
                break;
            case 'bar':
                chartConfig = this.createBarChart(data, mergedOptions);
                break;
            case 'doughnut':
                chartConfig = this.createDoughnutChart(data, mergedOptions);
                break;
            case 'pie':
                chartConfig = this.createPieChart(data, mergedOptions);
                break;
            case 'area':
                chartConfig = this.createAreaChart(data, mergedOptions);
                break;
            default:
                console.error(`Unknown chart type: ${type}`);
                return null;
        }
        
        const chart = new Chart(ctx, chartConfig);
        this.charts.set(chartId, chart);
        
        return chart;
    }

    createLineChart(data, options) {
        return {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: data.datasets.map((dataset, index) => ({
                    label: dataset.label,
                    data: dataset.data,
                    borderColor: dataset.borderColor || this.getColor(index),
                    backgroundColor: dataset.backgroundColor || this.getColor(index, 0.1),
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4,
                    pointBackgroundColor: dataset.borderColor || this.getColor(index),
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }))
            },
            options: options
        };
    }

    createBarChart(data, options) {
        return {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: data.datasets.map((dataset, index) => ({
                    label: dataset.label,
                    data: dataset.data,
                    backgroundColor: dataset.backgroundColor || this.getColor(index, 0.8),
                    borderColor: dataset.borderColor || this.getColor(index),
                    borderWidth: 1,
                    borderRadius: 4,
                    borderSkipped: false
                }))
            },
            options: {
                ...options,
                scales: {
                    ...options.scales,
                    x: {
                        ...options.scales.x,
                        grid: {
                            display: false
                        }
                    },
                    y: {
                        ...options.scales.y,
                        beginAtZero: true
                    }
                }
            }
        };
    }

    createAreaChart(data, options) {
        return {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: data.datasets.map((dataset, index) => ({
                    label: dataset.label,
                    data: dataset.data,
                    borderColor: dataset.borderColor || this.getColor(index),
                    backgroundColor: this.gradients[Object.keys(this.gradients)[index]] || this.getColor(index, 0.3),
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4,
                    pointBackgroundColor: dataset.borderColor || this.getColor(index),
                    pointBorderColor: '#ffffff',
                    pointBorderWidth: 2,
                    pointRadius: 0,
                    pointHoverRadius: 6
                }))
            },
            options: options
        };
    }

    createDoughnutChart(data, options) {
        return {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data,
                    backgroundColor: data.backgroundColor || data.labels.map((_, index) => this.getColor(index, 0.8)),
                    borderColor: data.borderColor || data.labels.map((_, index) => this.getColor(index)),
                    borderWidth: 2,
                    hoverOffset: 4
                }]
            },
            options: {
                ...options,
                cutout: '70%',
                plugins: {
                    ...options.plugins,
                    legend: {
                        ...options.plugins.legend,
                        position: 'right'
                    }
                }
            }
        };
    }

    createPieChart(data, options) {
        return {
            type: 'pie',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data,
                    backgroundColor: data.backgroundColor || data.labels.map((_, index) => this.getColor(index, 0.8)),
                    borderColor: data.borderColor || data.labels.map((_, index) => this.getColor(index)),
                    borderWidth: 2,
                    hoverOffset: 4
                }]
            },
            options: {
                ...options,
                plugins: {
                    ...options.plugins,
                    legend: {
                        ...options.plugins.legend,
                        position: 'right'
                    }
                }
            }
        };
    }

    getColor(index, alpha = 1) {
        const colorKeys = Object.keys(this.colors);
        const colorKey = colorKeys[index % colorKeys.length];
        const color = this.colors[colorKey];
        
        if (alpha === 1) {
            return color;
        } else {
            // Convert hex to rgba
            const hex = color.replace('#', '');
            const r = parseInt(hex.substr(0, 2), 16);
            const g = parseInt(hex.substr(2, 2), 16);
            const b = parseInt(hex.substr(4, 2), 16);
            return `rgba(${r}, ${g}, ${b}, ${alpha})`;
        }
    }

    // Utility method to deep merge objects
    mergeDeep(target, source) {
        const output = Object.assign({}, target);
        if (this.isObject(target) && this.isObject(source)) {
            Object.keys(source).forEach(key => {
                if (this.isObject(source[key])) {
                    if (!(key in target))
                        Object.assign(output, { [key]: source[key] });
                    else
                        output[key] = this.mergeDeep(target[key], source[key]);
                } else {
                    Object.assign(output, { [key]: source[key] });
                }
            });
        }
        return output;
    }

    isObject(item) {
        return item && typeof item === 'object' && !Array.isArray(item);
    }

    // Public methods for dynamic chart updates
    updateChart(chartId, newData) {
        const chart = this.charts.get(chartId);
        if (chart) {
            chart.data = newData;
            chart.update();
        }
    }

    destroyChart(chartId) {
        const chart = this.charts.get(chartId);
        if (chart) {
            chart.destroy();
            this.charts.delete(chartId);
        }
    }

    // Create specific healthcare charts
    createPatientStatsChart(element, data) {
        return this.createChart(element, 'bar', {
            labels: data.months || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'New Patients',
                data: data.newPatients || [12, 19, 3, 5, 2, 3],
                backgroundColor: this.colors.primary
            }, {
                label: 'Follow-up Visits',
                data: data.followUps || [2, 3, 20, 5, 1, 4],
                backgroundColor: this.colors.success
            }]
        });
    }

    createAppointmentTrendsChart(element, data) {
        return this.createChart(element, 'area', {
            labels: data.days || ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
            datasets: [{
                label: 'Appointments',
                data: data.appointments || [65, 59, 80, 81, 56, 55, 40],
                borderColor: this.colors.primary,
                backgroundColor: this.gradients.primary
            }]
        });
    }

    createMozeUtilizationChart(element, data) {
        return this.createChart(element, 'doughnut', {
            labels: data.centers || ['Al-Noor', 'As-Salam', 'Ar-Rahman'],
            data: data.utilization || [85, 65, 45]
        });
    }

    createHealthMetricsChart(element, data) {
        return this.createChart(element, 'line', {
            labels: data.months || ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Patient Satisfaction',
                data: data.satisfaction || [4.2, 4.5, 4.3, 4.7, 4.6, 4.8],
                borderColor: this.colors.success,
                backgroundColor: this.colors.success
            }, {
                label: 'Response Time (hrs)',
                data: data.responseTime || [2.1, 1.8, 2.3, 1.5, 1.7, 1.2],
                borderColor: this.colors.warning,
                backgroundColor: this.colors.warning,
                yAxisID: 'y1'
            }]
        }, {
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    min: 0,
                    max: 5,
                    title: {
                        display: true,
                        text: 'Satisfaction (1-5)'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    min: 0,
                    max: 5,
                    title: {
                        display: true,
                        text: 'Response Time (hours)'
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                }
            }
        });
    }
}

// ============================================
// DASHBOARD WIDGETS
// ============================================

class DashboardWidgets {
    constructor() {
        this.widgets = new Map();
    }

    createStatsWidget(element, data) {
        const widget = document.createElement('div');
        widget.className = 'stats-widget';
        widget.innerHTML = `
            <div class="stats-widget-header">
                <h3>${data.title}</h3>
                <div class="stats-widget-actions">
                    <button class="btn btn-sm btn-outline-secondary" onclick="this.closest('.stats-widget').classList.toggle('expanded')">
                        <i class="fas fa-expand-alt"></i>
                    </button>
                </div>
            </div>
            <div class="stats-widget-body">
                <div class="row">
                    ${data.stats.map(stat => `
                        <div class="col-md-6 mb-3">
                            <div class="stat-item">
                                <div class="stat-icon ${stat.type}">
                                    <i class="${stat.icon}"></i>
                                </div>
                                <div class="stat-content">
                                    <div class="stat-number">${stat.value}</div>
                                    <div class="stat-label">${stat.label}</div>
                                    ${stat.change ? `
                                        <div class="stat-change ${stat.change > 0 ? 'positive' : 'negative'}">
                                            <i class="fas fa-arrow-${stat.change > 0 ? 'up' : 'down'}"></i>
                                            ${Math.abs(stat.change)}%
                                        </div>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        element.appendChild(widget);
        this.widgets.set(element.id, widget);
        return widget;
    }

    createProgressWidget(element, data) {
        const widget = document.createElement('div');
        widget.className = 'progress-widget';
        widget.innerHTML = `
            <div class="progress-widget-header">
                <h4>${data.title}</h4>
                <span class="progress-percentage">${data.percentage}%</span>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: ${data.percentage}%"></div>
            </div>
            <div class="progress-details">
                <small class="text-muted">${data.description}</small>
            </div>
        `;

        element.appendChild(widget);
        return widget;
    }

    createTimelineWidget(element, data) {
        const widget = document.createElement('div');
        widget.className = 'timeline-widget';
        widget.innerHTML = `
            <div class="timeline-widget-header">
                <h4>${data.title}</h4>
            </div>
            <div class="timeline-widget-body">
                <div class="timeline">
                    ${data.events.map(event => `
                        <div class="timeline-item">
                            <div class="timeline-marker ${event.type}"></div>
                            <div class="timeline-content">
                                <div class="timeline-time">${event.time}</div>
                                <div class="timeline-title">${event.title}</div>
                                <div class="timeline-description">${event.description}</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;

        element.appendChild(widget);
        return widget;
    }
}

// ============================================
// REAL-TIME DATA UPDATES
// ============================================

class RealTimeUpdates {
    constructor() {
        this.updateInterval = 30000; // 30 seconds
        this.subscriptions = new Map();
    }

    subscribe(chartId, updateFunction) {
        this.subscriptions.set(chartId, updateFunction);
    }

    unsubscribe(chartId) {
        this.subscriptions.delete(chartId);
    }

    startUpdates() {
        setInterval(() => {
            this.subscriptions.forEach((updateFn, chartId) => {
                try {
                    updateFn();
                } catch (error) {
                    console.error(`Error updating chart ${chartId}:`, error);
                }
            });
        }, this.updateInterval);
    }

    // Simulate real-time data updates
    simulateDataUpdate(chartId) {
        const chart = window.chartManager.charts.get(chartId);
        if (chart) {
            // Add random data point
            const newValue = Math.floor(Math.random() * 100);
            const newLabel = new Date().toLocaleTimeString();
            
            chart.data.labels.push(newLabel);
            chart.data.datasets.forEach(dataset => {
                dataset.data.push(newValue + Math.random() * 20 - 10);
            });
            
            // Keep only last 10 data points
            if (chart.data.labels.length > 10) {
                chart.data.labels.shift();
                chart.data.datasets.forEach(dataset => {
                    dataset.data.shift();
                });
            }
            
            chart.update('none'); // No animation for real-time updates
        }
    }
}

// ============================================
// EXPORT/PRINT FUNCTIONALITY
// ============================================

class ChartExporter {
    exportChart(chartId, format = 'png') {
        const chart = window.chartManager.charts.get(chartId);
        if (!chart) return;

        const canvas = chart.canvas;
        
        if (format === 'png') {
            const link = document.createElement('a');
            link.download = `chart-${chartId}-${Date.now()}.png`;
            link.href = canvas.toDataURL('image/png');
            link.click();
        } else if (format === 'pdf') {
            // Would require additional PDF library
            console.log('PDF export requires additional library');
        }
    }

    printChart(chartId) {
        const chart = window.chartManager.charts.get(chartId);
        if (!chart) return;

        const canvas = chart.canvas;
        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>Chart Print</title>
                    <style>
                        body { margin: 0; padding: 20px; text-align: center; }
                        img { max-width: 100%; height: auto; }
                    </style>
                </head>
                <body>
                    <img src="${canvas.toDataURL('image/png')}" />
                </body>
            </html>
        `);
        printWindow.document.close();
        printWindow.print();
    }
}

// ============================================
// INITIALIZATION AND GLOBAL SETUP
// ============================================

// Initialize managers
const chartManager = new ChartManager();
const dashboardWidgets = new DashboardWidgets();
const realTimeUpdates = new RealTimeUpdates();
const chartExporter = new ChartExporter();

// Make available globally
window.chartManager = chartManager;
window.dashboardWidgets = dashboardWidgets;
window.realTimeUpdates = realTimeUpdates;
window.chartExporter = chartExporter;

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    if (typeof Chart !== 'undefined') {
        chartManager.init();
    }
    
    // Start real-time updates
    realTimeUpdates.startUpdates();
    
    // Add chart export buttons to existing charts
    setTimeout(() => {
        document.querySelectorAll('canvas[data-chart]').forEach(canvas => {
            const container = canvas.closest('.card, .chart-container');
            if (container && !container.querySelector('.chart-actions')) {
                const actions = document.createElement('div');
                actions.className = 'chart-actions';
                actions.style.cssText = 'position: absolute; top: 10px; right: 10px; display: flex; gap: 5px;';
                actions.innerHTML = `
                    <button class="btn btn-sm btn-outline-secondary" onclick="chartExporter.exportChart('${canvas.id}', 'png')" title="Export as PNG">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="chartExporter.printChart('${canvas.id}')" title="Print Chart">
                        <i class="fas fa-print"></i>
                    </button>
                `;
                
                container.style.position = 'relative';
                container.appendChild(actions);
            }
        });
    }, 1000);
});

// ============================================
// UTILITY FUNCTIONS
// ============================================

// Helper function to create sample data for testing
function createSampleData(type) {
    const sampleData = {
        line: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Patients',
                data: [65, 59, 80, 81, 56, 55]
            }]
        },
        bar: {
            labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'],
            datasets: [{
                label: 'Appointments',
                data: [12, 19, 3, 5, 2]
            }]
        },
        doughnut: {
            labels: ['Scheduled', 'Completed', 'Cancelled'],
            data: [65, 28, 7]
        }
    };
    
    return sampleData[type] || sampleData.line;
}

// Export utility functions
window.createSampleData = createSampleData;