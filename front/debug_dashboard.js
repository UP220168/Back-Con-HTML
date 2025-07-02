// Script de depuración para consola del navegador
console.log('=== DASHBOARD DEBUG SCRIPT ===');

// Función para verificar si todos los elementos del dashboard están presentes
function checkDashboardElements() {
    console.log('Checking dashboard elements...');
    
    const elements = {
        'total-sales': document.getElementById('total-sales'),
        'total-transactions': document.getElementById('total-transactions'),
        'total-customers': document.getElementById('total-customers'),
        'total-tickets': document.getElementById('total-tickets'),
        'movies-available': document.getElementById('movies-available'),
        'tickets-by-movie-container': document.getElementById('tickets-by-movie-container'),
        'tickets-by-auditorium-container': document.getElementById('tickets-by-auditorium-container'),
        'movies-highlights-container': document.getElementById('movies-highlights-container')
    };
    
    Object.entries(elements).forEach(([id, element]) => {
        if (element) {
            console.log(`✅ ${id}: Found`);
        } else {
            console.log(`❌ ${id}: NOT FOUND`);
        }
    });
    
    return elements;
}

// Función para verificar la API
function checkAPI() {
    console.log('Checking API...');
    
    if (typeof ReportsAPI !== 'undefined') {
        console.log('✅ ReportsAPI is available');
        console.log('Available methods:', Object.keys(ReportsAPI));
        
        // Verificar métodos específicos
        const methods = ['getMostSoldMovie', 'getLeastSoldMovie', 'getTicketsByMovie', 'getTicketsByAuditorium'];
        methods.forEach(method => {
            if (typeof ReportsAPI[method] === 'function') {
                console.log(`✅ ReportsAPI.${method} is available`);
            } else {
                console.log(`❌ ReportsAPI.${method} is NOT available`);
            }
        });
    } else {
        console.log('❌ ReportsAPI is NOT available');
    }
}

// Función para verificar el Dashboard
function checkDashboard() {
    console.log('Checking Dashboard...');
    
    if (typeof window.Dashboard !== 'undefined') {
        console.log('✅ Dashboard component is available');
        console.log('Dashboard data:', window.Dashboard.data);
    } else {
        console.log('❌ Dashboard component is NOT available');
    }
}

// Función para forzar la recarga de datos
async function reloadDashboard() {
    console.log('Reloading dashboard data...');
    
    if (window.Dashboard) {
        try {
            await window.Dashboard.loadData();
            console.log('✅ Dashboard data reloaded successfully');
            console.log('Current data:', window.Dashboard.data);
        } catch (error) {
            console.error('❌ Error reloading dashboard:', error);
        }
    } else {
        console.error('❌ Dashboard component not available');
    }
}

// Ejecutar todas las verificaciones
function runFullCheck() {
    console.clear();
    console.log('=== FULL DASHBOARD CHECK ===');
    
    checkDashboardElements();
    console.log('\n---');
    checkAPI();
    console.log('\n---');
    checkDashboard();
    
    console.log('\n=== RECOMMENDATIONS ===');
    console.log('1. If any elements are missing, check the HTML structure');
    console.log('2. If API methods are missing, check api.js file');
    console.log('3. If Dashboard is not available, check dashboard.js file');
    console.log('4. Run reloadDashboard() to force data reload');
}

// Exponer funciones globalmente
window.checkDashboardElements = checkDashboardElements;
window.checkAPI = checkAPI;
window.checkDashboard = checkDashboard;
window.reloadDashboard = reloadDashboard;
window.runFullCheck = runFullCheck;

console.log('Debug functions loaded. Use runFullCheck() to perform full check.');
console.log('Individual functions: checkDashboardElements(), checkAPI(), checkDashboard(), reloadDashboard()');
