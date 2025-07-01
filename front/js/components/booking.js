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
            const response = await fetch(`${CONFIG.API_BASE_URL}/movies/`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
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

            // Cargar funciones para esta película
            await this.loadScreenings(movie.mov_id);

        } catch (error) {
            console.error('❌ Error seleccionando película:', error);
        }
    }

    async loadScreenings(movieId) {
        try {
            
            // Usar el endpoint de búsqueda de screenings
            const response = await fetch(`${CONFIG.API_BASE_URL}/screenings/search?movie_id=${movieId}`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const screenings = await response.json();

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
                
                
                // Filtrar funciones válidas (futuras y programadas)
                const validScreenings = movieScreenings.filter(screening => {
                    const screeningDate = new Date(`${screening.scr_date}T${screening.scr_time}`);
                    const now = new Date();
                    return screeningDate > now && screening.scr_status === 'scheduled';
                });
                
                if (validScreenings.length > 0) {
                    
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

            // Validar campos requeridos
            if (!customerEmail || !customerName) {
                throw new Error('Por favor complete todos los campos requeridos (nombre y email)');
            }

            if (this.selectedSeats.length === 0) {
                throw new Error('Por favor seleccione al menos un asiento');
            }

            // Crear la compra completa con tickets y venta usando el endpoint especializado
            const purchaseData = {
                customer_email: customerEmail,
                customer_name: customerName,
                customer_phone: customerPhone || '',
                scr_id: this.selectedScreening.scr_id,
                seats: this.selectedSeats.map(seat => seat.id),
                payment_method: "cash", // Por defecto efectivo
                total_amount: this.selectedSeats.length * (this.selectedScreening.scr_price || 12.5)
            };


            // Usar el endpoint especializado para compra simplificada
            const response = await fetch(`${CONFIG.API_BASE_URL}/sales/purchase-simple`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(purchaseData)
            });

            if (response.ok) {
                const result = await response.json();
                
                // Generar PDF del boleto con los datos de la compra
                this.generateTicketPDF(purchaseData, result);
                
                // Mostrar mensaje de éxito con detalles
                this.showSuccessMessage(result);
                
                // Resetear el formulario y volver al inicio
                setTimeout(() => {
                    this.resetBooking();
                }, 3000);
                
            } else {
                const errorData = await response.json();
                console.error('❌ Error en la compra:', errorData);
                throw new Error(errorData.detail || 'Error procesando la compra');
            }

        } catch (error) {
            console.error('❌ Error procesando compra:', error);
            alert(`Error al procesar la compra: ${error.message}\nPor favor intente de nuevo.`);
        } finally {
            showLoading(false);
        }
    }

    showSuccessMessage(result) {
        const saleId = result?.sale_id || 'N/A';
        const ticketCount = result?.ticket_ids?.length || this.selectedSeats.length;
        const ticketIds = result?.ticket_ids || [];
        
        // Crear un mensaje más detallado
        let message = `¡Compra realizada exitosamente! 🎬\n\n`;
        message += `🎪 ¡Disfrute la función!`;

        alert(message);
    }

    // Métodos de descarga del backend removidos - ahora se genera PDF en frontend

    generateTicketPDF(purchaseData, result = null) {
        try {
            // Verificar que jsPDF esté disponible (UMD build)
            if (typeof window.jspdf === 'undefined' || typeof window.jspdf.jsPDF === 'undefined') {
                console.error('❌ jsPDF no está cargado');
                alert('Error: No se puede generar el PDF. Biblioteca jsPDF no disponible.');
                return;
            }

            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();

            // Configuración del documento (súper compacto)
            const pageWidth = doc.internal.pageSize.getWidth();
            const pageHeight = doc.internal.pageSize.getHeight();
            const marginLeft = 10;
            const marginRight = 10;
            const contentWidth = pageWidth - marginLeft - marginRight;
            let currentY = 15;

            // Header del boleto (compacto)
            doc.setFontSize(16);
            doc.setTextColor(40, 40, 40);
            doc.text('Cinema el Foráneo', marginLeft, currentY);
            
            currentY += 8;
            doc.setFontSize(12);
            doc.setTextColor(60, 60, 60);
            doc.text('BOLETO DE ENTRADA', marginLeft, currentY);

            // Línea separadora
            currentY += 5;
            doc.setLineWidth(0.3);
            doc.setDrawColor(100, 100, 100);
            doc.line(marginLeft, currentY, pageWidth - marginRight, currentY);

            // Información de la compra (súper compacto)
            currentY += 8;
            doc.setFontSize(8);
            doc.setTextColor(80, 80, 80);
            
            if (result && result.sale_id) {
                doc.text(`ID Venta: ${result.sale_id}`, marginLeft, currentY);
                currentY += 4;
            }
            
            const now = new Date();
            doc.text(`Compra: ${now.toLocaleDateString('es-ES')} ${now.toLocaleTimeString('es-ES')}`, marginLeft, currentY);
            currentY += 6;

            // Información de la película y función
            doc.setFontSize(12);
            doc.setTextColor(40, 40, 40);
            doc.text('FUNCIÓN', marginLeft, currentY);
            currentY += 8;

            doc.setFontSize(9);
            doc.setTextColor(60, 60, 60);
            
            // Película
            if (this.selectedMovie) {
                doc.text(`Película: ${this.selectedMovie.mov_title}`, marginLeft, currentY);
                currentY += 5;
                doc.text(`Género: ${this.selectedMovie.mov_genre || 'N/A'}`, marginLeft, currentY);
                currentY += 5;
                doc.text(`Duración: ${this.selectedMovie.mov_duration || 'N/A'} min | ${this.selectedMovie.mov_classification || 'N/A'}`, marginLeft, currentY);
                currentY += 7;
            }

            // Función y sala
            if (this.selectedScreening) {
                const screeningDate = new Date(`${this.selectedScreening.scr_date}T${this.selectedScreening.scr_time}`);
                const fechaStr = screeningDate.toLocaleDateString('es-ES', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric'
                });
                const horaStr = screeningDate.toLocaleTimeString('es-ES', {
                    hour: '2-digit',
                    minute: '2-digit'
                });

                doc.text(`Fecha: ${fechaStr} | Hora: ${horaStr}`, marginLeft, currentY);
                currentY += 5;
                doc.text(`Sala: ${this.getAuditoriumName(this.selectedScreening.scr_aud_id)}`, marginLeft, currentY);
                currentY += 8;
            }

            // Información del cliente
            doc.setFontSize(12);
            doc.setTextColor(40, 40, 40);
            doc.text('CLIENTE', marginLeft, currentY);
            currentY += 8;

            doc.setFontSize(9);
            doc.setTextColor(60, 60, 60);
            doc.text(`${purchaseData.customer_name}`, marginLeft, currentY);
            currentY += 5;
            doc.text(`${purchaseData.customer_email}`, marginLeft, currentY);
            currentY += 5;
            if (purchaseData.customer_phone) {
                doc.text(`Tel: ${purchaseData.customer_phone}`, marginLeft, currentY);
                currentY += 5;
            }
            currentY += 3;

            // Información de los boletos
            doc.setFontSize(12);
            doc.setTextColor(40, 40, 40);
            doc.text('BOLETOS', marginLeft, currentY);
            currentY += 8;

            doc.setFontSize(9);
            doc.setTextColor(60, 60, 60);
            
            const seats = this.selectedSeats.map(seat => seat.id).join(', ');
            doc.text(`Asientos: ${seats}`, marginLeft, currentY);
            currentY += 5;
            doc.text(`Cantidad: ${this.selectedSeats.length} boleto(s)`, marginLeft, currentY);
            currentY += 5;

            if (result && result.ticket_ids && result.ticket_ids.length > 0) {
                const ticketIds = result.ticket_ids.length > 3 
                    ? result.ticket_ids.slice(0, 3).join(', ') + '...'
                    : result.ticket_ids.join(', ');
                doc.text(`IDs: ${ticketIds}`, marginLeft, currentY);
                currentY += 7;
            }

            // Resumen de pago
            doc.setFontSize(12);
            doc.setTextColor(40, 40, 40);
            doc.text('PAGO', marginLeft, currentY);
            currentY += 8;

            doc.setFontSize(9);
            doc.setTextColor(60, 60, 60);
            
            const unitPrice = this.selectedScreening?.scr_price || 12.5;
            doc.text(`Precio: $${unitPrice.toFixed(2)} x ${this.selectedSeats.length} | ${purchaseData.payment_method.toUpperCase()}`, marginLeft, currentY);
            currentY += 6;

            // Total con destacado
            doc.setFontSize(14);
            doc.setTextColor(40, 40, 40);
            doc.text(`TOTAL: $${purchaseData.total_amount.toFixed(2)} MXN`, marginLeft, currentY);
            currentY += 10;

            // Línea separadora
            doc.setLineWidth(0.3);
            doc.setDrawColor(100, 100, 100);
            doc.line(marginLeft, currentY, pageWidth - marginRight, currentY);
            currentY += 8;

            // Instrucciones compactas
            doc.setFontSize(10);
            doc.setTextColor(80, 80, 80);
            doc.text('INSTRUCCIONES:', marginLeft, currentY);
            currentY += 6;

            doc.setFontSize(8);
            doc.setTextColor(100, 100, 100);
            const instructions = [
                '• Presente boleto al ingresar • Llegue 15 min antes',
                '• Sin devoluciones ni cambios • Sin alimentos externos',
                '• Conserve el boleto durante la función'
            ];

            instructions.forEach(instruction => {
                doc.text(instruction, marginLeft, currentY);
                currentY += 4;
            });

            // Footer compacto
            currentY = pageHeight - 20;
            doc.setFontSize(12);
            doc.setTextColor(40, 40, 40);
            doc.text('¡DISFRUTE SU FUNCIÓN!', marginLeft, currentY);
            
            currentY += 6;
            doc.setFontSize(7);
            doc.setTextColor(120, 120, 120);
            doc.text(`${now.toLocaleDateString('es-ES')} ${now.toLocaleTimeString('es-ES')}`, marginLeft, currentY);
            doc.text('Cinema el Foráneo', pageWidth - marginRight - 25, currentY);

            // Guardar el PDF
            const fileName = `boleto_${result?.sale_id || 'compra'}_${now.getTime()}.pdf`;
            doc.save(fileName);
            
            
            // Mostrar mensaje de confirmación
            setTimeout(() => {
                alert('✅ ¡Boleto PDF generado exitosamente!\nRevise su carpeta de descargas.');
            }, 500);

        } catch (error) {
            console.error('❌ Error generando PDF:', error);
            alert(`❌ Error al generar el boleto PDF: ${error.message}\nPor favor intente de nuevo.`);
        }
    }

    async loadAuditoriums() {
        try {
            const response = await fetch(`${CONFIG.API_BASE_URL}/auditoriums/`);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            if (data.auditoriums && Array.isArray(data.auditoriums)) {
                this.auditoriums = data.auditoriums;
            } else {
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
            
            // Usar el endpoint correcto que filtra por screening_id
            const response = await fetch(`${CONFIG.API_BASE_URL}/tickets/screening/${screeningId}`);
            
            if (!response.ok) {
                console.warn(`⚠️ No se pudieron obtener tickets: ${response.status}`);
                return []; // Si no se pueden obtener, asumir que están todos disponibles
            }
            
            const data = await response.json();
            
            // Extraer números de asiento de los tickets
            const occupiedSeats = [];
            
            // La respuesta es directamente un array de tickets
            if (Array.isArray(data)) {
                data.forEach(ticket => {
                    // Solo incluir tickets vendidos
                    if (ticket.tic_status === 'sold') {
                        // Combinar tic_row y tic_seat para formar el ID del asiento (ej: "A1")
                        const seatId = `${ticket.tic_row}${ticket.tic_seat}`;
                        occupiedSeats.push(seatId);
                    }
                });
            }
            
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
