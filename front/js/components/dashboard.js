// Componente Dashboard
class Dashboard {
    constructor() {
        this.data = {};
        this.isLoading = false;
        this.init();
    }

    init() {
        log('Initializing Dashboard component');
    }

    async loadData() {
        // Evitar cargas múltiples simultáneas
        if (this.isLoading) {
            log('Dashboard is already loading, skipping...', 'warn');
            return;
        }

        try {
            this.isLoading = true;
            showLoading(true);
            log('Loading dashboard data...');

            // Cargar datos del dashboard desde la API
            const dashboardData = await ReportsAPI.getDashboard();
            log('Dashboard data received:', 'info', dashboardData);
            this.data = dashboardData;

            // Cargar datos adicionales para los nuevos reportes
            await Promise.all([
                this.loadTicketsByMovie(),
                this.loadTicketsByAuditorium(), 
                this.loadMostSoldMovie(),
                this.loadLeastSoldMovie()
            ]);

            // Actualizar la UI
            this.updateUI();

        } catch (error) {
            log('Error loading dashboard data', 'error', error);
            this.showError('Error cargando los datos del dashboard');
        } finally {
            this.isLoading = false;
            showLoading(false);
        }
    }

    updateUI() {
        log('Updating dashboard UI', 'info', this.data);

        // Actualizar métricas principales
        this.updateSalesMetrics();
        this.updateCustomersMetrics();
        this.updateMoviesMetrics();
        
        // Actualizar nuevos reportes
        // Actualizar las nuevas secciones de reportes
        this.updateTicketsByMovieChart();
        this.updateTicketsByAuditoriumChart();
        this.updateMoviesHighlights();
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

    // Nuevos métodos para cargar datos de reportes
    async loadTicketsByMovie() {
        try {
            this.data.ticketsByMovie = await ReportsAPI.getTicketsByMovie();
            log('Tickets by movie loaded:', 'info', this.data.ticketsByMovie);
        } catch (error) {
            log('Error loading tickets by movie', 'error', error);
            this.data.ticketsByMovie = { movies: [] };
        }
    }

    async loadTicketsByAuditorium() {
        try {
            this.data.ticketsByAuditorium = await ReportsAPI.getTicketsByAuditorium();
            log('Tickets by auditorium loaded:', 'info', this.data.ticketsByAuditorium);
        } catch (error) {
            log('Error loading tickets by auditorium', 'error', error);
            this.data.ticketsByAuditorium = { auditoriums: [] };
        }
    }

    async loadMostSoldMovie() {
        try {
            this.data.mostSoldMovie = await ReportsAPI.getMostSoldMovie();
            log('Most sold movie loaded:', 'info', this.data.mostSoldMovie);
        } catch (error) {
            log('Error loading most sold movie', 'error', error);
            this.data.mostSoldMovie = { movie: null };
        }
    }

    async loadLeastSoldMovie() {
        try {
            this.data.leastSoldMovie = await ReportsAPI.getLeastSoldMovie();
            log('Least sold movie loaded:', 'info', this.data.leastSoldMovie);
        } catch (error) {
            log('Error loading least sold movie', 'error', error);
            this.data.leastSoldMovie = { movie: null };
        }
    }

    // Métodos para actualizar las nuevas secciones
    updateTicketsByMovieChart() {
        log('Updating tickets by movie chart...', 'info');
        const container = document.getElementById('tickets-by-movie-container');
        if (!container || !this.data.ticketsByMovie) return;

        const movies = this.data.ticketsByMovie.movies || [];
        
        if (movies.length === 0) {
            container.innerHTML = '<p class="no-data">No hay datos de boletos por película</p>';
            return;
        }

        // Mostrar película principal (la más vendida)
        const topMovie = movies[0];
        const totalTickets = movies.reduce((sum, movie) => sum + movie.total_tickets_sold, 0);
        
        container.innerHTML = `
            <div class="metric">
                <span class="metric-value">${this.truncateText(topMovie.movie_title, 20)}</span>
                <span class="metric-label">Película Top</span>
            </div>
            <div class="metric">
                <span class="metric-value">${totalTickets}</span>
                <span class="metric-label">Total Boletos</span>
            </div>
        `;
        
        log('Tickets by movie chart updated', 'info');
    }

    updateTicketsByAuditoriumChart() {
        log('Updating tickets by auditorium chart...', 'info');
        const container = document.getElementById('tickets-by-auditorium-container');
        if (!container || !this.data.ticketsByAuditorium) return;

        const auditoriums = this.data.ticketsByAuditorium.auditoriums || [];
        
        if (auditoriums.length === 0) {
            container.innerHTML = '<p class="no-data">No hay datos de boletos por sala</p>';
            return;
        }

        // Mostrar sala principal (la más vendida) y total
        const topAuditorium = auditoriums[0];
        const totalTickets = auditoriums.reduce((sum, auditorium) => sum + auditorium.total_tickets_sold, 0);
        
        container.innerHTML = `
            <div class="metric">
                <span class="metric-value">${topAuditorium.auditorium_name}</span>
                <span class="metric-label">Sala Top</span>
            </div>
            <div class="metric">
                <span class="metric-value">${totalTickets}</span>
                <span class="metric-label">Total Boletos</span>
            </div>
        `;
        
        log('Tickets by auditorium chart updated', 'info');
    }

    updateMoviesHighlights() {
        const container = document.getElementById('movies-highlights-container');
        if (!container) return;

        const mostSoldMovie = this.data.mostSoldMovie?.movie;
        const leastSoldMovie = this.data.leastSoldMovie?.movie;
        
        if (!mostSoldMovie && !leastSoldMovie) {
            container.innerHTML = '<p class="no-data">No hay datos de películas destacadas</p>';
            return;
        }

        let html = '';
        
        // Película más vendida
        if (mostSoldMovie) {
            html += `
                <div class="movie-section">
                    <div class="movie-section-header">
                        <span class="movie-section-icon">🏆</span>
                        <span class="movie-section-title">Más Vendida</span>
                    </div>
                    <div class="metric movie-metric">
                        <span class="metric-value movie-title">${this.truncateText(mostSoldMovie.movie_title, 20)}</span>
                        <span class="metric-label">${mostSoldMovie.movie_genre}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-value">${mostSoldMovie.total_tickets_sold}</span>
                        <span class="metric-label">Boletos</span>
                    </div>
                </div>
            `;
        }
        
        // Película menos vendida
        if (leastSoldMovie) {
            html += `
                <div class="movie-section">
                    <div class="movie-section-header">
                        <span class="movie-section-icon">📉</span>
                        <span class="movie-section-title">Menos Vendida</span>
                    </div>
                    <div class="metric movie-metric">
                        <span class="metric-value movie-title least-sold">${this.truncateText(leastSoldMovie.movie_title, 20)}</span>
                        <span class="metric-label">${leastSoldMovie.movie_genre}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-value">${leastSoldMovie.total_tickets_sold}</span>
                        <span class="metric-label">Boletos</span>
                    </div>
                </div>
            `;
        }
        
        container.innerHTML = html;
    }

    // Método utilitario para truncar texto
    truncateText(text, maxLength) {
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength - 3) + '...';
    }
}

// Crear instancia global
window.Dashboard = new Dashboard();

// Auto-cargar datos cuando se inicializa la página solo si no se ha cargado ya
document.addEventListener('DOMContentLoaded', () => {
    // Solo cargar datos si ya estamos en el dashboard y no se ha cargado previamente
    if ((window.location.hash === '' || window.location.hash === '#dashboard') && 
        Object.keys(window.Dashboard.data).length === 0) {
        setTimeout(() => {
            window.Dashboard.loadData();
        }, 500);
    }
});
