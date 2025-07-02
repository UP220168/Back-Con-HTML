// Script para probar el dashboard desde la consola del navegador
console.log('🎬 PROBANDO DASHBOARD DEL FRONTEND');
console.log('='.repeat(50));

// Función para probar la carga de datos del dashboard
async function testDashboardData() {
    try {
        console.log('🚀 Iniciando pruebas del dashboard...');
        
        // Verificar que el componente Dashboard existe
        if (typeof window.Dashboard === 'undefined') {
            console.error('❌ Componente Dashboard no encontrado');
            return;
        }
        
        console.log('✅ Componente Dashboard encontrado');
        
        // Verificar que la API está disponible
        if (typeof window.API === 'undefined' || typeof window.ReportsAPI === 'undefined') {
            console.error('❌ API no disponible');
            return;
        }
        
        console.log('✅ API disponible');
        
        // Cargar datos del dashboard
        console.log('📡 Cargando datos del dashboard...');
        await window.Dashboard.loadData();
        
        console.log('✅ Datos del dashboard cargados');
        
        // Verificar que los elementos del DOM existen
        const elements = [
            'total-sales',
            'total-transactions', 
            'total-customers',
            'total-tickets',
            'movies-available',
            'tickets-by-movie-container',
            'tickets-by-auditorium-container',
            'most-sold-movie-container',
            'least-sold-movie-container'
        ];
        
        console.log('🔍 Verificando elementos del DOM...');
        elements.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                console.log(`✅ ${id}: ${element.textContent || 'Contenido dinámico'}`);
            } else {
                console.log(`❌ ${id}: No encontrado`);
            }
        });
        
        // Mostrar datos cargados
        if (window.Dashboard.data) {
            console.log('📊 Datos del dashboard:', window.Dashboard.data);
        }
        
        console.log('🎉 Pruebas completadas exitosamente!');
        
    } catch (error) {
        console.error('💥 Error en las pruebas:', error);
    }
}

// Función para refrescar el dashboard
async function refreshDashboard() {
    console.log('🔄 Refrescando dashboard...');
    try {
        await window.Dashboard.refresh();
        console.log('✅ Dashboard refrescado');
    } catch (error) {
        console.error('❌ Error refrescando dashboard:', error);
    }
}

// Función para probar endpoints individualmente
async function testIndividualEndpoints() {
    console.log('🔍 Probando endpoints individuales...');
    
    try {
        // Probar boletos por película
        console.log('📽️ Probando boletos por película...');
        const movieData = await ReportsAPI.getTicketsByMovie();
        console.log('Boletos por película:', movieData);
        
        // Probar boletos por sala
        console.log('🏛️ Probando boletos por sala...');
        const auditoriumData = await ReportsAPI.getTicketsByAuditorium();
        console.log('Boletos por sala:', auditoriumData);
        
        // Probar película más vendida
        console.log('🏆 Probando película más vendida...');
        const mostSoldData = await ReportsAPI.getMostSoldMovie();
        console.log('Película más vendida:', mostSoldData);
        
        // Probar película menos vendida
        console.log('📉 Probando película menos vendida...');
        const leastSoldData = await ReportsAPI.getLeastSoldMovie();
        console.log('Película menos vendida:', leastSoldData);
        
        console.log('✅ Todos los endpoints probados exitosamente');
        
    } catch (error) {
        console.error('❌ Error probando endpoints:', error);
    }
}

// Exponer funciones globalmente para uso en consola
window.testDashboardData = testDashboardData;
window.refreshDashboard = refreshDashboard;
window.testIndividualEndpoints = testIndividualEndpoints;

console.log('📋 FUNCIONES DISPONIBLES:');
console.log('- testDashboardData(): Prueba completa del dashboard');
console.log('- refreshDashboard(): Refresca los datos del dashboard');
console.log('- testIndividualEndpoints(): Prueba endpoints individuales');
console.log('');
console.log('💡 Ejecuta: testDashboardData() para empezar');
