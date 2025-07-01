// Utilidad para generar PDFs de boletos
class PDFGenerator {
    static generateTicketPDF(saleData, customerData) {
        console.log('📄 Generando PDF de boletos...');
        
        try {
            // Crear nueva instancia de jsPDF
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            
            // Configuración de colores
            const primaryColor = [74, 144, 226];
            const textColor = [51, 51, 51];
            const grayColor = [128, 128, 128];
            
            // Header
            doc.setFillColor(...primaryColor);
            doc.rect(0, 0, 210, 30, 'F');
            
            doc.setTextColor(255, 255, 255);
            doc.setFontSize(24);
            doc.setFont('helvetica', 'bold');
            doc.text('🎬 Cinema el Foraneo', 20, 20);
            
            // Título del boleto
            doc.setTextColor(...textColor);
            doc.setFontSize(18);
            doc.setFont('helvetica', 'bold');
            doc.text('BOLETO DE ENTRADA', 20, 45);
            
            // Información de la venta
            doc.setFontSize(12);
            doc.setFont('helvetica', 'normal');
            doc.text(`ID de Venta: ${saleData.sal_id || 'N/A'}`, 20, 60);
            doc.text(`Fecha: ${new Date().toLocaleDateString('es-ES')}`, 120, 60);
            
            // Línea separadora
            doc.setDrawColor(...grayColor);
            doc.line(20, 70, 190, 70);
            
            // Información de la película y función
            let yPos = 85;
            doc.setFontSize(14);
            doc.setFont('helvetica', 'bold');
            doc.text('DETALLES DE LA FUNCIÓN', 20, yPos);
            
            yPos += 15;
            doc.setFontSize(11);
            doc.setFont('helvetica', 'normal');
            doc.text(`Película: ${saleData.movieTitle || 'N/A'}`, 20, yPos);
            
            yPos += 10;
            doc.text(`Fecha: ${saleData.screeningDate || 'N/A'}`, 20, yPos);
            doc.text(`Hora: ${saleData.screeningTime || 'N/A'}`, 120, yPos);
            
            yPos += 10;
            doc.text(`Auditorio: ${saleData.auditoriumName || 'N/A'}`, 20, yPos);
            doc.text(`Precio: $${saleData.ticketPrice || '0.00'}`, 120, yPos);
            
            // Línea separadora
            yPos += 15;
            doc.line(20, yPos, 190, yPos);
            
            // Información de los asientos
            yPos += 15;
            doc.setFontSize(14);
            doc.setFont('helvetica', 'bold');
            doc.text('ASIENTOS SELECCIONADOS', 20, yPos);
            
            yPos += 15;
            doc.setFontSize(11);
            doc.setFont('helvetica', 'normal');
            
            if (saleData.selectedSeats && saleData.selectedSeats.length > 0) {
                saleData.selectedSeats.forEach((seat, index) => {
                    doc.text(`Asiento ${index + 1}: Fila ${seat.row}, Asiento ${seat.number}`, 20, yPos);
                    yPos += 8;
                });
            } else {
                doc.text('No hay información de asientos disponible', 20, yPos);
                yPos += 8;
            }
            
            // Línea separadora
            yPos += 10;
            doc.line(20, yPos, 190, yPos);
            
            // Información del cliente
            yPos += 15;
            doc.setFontSize(14);
            doc.setFont('helvetica', 'bold');
            doc.text('INFORMACIÓN DEL CLIENTE', 20, yPos);
            
            yPos += 15;
            doc.setFontSize(11);
            doc.setFont('helvetica', 'normal');
            doc.text(`Nombre: ${customerData.name || 'N/A'}`, 20, yPos);
            
            yPos += 10;
            doc.text(`Email: ${customerData.email || 'N/A'}`, 20, yPos);
            
            yPos += 10;
            doc.text(`Teléfono: ${customerData.phone || 'N/A'}`, 20, yPos);
            
            // Total
            yPos += 20;
            doc.setFillColor(240, 240, 240);
            doc.rect(20, yPos - 5, 170, 20, 'F');
            
            doc.setFontSize(14);
            doc.setFont('helvetica', 'bold');
            doc.setTextColor(...primaryColor);
            doc.text(`TOTAL: $${saleData.totalAmount || '0.00'}`, 20, yPos + 8);
            
            // Método de pago
            doc.setTextColor(...textColor);
            doc.setFontSize(11);
            doc.setFont('helvetica', 'normal');
            doc.text(`Método de pago: ${customerData.paymentMethod || 'N/A'}`, 120, yPos + 8);
            
            // Footer
            yPos += 40;
            doc.setTextColor(...grayColor);
            doc.setFontSize(9);
            doc.text('Este boleto es válido únicamente para la función indicada.', 20, yPos);
            doc.text('Conserve este boleto como comprobante de su compra.', 20, yPos + 8);
            doc.text('Cinema el Foraneo - Sistema de Gestión de Boletos', 20, yPos + 20);
            
            // Generar nombre del archivo
            const fileName = `boleto_${saleData.sal_id || 'temp'}_${Date.now()}.pdf`;
            
            // Descargar el PDF
            doc.save(fileName);
            
            console.log('✅ PDF generado exitosamente:', fileName);
            return fileName;
            
        } catch (error) {
            console.error('❌ Error generando PDF:', error);
            throw new Error('Error al generar el PDF: ' + error.message);
        }
    }
    
    static generateSimplePDF(text = 'Boleto de prueba') {
        try {
            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();
            
            doc.setFontSize(16);
            doc.text(text, 20, 20);
            doc.text(`Generado: ${new Date().toLocaleString()}`, 20, 40);
            
            doc.save('boleto_prueba.pdf');
            console.log('✅ PDF de prueba generado');
            
        } catch (error) {
            console.error('❌ Error generando PDF de prueba:', error);
            alert('Error: jsPDF no está disponible. Asegúrate de que la librería esté cargada.');
        }
    }
}

// Exponer PDFGenerator globalmente
window.PDFGenerator = PDFGenerator;

// Función de prueba
window.testPDF = () => {
    const testData = {
        sal_id: 'TEST123',
        movieTitle: 'Película de Prueba',
        screeningDate: '2024-01-15',
        screeningTime: '20:00',
        auditoriumName: 'Auditorio 1',
        ticketPrice: '12.50',
        selectedSeats: [
            { row: 'A', number: 5 },
            { row: 'A', number: 6 }
        ],
        totalAmount: '25.00'
    };
    
    const customerData = {
        name: 'Cliente de Prueba',
        email: 'test@example.com',
        phone: '123-456-7890',
        paymentMethod: 'Tarjeta'
    };
    
    PDFGenerator.generateTicketPDF(testData, customerData);
};

console.log('📄 PDFGenerator cargado. Usa testPDF() para probar.');
