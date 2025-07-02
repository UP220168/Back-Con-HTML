// Script de prueba para verificar la tarjeta combinada de películas destacadas
console.log('=== TESTING COMBINED MOVIES HIGHLIGHTS ===');

// Función para simular datos de prueba
async function testMoviesHighlights() {
    try {
        console.log('Testing movies highlights card...');
        
        // Verificar que el container existe
        const container = document.getElementById('movies-highlights-container');
        if (!container) {
            console.error('❌ Container movies-highlights-container not found');
            return;
        }
        
        console.log('✅ Container found:', container);
        
        // Verificar que Dashboard existe
        if (!window.Dashboard) {
            console.error('❌ Dashboard component not found');
            return;
        }
        
        console.log('✅ Dashboard component found');
        
        // Cargar datos del dashboard
        console.log('Loading dashboard data...');
        await window.Dashboard.loadData();
        
        console.log('Dashboard data loaded:');
        console.log('- Most sold movie:', window.Dashboard.data.mostSoldMovie);
        console.log('- Least sold movie:', window.Dashboard.data.leastSoldMovie);
        
        // Verificar el contenido del container después de cargar datos
        setTimeout(() => {
            console.log('Container content after loading:', container.innerHTML);
            
            if (container.innerHTML.includes('No hay datos')) {
                console.warn('⚠️ No data available for movies highlights');
            } else if (container.innerHTML.includes('Cargando')) {
                console.warn('⚠️ Still loading...');
            } else {
                console.log('✅ Movies highlights loaded successfully!');
            }
        }, 2000);
        
    } catch (error) {
        console.error('❌ Error testing movies highlights:', error);
    }
}

// Función para verificar los endpoints directamente
async function testMoviesEndpoints() {
    try {
        console.log('Testing movies endpoints...');
        
        // Test most sold movie
        console.log('Testing most sold movie endpoint...');
        const mostSoldResponse = await fetch('http://localhost:5000/api/reports/movies/most-sold');
        const mostSoldData = await mostSoldResponse.json();
        console.log('Most sold movie data:', mostSoldData);
        
        // Test least sold movie
        console.log('Testing least sold movie endpoint...');
        const leastSoldResponse = await fetch('http://localhost:5000/api/reports/movies/least-sold');
        const leastSoldData = await leastSoldResponse.json();
        console.log('Least sold movie data:', leastSoldData);
        
        return {
            mostSold: mostSoldData,
            leastSold: leastSoldData
        };
        
    } catch (error) {
        console.error('❌ Error testing endpoints:', error);
        return null;
    }
}

// Exponer funciones globalmente
window.testMoviesHighlights = testMoviesHighlights;
window.testMoviesEndpoints = testMoviesEndpoints;

// Auto-ejecutar test cuando la página esté lista
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(() => {
        if (window.location.hash === '' || window.location.hash === '#dashboard') {
            console.log('Running automatic test...');
            testMoviesHighlights();
        }
    }, 3000);
});

console.log('Test functions loaded. Use testMoviesHighlights() or testMoviesEndpoints() to test manually.');
