// Componente Reports
class Reports {
    constructor() {
        this.init();
    }

    init() {
        log('Initializing Reports component');
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Filtros de ventas
        const filterSalesBtn = document.getElementById('filter-sales');
        if (filterSalesBtn) {
            filterSalesBtn.addEventListener('click', () => {
                this.loadSalesReport();
            });
        }
    }

    async loadSalesReport() {
        try {
            showLoading(true);
            log('Loading sales report...');

            // Obtener fechas de filtro
            const startDate = document.getElementById('start-date')?.value || null;
            const endDate = document.getElementById('end-date')?.value || null;

            // Cargar datos de ventas
            const salesData = await ReportsAPI.getSalesTotal(startDate, endDate);
            const membershipData = await ReportsAPI.getSalesByMembership();

            // Mostrar datos
            this.displaySalesReport(salesData, membershipData);

        } catch (error) {
            log('Error loading sales report', 'error', error);
            this.showReportError('sales-data', 'Error cargando reporte de ventas');
        } finally {
            showLoading(false);
        }
    }

    displaySalesReport(salesData, membershipData) {
        const container = document.getElementById('sales-data');
        if (!container) return;

        container.innerHTML = `
            <div class="report-section">
                <h3>Resumen de Ventas</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <span class="stat-value">${formatCurrency(salesData.total_amount || 0)}</span>
                        <span class="stat-label">Total en Ventas</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">${salesData.total_sales || 0}</span>
                        <span class="stat-label">Número de Ventas</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">${formatCurrency(salesData.average_sale || 0)}</span>
                        <span class="stat-label">Venta Promedio</span>
                    </div>
                </div>
            </div>

            <div class="report-section">
                <h3>Ventas por Membresía</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <span class="stat-value">${formatCurrency(membershipData.with_membership?.total_amount || 0)}</span>
                        <span class="stat-label">Con Membresía</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">${formatCurrency(membershipData.without_membership?.total_amount || 0)}</span>
                        <span class="stat-label">Sin Membresía</span>
                    </div>
                </div>
            </div>
        `;
    }

    async loadCustomersReport() {
        try {
            showLoading(true);
            log('Loading customers report...');

            const customersData = await ReportsAPI.getCustomersTotal();
            this.displayCustomersReport(customersData);

        } catch (error) {
            log('Error loading customers report', 'error', error);
            this.showReportError('customers-data', 'Error cargando reporte de clientes');
        } finally {
            showLoading(false);
        }
    }

    displayCustomersReport(customersData) {
        const container = document.getElementById('customers-data');
        if (!container) return;

        container.innerHTML = `
            <div class="report-section">
                <h3>Estadísticas de Clientes</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <span class="stat-value">${customersData.total_customers || 0}</span>
                        <span class="stat-label">Clientes Atendidos</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">${customersData.unique_customers || 0}</span>
                        <span class="stat-label">Clientes Únicos</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">${customersData.returning_customers || 0}</span>
                        <span class="stat-label">Clientes Recurrentes</span>
                    </div>
                </div>
            </div>
        `;
    }

    async loadMoviesReport() {
        try {
            showLoading(true);
            log('Loading movies report...');

            const moviesData = await ReportsAPI.getTicketsByMovie();
            const mostSold = await ReportsAPI.getMostSoldMovie();
            const leastSold = await ReportsAPI.getLeastSoldMovie();

            this.displayMoviesReport(moviesData, mostSold, leastSold);

        } catch (error) {
            log('Error loading movies report', 'error', error);
            this.showReportError('movies-data', 'Error cargando reporte de películas');
        } finally {
            showLoading(false);
        }
    }

    displayMoviesReport(moviesData, mostSold, leastSold) {
        const container = document.getElementById('movies-data');
        if (!container) return;

        // Crear tabla de películas
        let tableRows = '';
        if (moviesData && moviesData.length > 0) {
            tableRows = moviesData.map(movie => `
                <tr>
                    <td>${movie.mov_title || 'N/A'}</td>
                    <td>${movie.mov_genre || 'N/A'}</td>
                    <td>${movie.total_tickets || 0}</td>
                    <td>${formatCurrency(movie.total_revenue || 0)}</td>
                </tr>
            `).join('');
        } else {
            tableRows = '<tr><td colspan="4" class="text-center">No hay datos disponibles</td></tr>';
        }

        container.innerHTML = `
            <div class="report-section">
                <h3>Rendimiento de Películas</h3>
                <div class="stats-grid">
                    <div class="stat-card">
                        <span class="stat-value">${mostSold.mov_title || 'N/A'}</span>
                        <span class="stat-label">Más Vendida (${mostSold.total_tickets || 0} boletos)</span>
                    </div>
                    <div class="stat-card">
                        <span class="stat-value">${leastSold.mov_title || 'N/A'}</span>
                        <span class="stat-label">Menos Vendida (${leastSold.total_tickets || 0} boletos)</span>
                    </div>
                </div>
            </div>

            <div class="report-section">
                <h3>Detalle por Película</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Película</th>
                            <th>Género</th>
                            <th>Boletos Vendidos</th>
                            <th>Ingresos</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tableRows}
                    </tbody>
                </table>
            </div>
        `;
    }

    async loadTicketsReport() {
        try {
            showLoading(true);
            log('Loading tickets report...');

            const ticketsData = await ReportsAPI.getTicketsByAuditorium();
            this.displayTicketsReport(ticketsData);

        } catch (error) {
            log('Error loading tickets report', 'error', error);
            this.showReportError('tickets-data', 'Error cargando reporte de boletos');
        } finally {
            showLoading(false);
        }
    }

    displayTicketsReport(ticketsData) {
        const container = document.getElementById('tickets-data');
        if (!container) return;

        // Crear tabla de auditorios
        let tableRows = '';
        if (ticketsData && ticketsData.length > 0) {
            tableRows = ticketsData.map(auditorium => `
                <tr>
                    <td>${auditorium.aud_name || 'N/A'}</td>
                    <td>${auditorium.aud_type || 'N/A'}</td>
                    <td>${auditorium.total_capacity || 0}</td>
                    <td>${auditorium.total_tickets || 0}</td>
                    <td>${formatCurrency(auditorium.total_revenue || 0)}</td>
                    <td>${auditorium.occupancy_rate || 0}%</td>
                </tr>
            `).join('');
        } else {
            tableRows = '<tr><td colspan="6" class="text-center">No hay datos disponibles</td></tr>';
        }

        container.innerHTML = `
            <div class="report-section">
                <h3>Ventas por Auditorio</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Auditorio</th>
                            <th>Tipo</th>
                            <th>Capacidad</th>
                            <th>Boletos Vendidos</th>
                            <th>Ingresos</th>
                            <th>Ocupación</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tableRows}
                    </tbody>
                </table>
            </div>
        `;
    }

    showReportError(containerId, message) {
        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = `
            <div class="empty-state">
                <div class="icon">⚠️</div>
                <h3>Error</h3>
                <p>${message}</p>
                <button class="btn-primary" onclick="window.location.reload()">Reintentar</button>
            </div>
        `;
    }
}

// Crear instancia global
window.Reports = new Reports();
