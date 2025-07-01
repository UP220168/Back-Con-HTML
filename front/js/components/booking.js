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
            showLoading(true);
            log('Loading booking data...');
            
            await this.loadMovies();
            this.showStep(1);
            
        } catch (error) {
            log('Error loading booking data', 'error', error);
            this.showError('Error cargando los datos de películas');
        } finally {
            showLoading(false);
        }
    }

    async loadMovies() {
        try {
            // Obtener películas desde la API
            const response = await fetch(`${CONFIG.API_BASE_URL}/movies`);
            const data = await response.json();
            
            log('Movies loaded:', 'info', data);
            
            const moviesGrid = document.getElementById('movies-grid');
            if (!moviesGrid) return;

            moviesGrid.innerHTML = '';

            if (data.movies && data.movies.length > 0) {
                data.movies.forEach(movie => {
                    const movieCard = this.createMovieCard(movie);
                    moviesGrid.appendChild(movieCard);
                });
            } else {
                moviesGrid.innerHTML = '<p>No hay películas disponibles</p>';
            }

        } catch (error) {
            log('Error loading movies', 'error', error);
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
            log('Movie selected:', 'info', movie);

            // Cargar funciones para esta película
            await this.loadScreenings(movie.mov_id);

        } catch (error) {
            log('Error selecting movie', 'error', error);
        }
    }

    async loadScreenings(movieId) {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/screenings?movie_id=${movieId}`);
            const data = await response.json();
            
            log('Screenings loaded:', 'info', data);

            const screeningsList = document.getElementById('screenings-list');
            const screeningsGrid = document.getElementById('screenings-grid');
            
            if (!screeningsList || !screeningsGrid) return;

            screeningsGrid.innerHTML = '';

            if (data.screenings && data.screenings.length > 0) {
                data.screenings.forEach(screening => {
                    const screeningCard = this.createScreeningCard(screening);
                    screeningsGrid.appendChild(screeningCard);
                });
                screeningsList.style.display = 'block';
                
                // Mostrar botón siguiente
                document.getElementById('next-step').style.display = 'inline-block';
            } else {
                screeningsGrid.innerHTML = '<p>No hay funciones disponibles para esta película</p>';
                screeningsList.style.display = 'block';
            }

        } catch (error) {
            log('Error loading screenings', 'error', error);
        }
    }

    createScreeningCard(screening) {
        const card = document.createElement('div');
        card.className = 'screening-card';
        card.setAttribute('data-screening-id', screening.scr_id);
        
        // Formatear fecha y hora
        const date = new Date(screening.scr_start_time);
        const dateStr = date.toLocaleDateString();
        const timeStr = date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        card.innerHTML = `
            <div class="screening-time">${timeStr}</div>
            <div class="screening-date">${dateStr}</div>
            <div class="screening-auditorium">Sala: ${screening.aud_name || 'N/A'}</div>
            <div class="screening-price">$${(screening.scr_ticket_price || 12.5).toFixed(2)}</div>
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
        log('Screening selected:', 'info', screening);
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

    generateSeats() {
        const container = document.getElementById('seats-container');
        if (!container) return;

        container.innerHTML = '';
        
        // Generar matriz de asientos (10x10 por ejemplo)
        const rows = 10;
        const seatsPerRow = 10;
        
        this.auditoriumSeats = [];

        for (let row = 0; row < rows; row++) {
            for (let seat = 0; seat < seatsPerRow; seat++) {
                const seatElement = document.createElement('div');
                const seatId = `${String.fromCharCode(65 + row)}${seat + 1}`;
                
                seatElement.className = 'seat available';
                seatElement.textContent = seatId;
                seatElement.setAttribute('data-seat-id', seatId);
                
                // Simular algunos asientos ocupados (aleatorio)
                if (Math.random() < 0.15) {
                    seatElement.className = 'seat occupied';
                } else {
                    seatElement.addEventListener('click', () => this.toggleSeat(seatId, seatElement));
                }

                container.appendChild(seatElement);
                
                this.auditoriumSeats.push({
                    id: seatId,
                    row: String.fromCharCode(65 + row),
                    number: seat + 1,
                    available: !seatElement.classList.contains('occupied')
                });
            }
        }
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

        log('Selected seats:', 'info', this.selectedSeats);
        this.updateNavigation();
    }

    updateSummary() {
        const summaryEl = document.getElementById('booking-summary');
        if (!summaryEl) return;

        const ticketPrice = this.selectedScreening.scr_ticket_price || 12.5;
        const totalPrice = this.selectedSeats.length * ticketPrice;

        summaryEl.innerHTML = `
            <h4>Resumen de la compra</h4>
            <div class="summary-item">
                <span>Película:</span>
                <span>${this.selectedMovie.mov_title}</span>
            </div>
            <div class="summary-item">
                <span>Función:</span>
                <span>${new Date(this.selectedScreening.scr_start_time).toLocaleString()}</span>
            </div>
            <div class="summary-item">
                <span>Sala:</span>
                <span>${this.selectedScreening.aud_name || 'N/A'}</span>
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
                total_amount: this.selectedSeats.length * (this.selectedScreening.scr_ticket_price || 12.5)
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
                const fecha = new Date(this.selectedScreening.scr_start_time);
                const fechaStr = fecha.toLocaleDateString('es-MX');
                const horaStr = fecha.toLocaleTimeString('es-MX', {hour: '2-digit', minute:'2-digit'});
                
                doc.text(`Función: ${fechaStr} a las ${horaStr}`, marginLeft, currentY);
                currentY += 8;
                doc.text(`Sala: ${this.selectedScreening.aud_name || 'N/A'}`, marginLeft, currentY);
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
}

// Crear instancia global
window.Booking = new Booking();

// Auto-cargar datos cuando se navega a booking
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.hash === '#booking') {
        window.Booking.loadData();
    }
});
