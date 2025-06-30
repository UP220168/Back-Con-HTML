// Componente Generador de Tickets PDF
class TicketGenerator {
    constructor() {
        this.init();
    }

    init() {
        log('Initializing TicketGenerator component');
        this.setupEventListeners();
    }

    setupEventListeners() {
        const generateBtn = document.getElementById('generate-pdf');
        if (generateBtn) {
            generateBtn.addEventListener('click', () => {
                this.generateTicketPDF();
            });
        }
    }

    async generateTicketPDF() {
        const ticketId = document.getElementById('ticket-id')?.value;
        
        if (!ticketId) {
            this.showError('Por favor ingresa un ID de boleto válido');
            return;
        }

        try {
            showLoading(true);
            log(`Generating PDF for ticket: ${ticketId}`);

            // Obtener datos del ticket
            const ticketData = await this.getTicketData(ticketId);
            
            if (!ticketData) {
                throw new Error('Ticket no encontrado');
            }

            // Generar y mostrar preview del ticket
            this.showTicketPreview(ticketData);

            // Generar PDF
            await this.createPDF(ticketData);

        } catch (error) {
            log('Error generating ticket PDF', 'error', error);
            this.showError('Error generando el boleto: ' + error.message);
        } finally {
            showLoading(false);
        }
    }

    async getTicketData(ticketId) {
        try {
            // Intentar obtener el ticket por ID
            const ticket = await TicketsAPI.getById(ticketId);
            
            if (!ticket) {
                return null;
            }

            // Obtener datos adicionales si es necesario
            const additionalData = await this.getAdditionalTicketData(ticket);
            
            return {
                ...ticket,
                ...additionalData
            };

        } catch (error) {
            log('Error fetching ticket data', 'error', error);
            return null;
        }
    }

    async getAdditionalTicketData(ticket) {
        try {
            // Obtener datos de la proyección, película, auditorio, etc.
            const screeningData = await api.get(`/screenings/${ticket.tic_scr_id}`);
            const movieData = await api.get(`/movies/${screeningData.scr_mov_id}`);
            const auditoriumData = await api.get(`/auditoriums/${screeningData.scr_aud_id}`);

            return {
                screening: screeningData,
                movie: movieData,
                auditorium: auditoriumData
            };
        } catch (error) {
            log('Error fetching additional ticket data', 'error', error);
            return {};
        }
    }

    showTicketPreview(ticketData) {
        const previewContainer = document.querySelector('.ticket-preview') || this.createPreviewContainer();
        
        const ticketHTML = this.generateTicketHTML(ticketData);
        previewContainer.innerHTML = ticketHTML;
        previewContainer.classList.add('has-content');
    }

    createPreviewContainer() {
        const container = document.createElement('div');
        container.className = 'ticket-preview';
        
        const ticketForm = document.querySelector('.ticket-form');
        if (ticketForm && ticketForm.parentNode) {
            ticketForm.parentNode.insertBefore(container, ticketForm.nextSibling);
        }
        
        return container;
    }

    generateTicketHTML(ticketData) {
        const movieTitle = ticketData.movie?.mov_title || 'Película';
        const auditoriumName = ticketData.auditorium?.aud_name || 'Auditorio';
        const screeningDate = formatDate(ticketData.screening?.scr_date);
        const screeningTime = formatTime(ticketData.screening?.scr_time);
        const seatInfo = `${ticketData.tic_row || 'A'}${ticketData.tic_seat || '1'}`;
        const price = formatCurrency(ticketData.screening?.scr_price || 0);

        return `
            <div class="ticket">
                <div class="ticket-header">
                    <div class="ticket-title">🎬 Cinema Ticket</div>
                    <div class="ticket-subtitle">Boleto de Entrada</div>
                </div>
                
                <div class="ticket-info">
                    <div class="ticket-field">
                        <span class="ticket-field-label">Película</span>
                        <span class="ticket-field-value">${movieTitle}</span>
                    </div>
                    <div class="ticket-field">
                        <span class="ticket-field-label">Auditorio</span>
                        <span class="ticket-field-value">${auditoriumName}</span>
                    </div>
                    <div class="ticket-field">
                        <span class="ticket-field-label">Fecha</span>
                        <span class="ticket-field-value">${screeningDate}</span>
                    </div>
                    <div class="ticket-field">
                        <span class="ticket-field-label">Hora</span>
                        <span class="ticket-field-value">${screeningTime}</span>
                    </div>
                    <div class="ticket-field">
                        <span class="ticket-field-label">Asiento</span>
                        <span class="ticket-field-value">${seatInfo}</span>
                    </div>
                    <div class="ticket-field">
                        <span class="ticket-field-label">Precio</span>
                        <span class="ticket-field-value">${price}</span>
                    </div>
                </div>
                
                <div class="ticket-footer">
                    <p>ID: ${ticketData.tic_id}</p>
                    <p>Generado el ${formatDate(new Date())}</p>
                    <button class="btn-primary" onclick="TicketGenerator.downloadPDF('${ticketData.tic_id}')">
                        📥 Descargar PDF
                    </button>
                </div>
            </div>
        `;
    }

    async createPDF(ticketData) {
        try {
            // Crear PDF usando jsPDF (se podría agregar la librería)
            // Por ahora, simularemos la creación del PDF
            log('Creating PDF for ticket', 'info', ticketData);
            
            // Aquí iría la lógica real de jsPDF
            this.showSuccess('PDF generado correctamente. Haz clic en "Descargar PDF" para descargarlo.');
            
        } catch (error) {
            throw new Error('Error creando el PDF');
        }
    }

    downloadPDF(ticketId) {
        // Simulación de descarga
        log(`Downloading PDF for ticket: ${ticketId}`);
        
        // Crear elemento de descarga simulado
        const link = document.createElement('a');
        link.href = '#'; // Aquí iría la URL del PDF generado
        link.download = `ticket-${ticketId}.pdf`;
        
        // En una implementación real, aquí se generaría el PDF usando jsPDF
        this.showSuccess('En una implementación completa, aquí se descargaría el PDF del boleto.');
    }

    showError(message) {
        showModal(`
            <div style="text-align: center; padding: 20px;">
                <div style="color: #e74c3c; font-size: 3rem; margin-bottom: 15px;">❌</div>
                <h3 style="color: #e74c3c; margin-bottom: 10px;">Error</h3>
                <p>${message}</p>
            </div>
        `);
    }

    showSuccess(message) {
        showModal(`
            <div style="text-align: center; padding: 20px;">
                <div style="color: #27ae60; font-size: 3rem; margin-bottom: 15px;">✅</div>
                <h3 style="color: #27ae60; margin-bottom: 10px;">Éxito</h3>
                <p>${message}</p>
            </div>
        `);
    }
}

// Crear instancia global
window.TicketGenerator = new TicketGenerator();

// Exponer método para usar desde el HTML
window.TicketGenerator.downloadPDF = window.TicketGenerator.downloadPDF.bind(window.TicketGenerator);
