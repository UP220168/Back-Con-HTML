// Componente Screenings
class Screenings {
    constructor() {
        this.screenings = [];
        this.movies = [];
        this.auditoriums = [];
        this.editingScreening = null;
        
        // Inicializar cuando el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    init() {
        log('Initializing Screenings component');
        
        // Verificar dependencias
        this.checkDependencies();
        
        this.setupEventListeners();
        // No cargar datos automáticamente en init - solo cuando se navega a la página
    }
    
    checkDependencies() {
        // Verificar showLoading
        if (typeof showLoading === 'undefined') {
            console.warn('showLoading no está disponible, creando función mock');
            window.showLoading = function(show) {
                console.log('showLoading mock:', show);
            };
        }
        
        // Verificar log
        if (typeof log === 'undefined') {
            console.warn('log no está disponible, creando función mock');
            window.log = function(message, type = 'info', data = null) {
                console.log(`[${type.toUpperCase()}]`, message, data);
            };
        }
        
        // Verificar CONFIG
        if (typeof CONFIG === 'undefined') {
            console.error('CONFIG no está disponible - el componente no funcionará correctamente');
        }
    }

    setupEventListeners() {
        // Botón agregar función
        const addBtn = document.getElementById('add-screening-btn');
        if (addBtn) {
            addBtn.addEventListener('click', () => this.showAddScreeningModal());
        }

        // Filtros
        const movieFilter = document.getElementById('movie-filter');
        const auditoriumFilter = document.getElementById('auditorium-filter');
        const dateFilter = document.getElementById('date-filter');
        const clearFilters = document.getElementById('clear-screening-filters');

        if (movieFilter) movieFilter.addEventListener('change', () => this.applyFilters());
        if (auditoriumFilter) auditoriumFilter.addEventListener('change', () => this.applyFilters());
        if (dateFilter) dateFilter.addEventListener('change', () => this.applyFilters());
        if (clearFilters) clearFilters.addEventListener('click', () => this.clearFilters());
    }

    async loadInitialData() {
        try {
            showLoading(true);
            
            // Cargar datos desde la base de datos únicamente
            await Promise.all([
                this.loadMoviesFromAPI(),
                this.loadAuditoriumsFromAPI(),
                this.loadScreeningsFromAPI()
            ]);
            
            this.populateFilters();
            this.renderScreenings();
            
            log('All data loaded successfully from database', 'info');
            
        } catch (error) {
            log('Error loading data from API', 'error', error);
            
            // En caso de error, mostrar mensaje al usuario
            this.showErrorMessage('Error al cargar datos desde la base de datos. Por favor, verifica la conexión.');
            
            // No usar datos de ejemplo - dejar vacío si falla la API
            this.movies = [];
            this.auditoriums = [];
            this.screenings = [];
            this.populateFilters();
            this.renderScreenings();
            
        } finally {
            showLoading(false);
        }
    }
    
    showErrorMessage(message) {
        const tbody = document.getElementById('screenings-list');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" style="text-align: center; color: #dc3545; padding: 20px;">
                        <i class="fas fa-exclamation-triangle"></i> ${message}
                        <br><br>
                        <button class="btn-primary" onclick="window.Screenings.loadData()">
                            Reintentar
                        </button>
                    </td>
                </tr>
            `;
        }
    }

    async loadMoviesFromAPI() {
        try {
            log('Loading movies from API...', 'info');
            const data = await API.movies.getAll();
            
            if (data.movies && data.movies.length > 0) {
                this.movies = data.movies.filter(movie => movie.mov_status === 'active');
                log(`Movies loaded successfully: ${this.movies.length} active movies`, 'info');
            } else {
                this.movies = [];
                log('No active movies found in database', 'warn');
            }
        } catch (error) {
            log('Error loading movies from API', 'error', error);
            this.movies = [];
            throw new Error(`Error cargando películas: ${error.message}`);
        }
    }

    async loadAuditoriumsFromAPI() {
        try {
            log('Loading auditoriums from API...', 'info');
            const data = await API.auditoriums.getAll();
            
            if (data.auditoriums && data.auditoriums.length > 0) {
                this.auditoriums = data.auditoriums.map(aud => ({
                    ...aud,
                    aud_capacity: aud.total_capacity // Mapear el campo de capacidad
                }));
                log(`Auditoriums loaded successfully: ${this.auditoriums.length} auditoriums`, 'info');
            } else {
                this.auditoriums = [];
                log('No auditoriums found in database', 'warn');
            }
        } catch (error) {
            log('Error loading auditoriums from API', 'error', error);
            this.auditoriums = [];
            throw new Error(`Error cargando auditoriums: ${error.message}`);
        }
    }

    async loadScreeningsFromAPI() {
        try {
            log('Loading screenings from API...', 'info');
            const data = await API.screenings.getAll();
            
            if (data.screenings && data.screenings.length > 0) {
                // Enriquecer los datos de screenings con información de películas y salas
                this.screenings = data.screenings.map(screening => {
                    const movie = this.movies.find(m => m.mov_id === screening.scr_mov_id);
                    const auditorium = this.auditoriums.find(a => a.aud_id === screening.scr_aud_id);
                    
                    // Combinar fecha y hora en un datetime para compatibilidad con el frontend
                    const startDateTime = new Date(`${screening.scr_date}T${screening.scr_time}`);
                    
                    return {
                        ...screening,
                        scr_start_time: startDateTime.toISOString(), // Para compatibilidad con el código existente
                        movie_title: movie ? movie.mov_title : 'Película no encontrada',
                        movie_duration: movie ? movie.mov_duration : 120,
                        auditorium_name: auditorium ? auditorium.aud_name : 'Sala no encontrada',
                        scr_ticket_price: screening.scr_price // Mapear nombre del campo
                    };
                });
                log(`Screenings loaded successfully: ${this.screenings.length} screenings`, 'info');
            } else {
                this.screenings = [];
                log('No screenings found in database', 'info');
            }
        } catch (error) {
            log('Error loading screenings from API', 'error', error);
            this.screenings = [];
            throw new Error(`Error cargando funciones: ${error.message}`);
        }
    }

    populateFilters() {
        // Llenar filtro de películas
        const movieFilter = document.getElementById('movie-filter');
        if (movieFilter) {
            movieFilter.innerHTML = '<option value="">Todas las películas</option>';
            this.movies.forEach(movie => {
                const option = document.createElement('option');
                option.value = movie.mov_id;
                option.textContent = movie.mov_title;
                movieFilter.appendChild(option);
            });
        }

        // Llenar filtro de salas
        const auditoriumFilter = document.getElementById('auditorium-filter');
        if (auditoriumFilter) {
            auditoriumFilter.innerHTML = '<option value="">Todas las salas</option>';
            this.auditoriums.forEach(aud => {
                const option = document.createElement('option');
                option.value = aud.aud_id;
                option.textContent = aud.aud_name;
                auditoriumFilter.appendChild(option);
            });
        }

        // Establecer fecha actual como valor por defecto
        const dateFilter = document.getElementById('date-filter');
        if (dateFilter) {
            const today = new Date();
            dateFilter.value = today.toISOString().split('T')[0];
        }
    }

    renderScreenings() {
        const tbody = document.getElementById('screenings-list');
        if (!tbody) {
            log('Screenings table body not found', 'error');
            return;
        }

        tbody.innerHTML = '';

        if (this.screenings.length === 0) {
            let message = '';
            if (this.movies.length === 0) {
                message = 'No hay películas disponibles en el sistema';
            } else if (this.auditoriums.length === 0) {
                message = 'No hay auditoriums disponibles en el sistema';
            } else {
                message = 'No hay funciones programadas. <br><br><button class="btn-primary" onclick="window.Screenings.showAddScreeningModal()">Programar Primera Función</button>';
            }
            
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" style="text-align: center; padding: 40px; color: #6c757d;">
                        <i class="fas fa-calendar-times" style="font-size: 3em; margin-bottom: 20px; display: block;"></i>
                        ${message}
                    </td>
                </tr>
            `;
            return;
        }

        this.screenings.forEach(screening => {
            const row = this.createScreeningRow(screening);
            tbody.appendChild(row);
        });
        
        log(`Rendered ${this.screenings.length} screenings`, 'info');
    }

    createScreeningRow(screening) {
        const row = document.createElement('tr');
        
        const startTime = new Date(screening.scr_start_time);
        const dateStr = startTime.toLocaleDateString('es-MX');
        const timeStr = startTime.toLocaleTimeString('es-MX', {hour: '2-digit', minute:'2-digit'});
        
        const statusClass = screening.scr_status === 'scheduled' ? 'status-active' : 'status-inactive';
        const statusText = screening.scr_status === 'scheduled' ? 'Programada' : 'Cancelada';

        row.innerHTML = `
            <td>${screening.movie_title}</td>
            <td>${screening.auditorium_name}</td>
            <td>${dateStr}</td>
            <td>${timeStr}</td>
            <td>$${screening.scr_ticket_price.toFixed(2)}</td>
            <td><span class="status ${statusClass}">${statusText}</span></td>
            <td>
                <button class="btn-sm btn-primary" onclick="window.Screenings.editScreening('${screening.scr_id}')">
                    Editar
                </button>
                <button class="btn-sm btn-danger" onclick="window.Screenings.deleteScreening('${screening.scr_id}')">
                    Eliminar
                </button>
            </td>
        `;

        return row;
    }

    applyFilters() {
        const movieFilter = document.getElementById('movie-filter').value;
        const auditoriumFilter = document.getElementById('auditorium-filter').value;
        const dateFilter = document.getElementById('date-filter').value;

        let filteredScreenings = [...this.screenings];

        if (movieFilter) {
            filteredScreenings = filteredScreenings.filter(s => s.scr_mov_id === movieFilter);
        }

        if (auditoriumFilter) {
            filteredScreenings = filteredScreenings.filter(s => s.scr_aud_id === auditoriumFilter);
        }

        if (dateFilter) {
            filteredScreenings = filteredScreenings.filter(s => {
                return s.scr_date === dateFilter;
            });
        }

        // Renderizar funciones filtradas
        const tbody = document.getElementById('screenings-list');
        if (tbody) {
            tbody.innerHTML = '';
            filteredScreenings.forEach(screening => {
                const row = this.createScreeningRow(screening);
                tbody.appendChild(row);
            });
        }
    }

    clearFilters() {
        document.getElementById('movie-filter').value = '';
        document.getElementById('auditorium-filter').value = '';
        document.getElementById('date-filter').value = '';
        this.renderScreenings();
    }

    showAddScreeningModal() {
        this.editingScreening = null;
        this.showScreeningModal();
    }

    editScreening(screeningId) {
        this.editingScreening = this.screenings.find(s => s.scr_id === screeningId);
        if (this.editingScreening) {
            this.showScreeningModal(this.editingScreening);
        }
    }

    showScreeningModal(screening = null) {
        const isEditing = screening !== null;
        
        // Verificar si hay datos necesarios
        if (this.movies.length === 0 || this.auditoriums.length === 0) {
            alert('No se pueden programar funciones. Asegúrate de que haya películas y auditoriums disponibles en el sistema.');
            return;
        }
        
        // Usar el modal existente en el HTML
        const modal = document.getElementById('screening-modal');
        const modalTitle = document.getElementById('screening-modal-title');
        const movieSelect = document.getElementById('screening-movie-select');
        const auditoriumSelect = document.getElementById('screening-auditorium-select');
        const dateInput = document.getElementById('screening-date-input');
        const timeSelect = document.getElementById('screening-time-select');
        const priceInput = document.getElementById('screening-price-input');
        const form = document.getElementById('screening-form');
        
        if (!modal || !modalTitle || !movieSelect || !auditoriumSelect || !dateInput || !timeSelect || !priceInput || !form) {
            console.error('Modal elements not found');
            return;
        }
        
        // Configurar título
        modalTitle.textContent = isEditing ? 'Editar Función' : 'Programar Nueva Función';
        
        // Poblar select de películas
        movieSelect.innerHTML = '<option value="">Seleccionar película</option>';
        this.movies.forEach(movie => {
            const option = document.createElement('option');
            option.value = movie.mov_id;
            option.textContent = `${movie.mov_title} (${movie.mov_duration} min)`;
            if (screening && screening.scr_mov_id === movie.mov_id) {
                option.selected = true;
            }
            movieSelect.appendChild(option);
        });
        
        // Poblar select de auditoriums
        auditoriumSelect.innerHTML = '<option value="">Seleccionar sala</option>';
        this.auditoriums.forEach(aud => {
            const option = document.createElement('option');
            option.value = aud.aud_id;
            option.textContent = `${aud.aud_name} (${aud.aud_capacity} asientos)`;
            if (screening && screening.scr_aud_id === aud.aud_id) {
                option.selected = true;
            }
            auditoriumSelect.appendChild(option);
        });
        
        // Configurar fecha (usar mañana por defecto para evitar problemas de validación)
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        dateInput.value = screening ? screening.scr_date : tomorrow.toISOString().split('T')[0];
        
        // Configurar precio
        priceInput.value = screening ? screening.scr_price : '89.50';
        
        // Poblar horas
        this.populateTimeOptions(timeSelect, screening);
        
        // Mostrar modal
        modal.style.display = 'block';
        
        // Configurar eventos
        const newForm = form.cloneNode(true);
        form.parentNode.replaceChild(newForm, form);
        newForm.addEventListener('submit', (e) => this.handleScreeningSubmit(e));
        
        // Eventos para actualizar horas disponibles
        movieSelect.addEventListener('change', () => this.updateAvailableTimesModal());
        auditoriumSelect.addEventListener('change', () => this.updateAvailableTimesModal());
        dateInput.addEventListener('change', () => this.updateAvailableTimesModal());
    }

    populateTimeOptions(timeSelect, currentScreening = null) {
        timeSelect.innerHTML = '<option value="">Seleccionar hora</option>';
        
        // Generar intervalos de 30 minutos desde las 10:00 hasta las 23:30
        for (let hour = 10; hour <= 23; hour++) {
            for (let minute of [0, 30]) {
                if (hour === 23 && minute === 30) break; // No incluir 23:30
                
                const timeStr = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
                const option = document.createElement('option');
                option.value = timeStr;
                option.textContent = timeStr;
                
                if (currentScreening && 
                    currentScreening.scr_time && 
                    currentScreening.scr_time.substring(0, 5) === timeStr) {
                    option.selected = true;
                }
                
                timeSelect.appendChild(option);
            }
        }
    }

    updateAvailableTimesModal() {
        const auditoriumId = document.getElementById('screening-auditorium-select').value;
        const selectedDate = document.getElementById('screening-date-input').value;
        const timeSelect = document.getElementById('screening-time-select');
        
        if (!auditoriumId || !selectedDate) return;

        // Encontrar funciones existentes en esa sala y fecha
        const existingScreenings = this.screenings.filter(s => {
            return s.scr_aud_id === auditoriumId && 
                   s.scr_date === selectedDate &&
                   (!this.editingScreening || s.scr_id !== this.editingScreening.scr_id);
        });

        // Regenerar opciones de tiempo
        timeSelect.innerHTML = '<option value="">Seleccionar hora</option>';
        
        for (let hour = 10; hour <= 23; hour++) {
            for (let minute of [0, 30]) {
                if (hour === 23 && minute === 30) break;
                
                const timeStr = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
                const currentTime = new Date(`${selectedDate}T${timeStr}:00`);
                
                // Verificar si este horario está disponible
                const isAvailable = this.isTimeSlotAvailable(currentTime, existingScreenings);
                
                const option = document.createElement('option');
                option.value = timeStr;
                option.textContent = timeStr;
                option.disabled = !isAvailable;
                
                if (!isAvailable) {
                    option.textContent += ' (Ocupado)';
                    option.style.color = '#999';
                }
                
                timeSelect.appendChild(option);
            }
        }
    }

    isTimeSlotAvailable(proposedTime, existingScreenings) {
        const movieSelect = document.getElementById('screening-movie');
        const selectedMovieId = movieSelect.value;
        
        if (!selectedMovieId) return true;
        
        const selectedMovie = this.movies.find(m => m.mov_id === selectedMovieId);
        if (!selectedMovie) return true;
        
        const movieDuration = selectedMovie.mov_duration;
        const proposedEndTime = new Date(proposedTime.getTime() + movieDuration * 60000); // Duración en minutos
        
        // Agregar 30 minutos de buffer entre funciones
        const bufferTime = 30 * 60000;
        const proposedStartWithBuffer = new Date(proposedTime.getTime() - bufferTime);
        const proposedEndWithBuffer = new Date(proposedEndTime.getTime() + bufferTime);
        
        // Verificar conflictos con funciones existentes
        for (const existing of existingScreenings) {
            const existingStart = new Date(`${existing.scr_date}T${existing.scr_time}`);
            const existingMovie = this.movies.find(m => m.mov_id === existing.scr_mov_id);
            const existingEnd = new Date(existingStart.getTime() + existingMovie.mov_duration * 60000);
            
            // Verificar si hay conflicto
            if (proposedStartWithBuffer < existingEnd && proposedEndWithBuffer > existingStart) {
                return false;
            }
        }
        
        return true;
    }

    async handleScreeningSubmit(event) {
        event.preventDefault();
        
        try {
            showLoading(true);
            
            const movieId = document.getElementById('screening-movie-select').value;
            const auditoriumId = document.getElementById('screening-auditorium-select').value;
            const date = document.getElementById('screening-date-input').value;
            const time = document.getElementById('screening-time-select').value;
            const price = parseFloat(document.getElementById('screening-price-input').value);
            
            // Validaciones
            if (!movieId || !auditoriumId || !date || !time || !price) {
                alert('Por favor complete todos los campos');
                return;
            }
            
            const movie = this.movies.find(m => m.mov_id === movieId);
            const auditorium = this.auditoriums.find(a => a.aud_id === auditoriumId);
            
            // Preparar datos en el formato que espera la API (fecha y hora separadas)
            const screeningData = {
                scr_mov_id: movieId,
                scr_aud_id: auditoriumId,
                scr_date: date,
                scr_time: `${time}:00`,
                scr_price: price,
                scr_status: 'scheduled'
            };
            
            // Debug logging
            console.log('=== SENDING SCREENING DATA ===');
            console.log('URL:', `${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.SCREENINGS}`);
            console.log('Data:', JSON.stringify(screeningData, null, 2));
            console.log('Movie found:', movie ? movie.mov_title : 'NOT FOUND');
            console.log('Auditorium found:', auditorium ? auditorium.aud_name : 'NOT FOUND');
            
            let result;
            if (this.editingScreening) {
                // Actualizar función existente
                console.log('Updating existing screening:', this.editingScreening.scr_id);
                result = await API.screenings.update(this.editingScreening.scr_id, screeningData);
            } else {
                // Crear nueva función
                console.log('Creating new screening...');
                result = await API.screenings.create(screeningData);
            }
            
            console.log('✅ API Response:', result);
            
            // Recargar datos desde la API
            await this.loadScreeningsFromAPI();
            this.renderScreenings();
            this.closeModal();
            
            const action = this.editingScreening ? 'actualizada' : 'programada';
            alert(`Función ${action} exitosamente`);
            log('Screening saved successfully', 'info', result);
            
        } catch (error) {
            console.error('❌ SCREENING CREATION ERROR:', error);
            console.error('Error details:', {
                message: error.message,
                stack: error.stack,
                response: error.response || 'No response data'
            });
            
            log('Error saving screening', 'error', error);
            alert(`Error al guardar la función: ${error.message}`);
        } finally {
            showLoading(false);
        }
    }

    async deleteScreening(screeningId) {
        const screening = this.screenings.find(s => s.scr_id === screeningId);
        if (!screening) return;
        
        if (confirm(`¿Está seguro de eliminar la función de "${screening.movie_title}" en ${screening.auditorium_name}?`)) {
            try {
                showLoading(true);
                
                await API.screenings.delete(screeningId);
                
                // Recargar datos desde la API
                await this.loadScreeningsFromAPI();
                this.renderScreenings();
                alert('Función eliminada exitosamente');
                log('Screening deleted successfully', 'info', { screeningId });
            } catch (error) {
                log('Error deleting screening', 'error', error);
                alert(`Error al eliminar la función: ${error.message}`);
            } finally {
                showLoading(false);
            }
        }
    }

    closeModal() {
        closeScreeningModal();
    }

    // Método para cargar datos cuando se navega a la página
    async loadData() {
        await this.loadInitialData();
    }
}

// Crear instancia global de manera segura
try {
    window.Screenings = new Screenings();
    console.log('✅ Componente Screenings cargado exitosamente');
} catch (error) {
    console.error('❌ Error cargando componente Screenings:', error);
    
    // Crear un objeto mock básico para evitar errores
    window.Screenings = {
        loadData: function() {
            console.error('Screenings component failed to load');
            return Promise.resolve();
        },
        movies: [],
        auditoriums: [],
        screenings: []
    };
}
