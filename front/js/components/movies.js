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
        const clearFiltersBtn = document.getElementById('clear-filters');

        if (genreFilter) {
            genreFilter.addEventListener('change', () => this.applyFilters());
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

            // Cargar películas desde la API (incluyendo inactivas para administración)
            // Agregar timestamp para evitar cache
            const timestamp = new Date().getTime();
            const response = await fetch(`${CONFIG.API_BASE_URL}/movies?include_inactive=true&_t=${timestamp}`);
            if (!response.ok) {
                throw new Error('Error al cargar películas');
            }

            const data = await response.json();
            log('Movies loaded:', 'info', data);
            
            // Debug: contar películas por estado
            const activeMovies = (data.movies || []).filter(m => m.mov_status === 'active');
            const inactiveMovies = (data.movies || []).filter(m => m.mov_status === 'inactive');
            console.log(`📊 Películas encontradas: ${data.movies?.length || 0} total | ${activeMovies.length} activas | ${inactiveMovies.length} inactivas`);
            
            // Debug: mostrar URL completa que se está llamando
            console.log(`🔗 URL llamada: ${CONFIG.API_BASE_URL}/movies?include_inactive=true&_t=${timestamp}`);

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
        
        // Determinar las acciones según el estado de la película
        let actionButtons = '';
        if (movie.mov_status === 'active') {
            actionButtons = `
                <button class="btn-small btn-edit" onclick="editMovie('${movie.mov_id}')">
                    Editar
                </button>
                <button class="btn-small btn-delete" onclick="deactivateMovie('${movie.mov_id}')">
                    Desactivar
                </button>
            `;
        } else {
            actionButtons = `
                <button class="btn-small btn-edit" onclick="editMovie('${movie.mov_id}')">
                    Editar
                </button>
                <button class="btn-small btn-success" onclick="reactivateMovie('${movie.mov_id}')">
                    Reactivar
                </button>
            `;
        }
        
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
                ${actionButtons}
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

        this.filteredMovies = this.movies.filter(movie => {
            const matchesSearch = !search || 
                movie.mov_title.toLowerCase().includes(search) ||
                movie.mov_genre.toLowerCase().includes(search);
            
            const matchesGenre = !genreFilter || movie.mov_genre === genreFilter;

            return matchesSearch && matchesGenre;
        });

        this.renderMovies();
        log(`Filtered movies: ${this.filteredMovies.length} of ${this.movies.length}`);
    }

    clearFilters() {
        // Limpiar inputs
        const searchInput = document.getElementById('movie-search');
        const genreFilter = document.getElementById('genre-filter');

        if (searchInput) searchInput.value = '';
        if (genreFilter) genreFilter.value = '';

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
        }
    }

    fillMovieForm(movie) {
        document.getElementById('movie-title').value = movie.mov_title || '';
        document.getElementById('movie-duration').value = movie.mov_duration || '';
        document.getElementById('movie-classification').value = movie.mov_classification || '';
        document.getElementById('movie-genre').value = movie.mov_genre || '';
    }

    async handleMovieSubmit(event) {
        event.preventDefault();
        
        try {
            showLoading(true);

            // Obtener valores directamente de los elementos del formulario
            const movieData = {
                mov_title: document.getElementById('movie-title').value,
                mov_duration: parseInt(document.getElementById('movie-duration').value),
                mov_classification: document.getElementById('movie-classification').value,
                mov_genre: document.getElementById('movie-genre').value
            };

            // Para nuevas películas, siempre usar 'active'. Para ediciones, mantener el estado actual
            if (this.currentMovie) {
                // Al editar, mantener el estado actual de la película
                movieData.mov_status = this.currentMovie.mov_status;
            } else {
                // Al crear, siempre establecer como activo
                movieData.mov_status = 'active';
            }

            // Validar que los campos requeridos estén llenos
            if (!movieData.mov_title || !movieData.mov_duration || !movieData.mov_classification || !movieData.mov_genre) {
                throw new Error('Por favor complete todos los campos requeridos');
            }

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
            alert(this.currentMovie ? 'Película actualizada correctamente' : 'Película actualizada correctamente');

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

        if (!confirm(`¿Estás seguro de que quieres desactivar la película "${movie.mov_title}"?\n\nEsta acción eliminara la pelicula de forma permanente`)) {
            return;
        }

        try {
            showLoading(true);

            const response = await fetch(`${CONFIG.API_BASE_URL}/movies/${movieId}`, {
                method: 'DELETE'
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error al desactivar la película');
            }

            log('Movie deactivated successfully');

            // Recargar datos
            await this.loadData();

            alert('Película desactivada correctamente');

        } catch (error) {
            log('Error deactivating movie', 'error', error);
            alert('Error al desactivar la película: ' + error.message);
        } finally {
            showLoading(false);
        }
    }

    async reactivateMovie(movieId) {
        const movie = this.movies.find(m => m.mov_id === movieId);
        if (!movie) {
            alert('Película no encontrada');
            return;
        }

        if (!confirm(`¿Estás seguro de que quieres reactivar la película "${movie.mov_title}"?`)) {
            return;
        }

        try {
            showLoading(true);

            // Actualizar el estado a activo
            const response = await fetch(`${CONFIG.API_BASE_URL}/movies/${movieId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    mov_status: 'active'
                })
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error al reactivar la película');
            }

            log('Movie reactivated successfully');

            // Recargar datos
            await this.loadData();

            alert('Película reactivada correctamente');

        } catch (error) {
            log('Error reactivating movie', 'error', error);
            alert('Error al reactivar la película: ' + error.message);
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

function editMovie(movieId) {
    if (window.Movies) {
        window.Movies.editMovie(movieId);
    }
}

function deleteMovie(movieId) {
    if (window.Movies) {
        window.Movies.deleteMovie(movieId);
    }
}

function deactivateMovie(movieId) {
    if (window.Movies) {
        window.Movies.deleteMovie(movieId);
    }
}

function reactivateMovie(movieId) {
    if (window.Movies) {
        window.Movies.reactivateMovie(movieId);
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
