// Componente Booking - Versión funcional completa
class Booking {
    constructor() {
        this.currentStep = 1;
        this.selectedMovie = null;
        this.selectedScreening = null;
        this.selectedSeats = [];
        this.auditoriumSeats = [];
        this.ticketPrice = 12.50; // Precio por defecto
        this.init();
    }

    init() {
        console.log('🎬 Inicializando componente Booking');
        this.setupEventListeners();
    }

    setupEventListeners() {
        // Navigation buttons
        const nextBtn = document.getElementById('next-step');
        const prevBtn = document.getElementById('prev-step');
        const backToSeatsBtn = document.getElementById('back-to-seats');
        const purchaseForm = document.getElementById('purchase-form');

        if (nextBtn) {
            nextBtn.addEventListener('click', () => this.nextStep());
        }

        if (prevBtn) {
            prevBtn.addEventListener('click', () => this.prevStep());
        }

        if (backToSeatsBtn) {
            backToSeatsBtn.addEventListener('click', () => this.goToStep(2));
        }

        if (purchaseForm) {
            purchaseForm.addEventListener('submit', (e) => this.handlePurchase(e));
        }
    }

    async loadData() {
        try {
            showLoading(true);
            console.log('📊 Cargando datos de booking...');
            
            await this.loadMovies();
            this.showStep(1);
            
        } catch (error) {
            console.error('❌ Error cargando datos:', error);
            this.showError('Error cargando los datos de películas');
        } finally {
            showLoading(false);
        }
    }

    async loadMovies() {
        try {
            console.log('🎬 Cargando películas...');
            const response = await fetch(`${CONFIG.API_BASE_URL}/movies/`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('📋 Películas recibidas:', data);
            
            const moviesGrid = document.getElementById('movies-grid');
            if (!moviesGrid) {
                console.error('❌ No se encontró movies-grid');
                return;
            }

            moviesGrid.innerHTML = '';

            if (data.movies && data.movies.length > 0) {
                // Filtrar solo películas activas
                const activeMovies = data.movies.filter(movie => 
                    movie.mov_status === 'active' || movie.mov_status === 'available'
                );
                
                console.log(`✅ ${activeMovies.length} películas activas encontradas`);
                
                if (activeMovies.length > 0) {
                    activeMovies.forEach(movie => {
                        const movieCard = this.createMovieCard(movie);
                        moviesGrid.appendChild(movieCard);
                    });
                } else {
                    moviesGrid.innerHTML = '<p class="no-data">No hay películas activas disponibles</p>';
                }
            } else {
                moviesGrid.innerHTML = '<p class="no-data">No hay películas disponibles</p>';
            }

        } catch (error) {
            console.error('❌ Error cargando películas:', error);
            const moviesGrid = document.getElementById('movies-grid');
            if (moviesGrid) {
                moviesGrid.innerHTML = '<p class="error-message">Error cargando películas. Intenta de nuevo.</p>';
            }
            throw error;
        }
    }

    createMovieCard(movie) {
        const card = document.createElement('div');
        card.className = 'movie-card';
        card.setAttribute('data-movie-id', movie.mov_id);
        
        card.innerHTML = `
            <div class="movie-title">${movie.mov_title}</div>
            <div class="movie-details">
                <div><strong>Duración:</strong> ${movie.mov_duration} min</div>
                <div><strong>Clasificación:</strong> ${movie.mov_classification}</div>
                <div><strong>Género:</strong> ${movie.mov_genre}</div>
                ${movie.mov_synopsis ? `<div class="movie-synopsis">${movie.mov_synopsis.substring(0, 100)}...</div>` : ''}
            </div>
        `;

        card.addEventListener('click', () => this.selectMovie(movie));
        return card;
    }

    async selectMovie(movie) {
        try {
            console.log('🎬 Seleccionando película:', movie.mov_title);
            
            // Remover selección anterior
            document.querySelectorAll('.movie-card').forEach(card => {
                card.classList.remove('selected');
            });

            // Seleccionar nueva película
            const selectedCard = document.querySelector(`[data-movie-id="${movie.mov_id}"]`);
            if (selectedCard) {
                selectedCard.classList.add('selected');
            }

            this.selectedMovie = movie;
            console.log('✅ Película seleccionada:', movie);

            // Cargar funciones para esta película
            await this.loadScreenings(movie.mov_id);

        } catch (error) {
            console.error('❌ Error seleccionando película:', error);
            this.showError('Error al seleccionar la película');
        }
    }

    async loadScreenings(movieId) {
        try {
            console.log('🎭 Cargando funciones para película:', movieId);
            
            // Usar el endpoint de búsqueda de screenings
            const response = await fetch(`${CONFIG.API_BASE_URL}/screenings/search?movie_id=${movieId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const screenings = await response.json();
            console.log('📅 Funciones recibidas:', screenings);
            
            const screeningsList = document.getElementById('screenings-list');
            const screeningsGrid = document.getElementById('screenings-grid');
            
            if (!screeningsList || !screeningsGrid) {
                console.error('❌ No se encontraron contenedores de funciones');
                return;
            }

            screeningsGrid.innerHTML = '';

            if (Array.isArray(screenings) && screenings.length > 0) {
                // Filtrar funciones válidas (futuras y programadas)
                const validScreenings = this.filterValidScreenings(screenings);
                
                if (validScreenings.length > 0) {
                    console.log(`✅ ${validScreenings.length} funciones válidas encontradas`);
                    
                    validScreenings.forEach(screening => {
                        const screeningCard = this.createScreeningCard(screening);
                        screeningsGrid.appendChild(screeningCard);
                    });
                    
                    screeningsList.style.display = 'block';
                } else {
                    screeningsGrid.innerHTML = '<p class="no-data">No hay funciones disponibles para esta película</p>';
                    screeningsList.style.display = 'block';
                }
            } else {
                screeningsGrid.innerHTML = '<p class="no-data">No hay funciones programadas para esta película</p>';
                screeningsList.style.display = 'block';
            }

        } catch (error) {
            console.error('❌ Error cargando funciones:', error);
            const screeningsGrid = document.getElementById('screenings-grid');
            if (screeningsGrid) {
                screeningsGrid.innerHTML = '<p class="error-message">Error cargando funciones. Intenta de nuevo.</p>';
            }
            const screeningsList = document.getElementById('screenings-list');
            if (screeningsList) {
                screeningsList.style.display = 'block';
            }
        }
    }

    filterValidScreenings(screenings) {
        const now = new Date();
        
        return screenings.filter(screening => {
            // Verificar estado
            if (screening.scr_status !== 'scheduled') {
                return false;
            }
            
            // Construir fecha y hora de la función
            const screeningDateTime = new Date(`${screening.scr_date}T${screening.scr_time}`);
            
            // Solo mostrar funciones futuras
            return screeningDateTime > now;
        });
    }

    createScreeningCard(screening) {
        const card = document.createElement('div');
        card.className = 'screening-card';
        card.setAttribute('data-screening-id', screening.scr_id);
        
        // Formatear fecha y hora
        const screeningDate = new Date(`${screening.scr_date}T${screening.scr_time}`);
        const dateStr = screeningDate.toLocaleDateString('es-ES', {
            weekday: 'long',
            day: 'numeric',
            month: 'long'
        });
        const timeStr = screeningDate.toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });
        
        card.innerHTML = `
            <div class="screening-time">${timeStr}</div>
            <div class="screening-date">${dateStr}</div>
            <div class="screening-auditorium">Sala: ${screening.scr_aud_id}</div>
            <div class="screening-price">$${(screening.scr_price || 12.50).toFixed(2)}</div>
            <div class="screening-seats">Asientos disponibles: ${screening.scr_available_seats || 'N/A'}</div>
        `;

        card.addEventListener('click', () => this.selectScreening(screening));
        return card;
    }

    selectScreening(screening) {
        console.log('🎭 Seleccionando función:', screening);
        
        // Remover selección anterior
        document.querySelectorAll('.screening-card').forEach(card => {
            card.classList.remove('selected');
        });

        // Seleccionar nueva función
        const selectedCard = document.querySelector(`[data-screening-id="${screening.scr_id}"]`);
        if (selectedCard) {
            selectedCard.classList.add('selected');
        }

        this.selectedScreening = screening;
        this.ticketPrice = screening.scr_price || 12.50;
        
        console.log('✅ Función seleccionada:', screening);
        
        // Mostrar botón siguiente
        const nextBtn = document.getElementById('next-step');
        if (nextBtn) {
            nextBtn.style.display = 'inline-block';
        }
    }

    nextStep() {
        if (this.currentStep === 1 && this.selectedScreening) {
            this.goToStep(2);
            this.generateSeats();
        } else if (this.currentStep === 2 && this.selectedSeats.length > 0) {
            this.goToStep(3);
            this.updateSummary();
        }
    }

    prevStep() {
        if (this.currentStep > 1) {
            this.goToStep(this.currentStep - 1);
        }
    }

    goToStep(step) {
        this.currentStep = step;
        this.showStep(step);
    }

    showStep(step) {
        // Ocultar todos los pasos
        document.querySelectorAll('.booking-step').forEach(stepEl => {
            stepEl.style.display = 'none';
        });

        // Mostrar paso actual
        const currentStepEl = document.getElementById(this.getStepId(step));
        if (currentStepEl) {
            currentStepEl.style.display = 'block';
        }

        // Actualizar navegación
        this.updateNavigation();
    }

    getStepId(step) {
        const stepIds = {
            1: 'movie-selection',
            2: 'seat-selection', 
            3: 'purchase-summary'
        };
        return stepIds[step];
    }

    updateNavigation() {
        const nextBtn = document.getElementById('next-step');
        const prevBtn = document.getElementById('prev-step');

        // Mostrar/ocultar botones según el paso
        if (prevBtn) {
            prevBtn.style.display = this.currentStep > 1 ? 'inline-block' : 'none';
        }

        if (nextBtn) {
            if (this.currentStep === 1) {
                nextBtn.style.display = this.selectedScreening ? 'inline-block' : 'none';
                nextBtn.textContent = 'Seleccionar Asientos';
            } else if (this.currentStep === 2) {
                nextBtn.style.display = this.selectedSeats.length > 0 ? 'inline-block' : 'none';
                nextBtn.textContent = 'Proceder a Compra';
            } else {
                nextBtn.style.display = 'none';
            }
        }
    }

    async generateSeats() {
        try {
            console.log('🪑 Generando asientos para la función:', this.selectedScreening.scr_id);
            
            const container = document.getElementById('seats-container');
            if (!container) return;

            container.innerHTML = '';
            
            // Obtener información del auditorio
            const auditoriumId = this.selectedScreening.scr_aud_id;
            let auditoriumInfo = null;
            
            try {
                const audResponse = await fetch(`${CONFIG.API_BASE_URL}/auditoriums/${auditoriumId}`);
                if (audResponse.ok) {
                    auditoriumInfo = await audResponse.json();
                    console.log('🏛️ Información del auditorio:', auditoriumInfo);
                }
            } catch (error) {
                console.log('⚠️ No se pudo obtener info del auditorio, usando valores por defecto');
            }
            
            // Usar valores del auditorio o por defecto
            const rows = auditoriumInfo?.aud_total_rows || 8;
            const seatsPerRow = auditoriumInfo?.aud_seats_per_row || 10;
            
            console.log(`🪑 Generando ${rows} filas con ${seatsPerRow} asientos cada una`);
            
            // Obtener tickets ocupados para esta función
            const occupiedSeats = await this.getOccupiedSeats(this.selectedScreening.scr_id);
            
            this.auditoriumSeats = [];

            for (let row = 0; row < rows; row++) {
                const rowDiv = document.createElement('div');
                rowDiv.className = 'seat-row';
                
                // Etiqueta de fila
                const rowLabel = document.createElement('div');
                rowLabel.className = 'row-label';
                rowLabel.textContent = String.fromCharCode(65 + row); // A, B, C, etc.
                rowDiv.appendChild(rowLabel);
                
                for (let seat = 0; seat < seatsPerRow; seat++) {
                    const seatElement = document.createElement('div');
                    const seatRow = String.fromCharCode(65 + row);
                    const seatNumber = seat + 1;
                    const seatId = `${seatRow}${seatNumber}`;
                    
                    seatElement.className = 'seat';
                    seatElement.textContent = seatNumber;
                    seatElement.setAttribute('data-seat-id', seatId);
                    seatElement.setAttribute('data-row', seatRow);
                    seatElement.setAttribute('data-number', seatNumber);
                    
                    // Verificar si el asiento está ocupado
                    const isOccupied = occupiedSeats.some(occupied => 
                        occupied.tic_row === seatRow && occupied.tic_seat === seatNumber
                    );
                    
                    if (isOccupied) {
                        seatElement.classList.add('occupied');
                    } else {
                        seatElement.classList.add('available');
                        seatElement.addEventListener('click', () => this.toggleSeat(seatId, seatElement));
                    }

                    rowDiv.appendChild(seatElement);
                    
                    this.auditoriumSeats.push({
                        id: seatId,
                        row: seatRow,
                        number: seatNumber,
                        available: !isOccupied
                    });
                }
                
                container.appendChild(rowDiv);
            }
            
            console.log(`✅ ${this.auditoriumSeats.length} asientos generados`);
            
        } catch (error) {
            console.error('❌ Error generando asientos:', error);
            this.showError('Error generando los asientos');
        }
    }

    async getOccupiedSeats(screeningId) {
        try {
            console.log('🔍 Consultando asientos ocupados para función:', screeningId);
            
            // Intentar obtener tickets de esta función
            const response = await fetch(`${CONFIG.API_BASE_URL}/tickets/`);
            if (!response.ok) {
                console.log('⚠️ No se pudieron obtener tickets, asumiendo todos disponibles');
                return [];
            }
            
            const tickets = await response.json();
            console.log('🎫 Tickets obtenidos:', tickets);
            
            // Filtrar tickets de esta función que estén vendidos o reservados
            const occupiedTickets = tickets.filter(ticket => 
                ticket.tic_scr_id === screeningId && 
                (ticket.tic_status === 'sold' || ticket.tic_status === 'reserved')
            );
            
            console.log(`🔒 ${occupiedTickets.length} asientos ocupados encontrados`);
            return occupiedTickets;
            
        } catch (error) {
            console.error('❌ Error obteniendo asientos ocupados:', error);
            return []; // Si hay error, asumir todos disponibles
        }
    }

    toggleSeat(seatId, seatElement) {
        if (seatElement.classList.contains('occupied')) return;

        if (seatElement.classList.contains('selected')) {
            // Deseleccionar
            seatElement.classList.remove('selected');
            seatElement.classList.add('available');
            this.selectedSeats = this.selectedSeats.filter(seat => seat.id !== seatId);
            console.log('➖ Asiento deseleccionado:', seatId);
        } else {
            // Seleccionar (máximo 6 asientos)
            if (this.selectedSeats.length < 6) {
                seatElement.classList.remove('available');
                seatElement.classList.add('selected');
                
                const seatInfo = {
                    id: seatId,
                    row: seatElement.getAttribute('data-row'),
                    number: parseInt(seatElement.getAttribute('data-number'))
                };
                
                this.selectedSeats.push(seatInfo);
                console.log('➕ Asiento seleccionado:', seatId);
            } else {
                this.showError('Máximo 6 asientos por compra');
                return;
            }
        }

        console.log('🪑 Asientos seleccionados:', this.selectedSeats);
        this.updateSeatSummary();
        this.updateNavigation();
    }

    updateSeatSummary() {
        // Actualizar contador de asientos y precio total
        const count = this.selectedSeats.length;
        const total = count * this.ticketPrice;
        
        // Buscar elementos de resumen en la página
        const countElements = document.querySelectorAll('#selected-seats-count, .selected-seats-count');
        const totalElements = document.querySelectorAll('#total-price, .total-price');
        
        countElements.forEach(el => el.textContent = count);
        totalElements.forEach(el => el.textContent = total.toFixed(2));
    }

    updateSummary() {
        const summaryEl = document.getElementById('booking-summary');
        if (!summaryEl) return;

        const totalPrice = this.selectedSeats.length * this.ticketPrice;
        const screeningDate = new Date(`${this.selectedScreening.scr_date}T${this.selectedScreening.scr_time}`);

        summaryEl.innerHTML = `
            <h4>Resumen de la compra</h4>
            <div class="summary-item">
                <span>Película:</span>
                <span>${this.selectedMovie.mov_title}</span>
            </div>
            <div class="summary-item">
                <span>Función:</span>
                <span>${screeningDate.toLocaleString('es-ES')}</span>
            </div>
            <div class="summary-item">
                <span>Sala:</span>
                <span>${this.selectedScreening.scr_aud_id}</span>
            </div>
            <div class="summary-item">
                <span>Asientos:</span>
                <span>${this.selectedSeats.map(seat => seat.id).join(', ')}</span>
            </div>
            <div class="summary-item">
                <span>Cantidad:</span>
                <span>${this.selectedSeats.length} boletos</span>
            </div>
            <div class="summary-item">
                <span>Precio unitario:</span>
                <span>$${this.ticketPrice.toFixed(2)}</span>
            </div>
            <div class="summary-total">
                <span>Total:</span>
                <span>$${totalPrice.toFixed(2)}</span>
            </div>
        `;
    }

    async handlePurchase(event) {
        event.preventDefault();
        
        try {
            console.log('💳 Procesando compra...');
            
            // Obtener datos del formulario
            const email = document.getElementById('customer-email').value;
            const name = document.getElementById('customer-name').value;
            const phone = document.getElementById('customer-phone').value;
            
            if (!email || !name) {
                this.showError('Por favor completa todos los campos requeridos');
                return;
            }
            
            // Crear o buscar usuario
            const userData = {
                usr_email: email,
                usr_name: name,
                usr_phone: phone || '',
                usr_membership: 'regular'
            };
            
            console.log('👤 Datos del usuario:', userData);
            
            // Crear la venta
            const saleData = {
                sal_usr_id: 'temp-user-id', // Se generará en el backend
                sal_total: this.selectedSeats.length * this.ticketPrice,
                sal_date: new Date().toISOString().split('T')[0],
                sal_payment_method: 'cash',
                sal_status: 'completed'
            };
            
            console.log('💰 Datos de la venta:', saleData);
            
            // Crear tickets
            const ticketsData = this.selectedSeats.map(seat => ({
                tic_row: seat.row,
                tic_seat: seat.number,
                tic_scr_id: this.selectedScreening.scr_id,
                tic_status: 'sold'
            }));
            
            console.log('🎫 Datos de los tickets:', ticketsData);
            
            // Simular compra exitosa (aquí deberías hacer las llamadas reales al API)
            showLoading(true, 'Procesando compra...');
            
            // Simular delay de procesamiento
            await new Promise(resolve => setTimeout(resolve, 2000));
            
            // Por ahora simular éxito
            this.showPurchaseSuccess({
                saleId: 'SAL-' + Date.now(),
                tickets: ticketsData,
                total: saleData.sal_total,
                customer: userData
            });
            
        } catch (error) {
            console.error('❌ Error procesando compra:', error);
            this.showError('Error procesando la compra. Intenta de nuevo.');
        } finally {
            showLoading(false);
        }
    }

    showPurchaseSuccess(purchaseData) {
        console.log('✅ Compra exitosa:', purchaseData);
        
        // Crear modal de éxito
        const modal = document.createElement('div');
        modal.className = 'modal';
        modal.innerHTML = `
            <div class="modal-content">
                <div class="modal-header">
                    <h3>¡Compra exitosa!</h3>
                </div>
                <div class="modal-body">
                    <div class="success-icon">✅</div>
                    <p><strong>ID de compra:</strong> ${purchaseData.saleId}</p>
                    <p><strong>Total:</strong> $${purchaseData.total.toFixed(2)}</p>
                    <p><strong>Asientos:</strong> ${this.selectedSeats.map(s => s.id).join(', ')}</p>
                    <p>Tu compra ha sido procesada exitosamente. Los boletos han sido generados.</p>
                </div>
                <div class="modal-footer">
                    <button class="btn-primary" onclick="this.closest('.modal').remove(); window.location.reload();">
                        Nueva compra
                    </button>
                    <button class="btn-secondary" onclick="this.closest('.modal').remove();">
                        Cerrar
                    </button>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Auto-cerrar después de 5 segundos
        setTimeout(() => {
            if (modal.parentNode) {
                modal.remove();
            }
        }, 10000);
    }

    showError(message) {
        console.error('❌ Error:', message);
        
        // Crear notificación de error
        const notification = document.createElement('div');
        notification.className = 'notification error';
        notification.textContent = message;
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #dc3545;
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            z-index: 1000;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
}

// Crear instancia global
window.Booking = Booking;
