// Componente Booking
class Booking {
    constructor() {
        this.currentStep = 1;
        this.selectedMovie = null;
        this.selectedScreening = null;
        this.selectedSeats = [];
        this.auditoriumSeats = [];
        this.init();
    }

    init() {
        log('Initializing Booking component');
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
            console.log('📊 Cargando datos de booking...');
            
            // Cargar auditorios primero para tener la información de las salas
            await this.loadAuditoriums();
            await this.loadMovies();
            this.showStep(1);
            
        } catch (error) {
            console.error('❌ Error cargando datos de booking:', error);
            this.showError('Error cargando los datos de películas');
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
                <div>Duración: ${movie.mov_duration} min</div>
                <div>Clasificación: ${movie.mov_classification}</div>
                <div>Género: ${movie.mov_genre}</div>
            </div>
        `;

        card.addEventListener('click', () => this.selectMovie(movie));
        return card;
    }

    async selectMovie(movie) {
        try {
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
                // Validación adicional: solo funciones de la película seleccionada
                const movieScreenings = screenings.filter(screening => 
                    screening.scr_mov_id === movieId
                );
                
                console.log(`🔍 Validación: ${screenings.length} funciones recibidas, ${movieScreenings.length} corresponden a la película`);
                
                // Filtrar funciones válidas (futuras y programadas)
                const validScreenings = movieScreenings.filter(screening => {
                    const screeningDate = new Date(`${screening.scr_date}T${screening.scr_time}`);
                    const now = new Date();
                    return screeningDate > now && screening.scr_status === 'scheduled';
                });
                
                if (validScreenings.length > 0) {
                    console.log(`✅ ${validScreenings.length} funciones válidas encontradas para ${this.selectedMovie.mov_title}`);
                    
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
        }
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
            <div class="screening-auditorium">Sala: ${this.getAuditoriumName(screening.scr_aud_id)}</div>
            <div class="screening-price">$${(screening.scr_price || 12.5).toFixed(2)}</div>
        `;

        card.addEventListener('click', () => this.selectScreening(screening));
        return card;
    }

    selectScreening(screening) {
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
        console.log('✅ Función seleccionada:', screening);
        
        // Actualizar navegación para mostrar el botón siguiente
        this.updateNavigation();
    }

    async nextStep() {
        if (this.currentStep === 1 && this.selectedScreening) {
            this.goToStep(2);
            await this.generateSeats();
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
        const container = document.getElementById('seats-container');
        if (!container) return;

        container.innerHTML = '';
        
        // Obtener información del auditorio seleccionado
        const auditorium = this.auditoriums.find(aud => aud.aud_id === this.selectedScreening.scr_aud_id);
        
        let rows, seatsPerRow;
        if (auditorium) {
            rows = auditorium.aud_total_rows || 10;
            seatsPerRow = auditorium.aud_seats_per_row || 10;
            console.log(`🎭 Generando asientos para ${auditorium.aud_name}: ${rows}x${seatsPerRow}`);
        } else {
            // Valores por defecto si no se encuentra el auditorio
            rows = 10;
            seatsPerRow = 10;
            console.warn('⚠️ Auditorio no encontrado, usando valores por defecto');
        }
        
        this.auditoriumSeats = [];

        // Obtener asientos ocupados desde la API
        const occupiedSeats = await this.getOccupiedSeats(this.selectedScreening.scr_id);

        for (let row = 0; row < rows; row++) {
            for (let seat = 0; seat < seatsPerRow; seat++) {
                const seatElement = document.createElement('div');
                const seatId = `${String.fromCharCode(65 + row)}${seat + 1}`;
                
                seatElement.className = 'seat available';
                seatElement.textContent = seatId;
                seatElement.setAttribute('data-seat-id', seatId);
                
                // Verificar si el asiento está ocupado (desde la API, no aleatorio)
                const isOccupied = occupiedSeats.includes(seatId);
                
                if (isOccupied) {
                    seatElement.className = 'seat occupied';
                } else {
                    seatElement.addEventListener('click', () => this.toggleSeat(seatId, seatElement));
                }

                container.appendChild(seatElement);
                
                this.auditoriumSeats.push({
                    id: seatId,
                    row: String.fromCharCode(65 + row),
                    number: seat + 1,
                    available: !isOccupied
                });
            }
        }
        
        console.log(`✅ ${this.auditoriumSeats.length} asientos generados (${occupiedSeats.length} ocupados)`);
    }

    toggleSeat(seatId, seatElement) {
        if (seatElement.classList.contains('occupied')) return;

        if (seatElement.classList.contains('selected')) {
            // Deseleccionar
            seatElement.classList.remove('selected');
            seatElement.classList.add('available');
            this.selectedSeats = this.selectedSeats.filter(seat => seat.id !== seatId);
        } else {
            // Seleccionar (máximo 6 asientos)
            if (this.selectedSeats.length < 6) {
                seatElement.classList.remove('available');
                seatElement.classList.add('selected');
                this.selectedSeats.push({
                    id: seatId,
                    row: seatId.charAt(0),
                    number: parseInt(seatId.slice(1))
                });
            } else {
                alert('Máximo 6 asientos por compra');
            }
        }

        console.log('🪑 Asientos seleccionados:', this.selectedSeats);
        this.updateNavigation();
    }

    updateSummary() {
        const summaryEl = document.getElementById('booking-summary');
        if (!summaryEl) return;

        const ticketPrice = this.selectedScreening.scr_price || 12.5;
        const totalPrice = this.selectedSeats.length * ticketPrice;

        // Formatear fecha y hora correctamente
        const screeningDate = new Date(`${this.selectedScreening.scr_date}T${this.selectedScreening.scr_time}`);
        const fechaStr = screeningDate.toLocaleDateString('es-ES', {
            weekday: 'long',
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        });
        const horaStr = screeningDate.toLocaleTimeString('es-ES', {
            hour: '2-digit',
            minute: '2-digit'
        });

        summaryEl.innerHTML = `
            <h4>Resumen de la compra</h4>
            <div class="summary-item">
                <span>Película:</span>
                <span>${this.selectedMovie.mov_title}</span>
            </div>
            <div class="summary-item">
                <span>Función:</span>
                <span>${fechaStr} - ${horaStr}</span>
            </div>
            <div class="summary-item">
                <span>Sala:</span>
                <span>${this.getAuditoriumName(this.selectedScreening.scr_aud_id)}</span>
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
                <span>$${ticketPrice.toFixed(2)}</span>
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
            showLoading(true);
            
            const formData = new FormData(event.target);
            const customerEmail = formData.get('customer-email') || document.getElementById('customer-email').value;
            const customerName = formData.get('customer-name') || document.getElementById('customer-name').value;
            const customerPhone = formData.get('customer-phone') || document.getElementById('customer-phone').value;

            // Crear la compra completa con tickets y venta
            const purchaseData = {
                customer_email: customerEmail,
                customer_name: customerName,
                customer_phone: customerPhone,
                scr_id: this.selectedScreening.scr_id,
                seats: this.selectedSeats.map(seat => seat.id),
                payment_method: "cash", // Por defecto efectivo
                total_amount: this.selectedSeats.length * (this.selectedScreening.scr_price || 12.5)
            };

            log('Processing purchase:', 'info', purchaseData);

            // Llamar al endpoint de compra completa (simplificado)
            const response = await fetch(`${CONFIG.API_BASE_URL}/sales`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    customer_email: customerEmail,
                    customer_name: customerName,
                    scr_id: this.selectedScreening.scr_id,
                    total_amount: purchaseData.total_amount
                })
            });

            if (response.ok) {
                const result = await response.json();
                log('Purchase successful:', 'info', result);
                
                // Generar PDF del boleto con los datos disponibles
                this.generateTicketPDF(purchaseData);
                
                // Mostrar mensaje de éxito
                this.showSuccessMessage(result);
                
                this.resetBooking();
            } else {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error en la compra');
            }

        } catch (error) {
            log('Error processing purchase', 'error', error);
            alert('Error al procesar la compra. Por favor intente de nuevo.');
        } finally {
            showLoading(false);
        }
    }

    showSuccessMessage(result) {
        const saleId = result?.sale_id || 'N/A';
        const ticketCount = this.selectedSeats.length;
        
        alert(`¡Compra realizada exitosamente! 
        
ID de Venta: ${saleId}
Boletos generados: ${ticketCount}
        
Su boleto PDF se descargará automáticamente.`);
    }

    generateTicketPDF(purchaseData) {
        try {
            // Verificar que jsPDF esté disponible
            if (typeof window.jsPDF === 'undefined') {
                console.error('jsPDF no está cargado');
                return;
            }

            const { jsPDF } = window;
            const doc = new jsPDF();

            // Configuración del documento
            const pageWidth = doc.internal.pageSize.getWidth();
            const marginLeft = 20;
            let currentY = 30;

            // Header del boleto
            doc.setFontSize(20);
            doc.setTextColor(40, 40, 40);
            doc.text('🎬 Cinema el Foraneo', marginLeft, currentY);
            
            currentY += 15;
            doc.setFontSize(16);
            doc.text('BOLETO DE ENTRADA', marginLeft, currentY);

            // Línea separadora
            currentY += 10;
            doc.setLineWidth(0.5);
            doc.line(marginLeft, currentY, pageWidth - marginLeft, currentY);

            // Información de la película
            currentY += 20;
            doc.setFontSize(12);
            doc.setTextColor(0, 0, 0);
            
            if (this.selectedMovie) {
                doc.text(`Película: ${this.selectedMovie.mov_title}`, marginLeft, currentY);
                currentY += 8;
                doc.text(`Duración: ${this.selectedMovie.mov_duration} min`, marginLeft, currentY);
                currentY += 8;
                doc.text(`Clasificación: ${this.selectedMovie.mov_classification}`, marginLeft, currentY);
                currentY += 8;
                doc.text(`Género: ${this.selectedMovie.mov_genre}`, marginLeft, currentY);
                currentY += 12;
            }

            // Información de la función
            if (this.selectedScreening) {
                const screeningDate = new Date(`${this.selectedScreening.scr_date}T${this.selectedScreening.scr_time}`);
                const fechaStr = screeningDate.toLocaleDateString('es-MX');
                const horaStr = screeningDate.toLocaleTimeString('es-MX', {hour: '2-digit', minute:'2-digit'});
                
                doc.text(`Función: ${fechaStr} a las ${horaStr}`, marginLeft, currentY);
                currentY += 8;
                doc.text(`Sala: ${this.getAuditoriumName(this.selectedScreening.scr_aud_id)}`, marginLeft, currentY);
                currentY += 12;
            }

            // Asientos
            const asientosStr = this.selectedSeats.map(seat => seat.id).join(', ');
            doc.text(`Asientos: ${asientosStr}`, marginLeft, currentY);
            currentY += 8;
            doc.text(`Cantidad de boletos: ${this.selectedSeats.length}`, marginLeft, currentY);
            currentY += 12;

            // Información del cliente
            doc.text(`Cliente: ${purchaseData.customer_name}`, marginLeft, currentY);
            currentY += 8;
            doc.text(`Email: ${purchaseData.customer_email}`, marginLeft, currentY);
            currentY += 12;

            // Total
            doc.setFontSize(14);
            doc.setTextColor(0, 100, 0);
            doc.text(`Total: $${purchaseData.total_amount.toFixed(2)} MXN`, marginLeft, currentY);

            // Información adicional
            currentY += 20;
            doc.setFontSize(10);
            doc.setTextColor(100, 100, 100);
            doc.text(`Fecha de compra: ${new Date().toLocaleString('es-MX')}`, marginLeft, currentY);
            currentY += 6;
            doc.text(`ID único: ${Date.now()}`, marginLeft, currentY);

            // Footer
            currentY += 20;
            doc.setTextColor(60, 60, 60);
            doc.text('Conserve este boleto para ingresar a la función.', marginLeft, currentY);
            currentY += 6;
            doc.text('No se admiten devoluciones ni cambios.', marginLeft, currentY);

            // Generar nombre del archivo
            const fileName = `boleto_${this.selectedMovie?.mov_title || 'pelicula'}_${Date.now()}.pdf`;
            
            // Descargar el PDF
            doc.save(fileName);
            
            log('PDF generado exitosamente', 'info', fileName);

        } catch (error) {
            log('Error generando PDF', 'error', error);
            alert('Error al generar el boleto PDF. La compra se realizó correctamente.');
        }
    }

    async loadAuditoriums() {
        try {
            console.log('🏛️ Cargando auditorios...');
            const response = await fetch(`${CONFIG.API_BASE_URL}/auditoriums/`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('🎭 Auditorios recibidos:', data);
            
            if (data.auditoriums && Array.isArray(data.auditoriums)) {
                this.auditoriums = data.auditoriums;
                console.log(`✅ ${this.auditoriums.length} auditorios cargados`);
            } else {
                console.warn('⚠️ No se encontraron auditorios');
                this.auditoriums = [];
            }

        } catch (error) {
            console.error('❌ Error cargando auditorios:', error);
            this.auditoriums = [];
        }
    }

    getAuditoriumName(auditoriumId) {
        const auditorium = this.auditoriums.find(aud => aud.aud_id === auditoriumId);
        return auditorium ? auditorium.aud_name : `Sala ${auditoriumId}`;
    }

    resetBooking() {
        this.currentStep = 1;
        this.selectedMovie = null;
        this.selectedScreening = null;
        this.selectedSeats = [];
        this.auditoriumSeats = [];
        this.showStep(1);
        this.loadMovies();
    }

    showError(message) {
        const container = document.querySelector('.booking-container');
        if (container) {
            container.innerHTML = `
                <div class="error-message">
                    <h3>Error</h3>
                    <p>${message}</p>
                    <button class="btn-primary" onclick="window.Booking.loadData()">Reintentar</button>
                </div>
            `;
        }
    }

    async getOccupiedSeats(screeningId) {
        try {
            console.log('🎟️ Consultando asientos ocupados para función:', screeningId);
            
            // Consultar tickets vendidos para esta función
            const response = await fetch(`${CONFIG.API_BASE_URL}/tickets/?screening_id=${screeningId}`);
            
            if (!response.ok) {
                console.warn(`⚠️ No se pudieron obtener tickets: ${response.status}`);
                return []; // Si no se pueden obtener, asumir que están todos disponibles
            }
            
            const data = await response.json();
            console.log('🎫 Tickets encontrados:', data);
            
            // Extraer números de asiento de los tickets
            const occupiedSeats = [];
            if (data.tickets && Array.isArray(data.tickets)) {
                data.tickets.forEach(ticket => {
                    if (ticket.ticket_seat_number) {
                        occupiedSeats.push(ticket.ticket_seat_number);
                    }
                });
            }
            
            console.log(`🚫 ${occupiedSeats.length} asientos ocupados:`, occupiedSeats);
            return occupiedSeats;
            
        } catch (error) {
            console.error('❌ Error consultando asientos ocupados:', error);
            return []; // En caso de error, asumir que están disponibles
        }
    }
}

// Crear instancia global con manejo de errores
try {
    window.BookingClass = Booking;
    window.Booking = new Booking();
    console.log('✅ Booking component initialized successfully');
} catch (error) {
    console.error('❌ Error initializing Booking component:', error);
    window.Booking = null;
}

// Auto-cargar datos cuando se navega a booking
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.hash === '#booking' && window.Booking) {
        window.Booking.loadData();
    }
});
