// Script de debug para probar screenings
console.log('=== DEBUGGING SCREENINGS COMPONENT ===');

// 1. Verificar que el componente esté disponible
if (window.Screenings) {
    console.log('✅ Componente Screenings está disponible');
    console.log('Screenings object:', window.Screenings);
} else {
    console.error('❌ Componente Screenings NO está disponible');
}

// 2. Verificar elementos del DOM
const screeningsList = document.getElementById('screenings-admin-list');
const screeningsTable = document.getElementById('screenings-table');

console.log('Elements check:');
console.log('- screenings-admin-list:', screeningsList);
console.log('- screenings-table:', screeningsTable);

// 3. Verificar si hay conflictos de ID
const allScreeningsElements = document.querySelectorAll('[id*="screenings-list"]');
console.log('All elements with screenings-list in ID:', allScreeningsElements);

// 4. Verificar configuración de API
console.log('API Config:', CONFIG);
console.log('Screenings endpoint:', CONFIG.ENDPOINTS.SCREENINGS);

// 5. Probar la API directamente
async function testScreeningsAPI() {
    try {
        console.log('Testing screenings API directly...');
        const response = await fetch(`${CONFIG.API_BASE_URL}${CONFIG.ENDPOINTS.SCREENINGS}`);
        const data = await response.json();
        console.log('✅ Direct API test successful:', data);
        return data;
    } catch (error) {
        console.error('❌ Direct API test failed:', error);
        return null;
    }
}

// 6. Función para reinicializar screenings
async function debugScreenings() {
    try {
        console.log('=== STARTING SCREENINGS DEBUG ===');
        
        // Test API first
        const apiData = await testScreeningsAPI();
        
        if (window.Screenings && typeof window.Screenings.loadData === 'function') {
            console.log('Calling Screenings.loadData()...');
            await window.Screenings.loadData();
            console.log('Screenings data after loadData():', window.Screenings.screenings);
        } else {
            console.error('Screenings.loadData() is not available');
        }
        
        // Check final DOM state
        const tbody = document.getElementById('screenings-admin-list');
        if (tbody) {
            console.log('Final tbody content:', tbody.innerHTML);
        } else {
            console.error('screenings-admin-list element not found');
        }
        
    } catch (error) {
        console.error('Debug failed:', error);
    }
}

// Exponer funciones globalmente para uso en consola
window.testScreeningsAPI = testScreeningsAPI;
window.debugScreenings = debugScreenings;

console.log('=== DEBUGGING FUNCTIONS AVAILABLE ===');
console.log('- testScreeningsAPI(): Test API directly');
console.log('- debugScreenings(): Run full debug process');
console.log('Execute: await debugScreenings()');
