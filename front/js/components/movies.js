// Componente Movies Management
class Movies {
    constructor() {
        this.movies = [];
        this.filteredMovies = [];
        this.currentMovie = null;
        this.init();
    }

    init() {
        log('Initializing Movies component');
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Botón agregar película
        const addMovieBtn = document.getElementById('add-movie-btn');
        if (addMovieBtn) {
            addMovieBtn.addEventListener('click', () => this.openAddMovieModal());
        }

        // Buscador
        const searchInput = document.getElementById('movie-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.filterMovies(e.target.value));
        }

        // Filtros
        const genreFilter = document.getElementById('genre-filter');
        const statusFilter = document.getElementById('status-filter');
        const clearFiltersBtn = document.getElementById('clear-filters');

        if (genreFilter) {
            genreFilter.addEventListener('change', () => this.applyFilters());
        }

        if (statusFilter) {
            statusFilter.addEventListener('change', () => this.applyFilters());
        }

        if (clearFiltersBtn) {
            clearFiltersBtn.addEventListener('click', () => this.clearFilters());
        }

        // Formulario de película
        const movieForm = document.getElementById('movie-form');
        if (movieForm) {
            movieForm.addEventListener('submit', (e) => this.handleMovieSubmit(e));
        }
    }

    async loadData() {
        try {
            showLoading(true);
            log('Loading movies data...');

            // Cargar películas desde la API
            const response = await fetch(`${CONFIG.API_BASE_URL}/movies`);
            if (!response.ok) {
                throw new Error('Error al cargar películas');
            }

            const data = await response.json();
            log('Movies loaded:', 'info', data);

            this.movies = data.movies || [];
            this.filteredMovies = [...this.movies];

            // Mostrar películas
            this.renderMovies();

        } catch (error) {
            log('Error loading movies', 'error', error);
            this.showError('Error al cargar las películas');
        } finally {
            showLoading(false);
        }
    }

    renderMovies() {
        const moviesList = document.getElementById('movies-list');
        if (!moviesList) return;

        // Limpiar contenido
        moviesList.innerHTML = '';

        if (this.filteredMovies.length === 0) {
            moviesList.innerHTML = `
                <div class="empty-state">
                    <span class="icon">🎬</span>
                    <h3>No hay películas</h3>
                    <p>No se encontraron películas con los filtros aplicados</p>
                </div>
            `;
            return;
        }

        // Renderizar cada película
        this.filteredMovies.forEach(movie => {
            const movieCard = this.createMovieCard(movie);
            moviesList.appendChild(movieCard);
        });

        log(`Rendered ${this.filteredMovies.length} movies`);
    }

    createMovieCard(movie) {
        const card = document.createElement('div');
        card.className = 'movie-item';
        
        card.innerHTML = `
            <div class="movie-title">${movie.mov_title}</div>
            <div class="movie-details">
                <div class="movie-detail">
                    <span class="label">Duración:</span>
                    <span class="value">${movie.mov_duration} min</span>
                </div>
                <div class="movie-detail">
                    <span class="label">Clasificación:</span>
                    <span class="value">${movie.mov_classification}</span>
                </div>
                <div class="movie-detail">
                    <span class="label">Género:</span>
                    <span class="value">${movie.mov_genre}</span>
                </div>
                <div class="movie-detail">
                    <span class="label">Estado:</span>
                    <span class="value">
                        <span class="movie-status ${movie.mov_status}">
                            ${movie.mov_status === 'active' ? 'Activo' : 'Inactivo'}
                        </span>
                    </span>
                </div>
            </div>
            <div class="movie-actions">
                <button class="btn-small btn-edit" onclick="Movies.editMovie('${movie.mov_id}')">
                    Editar
                </button>
                <button class="btn-small btn-delete" onclick="Movies.deleteMovie('${movie.mov_id}')">
                    Eliminar
                </button>
            </div>
        `;

        return card;
    }

    filterMovies(searchTerm) {
        const term = searchTerm.toLowerCase();
        this.applyFilters(term);
    }

    applyFilters(searchTerm = null) {
        const search = searchTerm || document.getElementById('movie-search')?.value.toLowerCase() || '';
        const genreFilter = document.getElementById('genre-filter')?.value || '';
        const statusFilter = document.getElementById('status-filter')?.value || '';

        this.filteredMovies = this.movies.filter(movie => {
            const matchesSearch = !search || 
                movie.mov_title.toLowerCase().includes(search) ||
                movie.mov_genre.toLowerCase().includes(search);
            
            const matchesGenre = !genreFilter || movie.mov_genre === genreFilter;
            const matchesStatus = !statusFilter || movie.mov_status === statusFilter;

            return matchesSearch && matchesGenre && matchesStatus;
        });

        this.renderMovies();
        log(`Filtered movies: ${this.filteredMovies.length} of ${this.movies.length}`);
    }

    clearFilters() {
        // Limpiar inputs
        const searchInput = document.getElementById('movie-search');
        const genreFilter = document.getElementById('genre-filter');
        const statusFilter = document.getElementById('status-filter');

        if (searchInput) searchInput.value = '';
        if (genreFilter) genreFilter.value = '';
        if (statusFilter) statusFilter.value = '';

        // Mostrar todas las películas
        this.filteredMovies = [...this.movies];
        this.renderMovies();
    }

    openAddMovieModal() {
        this.currentMovie = null;
        
        // Cambiar título del modal
        const modalTitle = document.getElementById('movie-modal-title');
        if (modalTitle) {
            modalTitle.textContent = 'Agregar Nueva Película';
        }

        // Limpiar formulario
        this.clearMovieForm();

        // Mostrar modal
        const modal = document.getElementById('movie-modal');
        if (modal) {
            modal.style.display = 'flex';
        }
    }

    openEditMovieModal(movieId) {
        this.currentMovie = this.movies.find(m => m.mov_id === movieId);
        
        if (!this.currentMovie) {
            alert('Película no encontrada');
            return;
        }

        // Cambiar título del modal
        const modalTitle = document.getElementById('movie-modal-title');
        if (modalTitle) {
            modalTitle.textContent = 'Editar Película';
        }

        // Llenar formulario con datos de la película
        this.fillMovieForm(this.currentMovie);

        // Mostrar modal
        const modal = document.getElementById('movie-modal');
        if (modal) {
            modal.style.display = 'flex';
        }
    }

    clearMovieForm() {
        const form = document.getElementById('movie-form');
        if (form) {
            form.reset();
            // Establecer valores por defecto
            document.getElementById('movie-status').value = 'active';
        }
    }

    fillMovieForm(movie) {
        document.getElementById('movie-title').value = movie.mov_title || '';
        document.getElementById('movie-duration').value = movie.mov_duration || '';
        document.getElementById('movie-classification').value = movie.mov_classification || '';
        document.getElementById('movie-genre').value = movie.mov_genre || '';
        document.getElementById('movie-status').value = movie.mov_status || 'active';
    }

    async handleMovieSubmit(event) {
        event.preventDefault();
        
        try {
            showLoading(true);

            const formData = new FormData(event.target);
            const movieData = {
                mov_title: formData.get('mov_title'),
                mov_duration: parseInt(formData.get('mov_duration')),
                mov_classification: formData.get('mov_classification'),
                mov_genre: formData.get('mov_genre'),
                mov_status: formData.get('mov_status')
            };

            log('Submitting movie data:', 'info', movieData);

            let response;
            if (this.currentMovie) {
                // Actualizar película existente
                response = await fetch(`${CONFIG.API_BASE_URL}/movies/${this.currentMovie.mov_id}`, {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(movieData)
                });
            } else {
                // Crear nueva película
                response = await fetch(`${CONFIG.API_BASE_URL}/movies`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(movieData)
                });
            }

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error al guardar la película');
            }

            const result = await response.json();
            log('Movie saved successfully:', 'info', result);

            // Cerrar modal
            this.closeMovieModal();

            // Recargar datos
            await this.loadData();

            // Mostrar mensaje de éxito
            alert(this.currentMovie ? 'Película actualizada correctamente' : 'Película creada correctamente');

        } catch (error) {
            log('Error saving movie', 'error', error);
            alert('Error al guardar la película: ' + error.message);
        } finally {
            showLoading(false);
        }
    }

    async editMovie(movieId) {
        this.openEditMovieModal(movieId);
    }

    async deleteMovie(movieId) {
        const movie = this.movies.find(m => m.mov_id === movieId);
        if (!movie) {
            alert('Película no encontrada');
            return;
        }

        if (!confirm(`¿Estás seguro de que quieres eliminar la película "${movie.mov_title}"?`)) {
            return;
        }

        try {
            showLoading(true);

            const response = await fetch(`${CONFIG.API_BASE_URL}/movies/${movieId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error al eliminar la película');
            }

            log('Movie deleted successfully');

            // Recargar datos
            await this.loadData();

            alert('Película eliminada correctamente');

        } catch (error) {
            log('Error deleting movie', 'error', error);
            alert('Error al eliminar la película: ' + error.message);
        } finally {
            showLoading(false);
        }
    }

    closeMovieModal() {
        const modal = document.getElementById('movie-modal');
        if (modal) {
            modal.style.display = 'none';
        }
        this.currentMovie = null;
    }

    showError(message) {
        const moviesList = document.getElementById('movies-list');
        if (moviesList) {
            moviesList.innerHTML = `
                <div class="empty-state">
                    <span class="icon">⚠️</span>
                    <h3>Error</h3>
                    <p>${message}</p>
                    <button class="btn-primary" onclick="Movies.loadData()">Reintentar</button>
                </div>
            `;
        }
    }
}

// Funciones globales para eventos
function closeMovieModal() {
    if (window.Movies) {
        window.Movies.closeMovieModal();
    }
}

// Crear instancia global
window.Movies = new Movies();

// Auto-cargar datos cuando se navega a movies
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.hash === '#movies') {
        window.Movies.loadData();
    }
});
