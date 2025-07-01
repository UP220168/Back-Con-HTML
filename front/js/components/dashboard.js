// Componente Dashboard
class Dashboard {
    constructor() {
        this.data = {};
        this.init();
    }

    init() {
        log('Initializing Dashboard component');
    }

    async loadData() {
        try {
            showLoading(true);
            log('Loading dashboard data...');

            // Cargar datos del dashboard desde la API
            const dashboardData = await ReportsAPI.getDashboard();
            log('Dashboard data received:', 'info', dashboardData);
            this.data = dashboardData;

            // Actualizar la UI
            this.updateUI();

        } catch (error) {
            log('Error loading dashboard data', 'error', error);
            this.showError('Error cargando los datos del dashboard');
        } finally {
            showLoading(false);
        }
    }

    updateUI() {
        log('Updating dashboard UI', 'info', this.data);

        // Actualizar métricas principales
        this.updateSalesMetrics();
        this.updateCustomersMetrics();
        this.updateMoviesMetrics();
    }

    updateSalesMetrics() {
        const totalSalesElement = document.getElementById('total-sales');
        const totalTransactionsElement = document.getElementById('total-transactions');

        if (this.data.summary) {
            if (totalSalesElement) {
                totalSalesElement.textContent = formatCurrency(this.data.summary.total_sales_amount || 0);
            }
            if (totalTransactionsElement) {
                totalTransactionsElement.textContent = this.data.summary.total_sales_count || 0;
            }
        }
    }

    updateCustomersMetrics() {
        const totalCustomersElement = document.getElementById('total-customers');
        
        if (this.data.summary && totalCustomersElement) {
            totalCustomersElement.textContent = this.data.summary.total_customers || 0;
        }
    }

    updateMoviesMetrics() {
        const totalTicketsElement = document.getElementById('total-tickets');
        const moviesAvailableElement = document.getElementById('movies-available');

        // Mostrar datos básicos disponibles
        if (this.data.summary) {
            if (totalTicketsElement) {
                totalTicketsElement.textContent = this.data.summary.total_tickets || 0;
            }
        }

        // Cargar número de películas disponibles
        this.loadMoviesCount();
    }

    async loadMoviesCount() {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/movies`);
            const data = await response.json();
            
            const moviesAvailableElement = document.getElementById('movies-available');
            if (moviesAvailableElement && data.movies) {
                moviesAvailableElement.textContent = data.movies.length;
            }
        } catch (error) {
            log('Error loading movies count', 'error', error);
        }
    }

    showError(message) {
        // Mostrar mensaje de error en el dashboard
        const dashboardGrid = document.querySelector('.dashboard-grid');
        if (dashboardGrid) {
            dashboardGrid.innerHTML = `
                <div class="card">
                    <div class="card-content">
                        <div class="empty-state">
                            <div class="icon">⚠️</div>
                            <h3>Error</h3>
                            <p>${message}</p>
                            <button class="btn-primary" onclick="Dashboard.loadData()">Reintentar</button>
                        </div>
                    </div>
                </div>
            `;
        }
    }

    // Método para refrescar datos
    async refresh() {
        await this.loadData();
    }
}

// Crear instancia global
window.Dashboard = new Dashboard();

// Auto-cargar datos cuando se inicializa la página
document.addEventListener('DOMContentLoaded', () => {
    // Cargar datos si ya estamos en el dashboard
    if (window.location.hash === '' || window.location.hash === '#dashboard') {
        setTimeout(() => {
            window.Dashboard.loadData();
        }, 500);
    }
});
