// Utilidad para generar PDFs de boletos
class TicketPDFGenerator {
    constructor() {
        // Verificar si jsPDF está disponible
        if (typeof window.jspdf === 'undefined') {
            console.warn('jsPDF no está disponible. Descargando desde CDN...');
            this.loadJsPDF();
        }
    }

    loadJsPDF() {
        return new Promise((resolve, reject) => {
            const script = document.createElement('script');
            script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js';
            script.onload = () => {
                console.log('✅ jsPDF cargado exitosamente');
                resolve();
            };
            script.onerror = () => {
                console.error('❌ Error cargando jsPDF');
                reject(new Error('No se pudo cargar jsPDF'));
            };
            document.head.appendChild(script);
        });
    }

    async generateTicketPDF(purchaseData) {
        try {
            // Asegurar que jsPDF esté disponible
            if (typeof window.jspdf === 'undefined') {
                await this.loadJsPDF();
            }

            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();

            // Configurar fuentes y colores
            doc.setFontSize(20);
            doc.setTextColor(74, 144, 226); // Color primario
            
            // Título principal
            doc.text('🎬 Cinema el Foraneo', 20, 30);
            doc.setFontSize(16);
            doc.setTextColor(0, 0, 0);
            doc.text('Boleto de Entrada', 20, 45);

            // Línea separadora
            doc.setDrawColor(74, 144, 226);
            doc.setLineWidth(1);
            doc.line(20, 50, 190, 50);

            // Información de la compra
            let yPosition = 70;
            doc.setFontSize(12);
            
            // ID de compra
            doc.setFont(undefined, 'bold');
            doc.text('ID de Compra:', 20, yPosition);
            doc.setFont(undefined, 'normal');
            doc.text(purchaseData.saleId || 'N/A', 80, yPosition);
            yPosition += 15;

            // Película
            doc.setFont(undefined, 'bold');
            doc.text('Película:', 20, yPosition);
            doc.setFont(undefined, 'normal');
            doc.text(purchaseData.movieTitle || 'N/A', 80, yPosition);
            yPosition += 15;

            // Fecha y hora
            doc.setFont(undefined, 'bold');
            doc.text('Fecha:', 20, yPosition);
            doc.setFont(undefined, 'normal');
            doc.text(purchaseData.screeningDate || 'N/A', 80, yPosition);
            yPosition += 10;

            doc.setFont(undefined, 'bold');
            doc.text('Hora:', 20, yPosition);
            doc.setFont(undefined, 'normal');
            doc.text(purchaseData.screeningTime || 'N/A', 80, yPosition);
            yPosition += 15;

            // Auditorio
            doc.setFont(undefined, 'bold');
            doc.text('Auditorio:', 20, yPosition);
            doc.setFont(undefined, 'normal');
            doc.text(purchaseData.auditoriumName || 'N/A', 80, yPosition);
            yPosition += 15;

            // Asientos
            doc.setFont(undefined, 'bold');
            doc.text('Asientos:', 20, yPosition);
            doc.setFont(undefined, 'normal');
            const seatsText = purchaseData.seats ? purchaseData.seats.map(seat => `${seat.row}${seat.number}`).join(', ') : 'N/A';
            doc.text(seatsText, 80, yPosition);
            yPosition += 15;

            // Cliente
            doc.setFont(undefined, 'bold');
            doc.text('Cliente:', 20, yPosition);
            doc.setFont(undefined, 'normal');
            doc.text(purchaseData.customerName || 'N/A', 80, yPosition);
            yPosition += 10;

            doc.text(purchaseData.customerEmail || 'N/A', 80, yPosition);
            yPosition += 15;

            // Total
            doc.setFont(undefined, 'bold');
            doc.setFontSize(14);
            doc.text('Total:', 20, yPosition);
            doc.setTextColor(40, 167, 69); // Color verde
            doc.text(`$${purchaseData.totalAmount || '0.00'}`, 80, yPosition);
            yPosition += 20;

            // Línea separadora
            doc.setDrawColor(74, 144, 226);
            doc.line(20, yPosition, 190, yPosition);
            yPosition += 15;

            // Instrucciones
            doc.setFontSize(10);
            doc.setTextColor(100, 100, 100);
            doc.text('Instrucciones:', 20, yPosition);
            yPosition += 10;
            doc.text('• Presente este boleto en taquilla 15 minutos antes del inicio', 20, yPosition);
            yPosition += 10;
            doc.text('• El boleto es válido únicamente para la función indicada', 20, yPosition);
            yPosition += 10;
            doc.text('• No se permiten devoluciones después de iniciada la función', 20, yPosition);
            yPosition += 15;

            // Fecha de emisión
            doc.text(`Emitido el: ${new Date().toLocaleString('es-ES')}`, 20, yPosition);

            // Código QR o código de barras simulado
            yPosition += 20;
            doc.setDrawColor(0, 0, 0);
            doc.setFillColor(0, 0, 0);
            
            // Simular un código de barras simple
            for (let i = 0; i < 20; i++) {
                const x = 20 + (i * 8);
                const height = Math.random() > 0.5 ? 10 : 15;
                doc.rect(x, yPosition, 3, height, 'F');
            }

            // Guardar el PDF
            const fileName = `boleto_${purchaseData.saleId || Date.now()}.pdf`;
            doc.save(fileName);

            console.log('✅ PDF generado exitosamente:', fileName);
            return fileName;

        } catch (error) {
            console.error('❌ Error generando PDF:', error);
            
            // Fallback: descargar como texto
            this.generateTextTicket(purchaseData);
            throw error;
        }
    }

    generateTextTicket(purchaseData) {
        const ticketText = `
🎬 CINEMA EL FORANEO
========================

BOLETO DE ENTRADA
ID: ${purchaseData.saleId || 'N/A'}

Película: ${purchaseData.movieTitle || 'N/A'}
Fecha: ${purchaseData.screeningDate || 'N/A'}
Hora: ${purchaseData.screeningTime || 'N/A'}
Auditorio: ${purchaseData.auditoriumName || 'N/A'}
Asientos: ${purchaseData.seats ? purchaseData.seats.map(seat => `${seat.row}${seat.number}`).join(', ') : 'N/A'}

Cliente: ${purchaseData.customerName || 'N/A'}
Email: ${purchaseData.customerEmail || 'N/A'}

TOTAL: $${purchaseData.totalAmount || '0.00'}

========================
Emitido: ${new Date().toLocaleString('es-ES')}

Instrucciones:
• Presente este boleto 15 minutos antes
• Válido solo para la función indicada
• No se permiten devoluciones
        `;

        // Crear un blob y descargarlo
        const blob = new Blob([ticketText], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `boleto_${purchaseData.saleId || Date.now()}.txt`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        console.log('✅ Boleto de texto generado como fallback');
    }
}

// Instancia global del generador de PDFs
window.TicketPDFGenerator = new TicketPDFGenerator();
