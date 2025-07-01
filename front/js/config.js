// Configuración de la aplicación
const CONFIG = {
    API_BASE_URL: 'http://localhost:5000/api',
    ENDPOINTS: {
        // Auth
        LOGIN: '/users/login',
        REGISTER: '/users',
        
        // Reports
        SALES_TOTAL: '/reports/sales/total',
        CUSTOMERS_TOTAL: '/reports/customers/total',
        SALES_MEMBERSHIP: '/reports/sales/membership',
        TICKETS_BY_MOVIE: '/reports/tickets/by-movie',
        TICKETS_BY_AUDITORIUM: '/reports/tickets/by-auditorium',
        MOVIES_MOST_SOLD: '/reports/movies/most-sold',
        MOVIES_LEAST_SOLD: '/reports/movies/least-sold',
        DASHBOARD: '/reports/dashboard',
        
        // Others
        MOVIES: '/movies',
        AUDITORIUMS: '/auditoriums',
        SCREENINGS: '/screenings',
        TICKETS: '/tickets',
        SALES: '/sales'
    },
    
    // Configuración de la aplicación
    APP: {
        NAME: 'Cinema Management',
        VERSION: '1.0.0',
        DEBUG: true
    },
    
    // Configuración de localStorage
    STORAGE: {
        USER_KEY: 'cinema_user',
        AUTH_TOKEN_KEY: 'cinema_auth_token',
        SETTINGS_KEY: 'cinema_settings'
    },
    
    // Configuración de UI
    UI: {
        LOADING_DELAY: 300,
        NOTIFICATION_DURATION: 5000,
        ANIMATION_DURATION: 300
    }
};

// Función para construir URL completa
function buildUrl(endpoint, params = {}) {
    let url = CONFIG.API_BASE_URL + endpoint;
    
    const queryParams = new URLSearchParams();
    Object.keys(params).forEach(key => {
        if (params[key] !== null && params[key] !== undefined) {
            queryParams.append(key, params[key]);
        }
    });
    
    const queryString = queryParams.toString();
    if (queryString) {
        url += '?' + queryString;
    }
    
    return url;
}

// Función para logging
function log(message, type = 'info', data = null) {
    if (!CONFIG.APP.DEBUG) return;
    
    const timestamp = new Date().toLocaleTimeString();
    const prefix = `[${timestamp}] [${type.toUpperCase()}]`;
    
    switch (type) {
        case 'error':
            console.error(prefix, message, data);
            break;
        case 'warn':
            console.warn(prefix, message, data);
            break;
        case 'info':
        default:
            console.log(prefix, message, data);
            break;
    }
}

// Función para testing
async function testAPI() {
    console.log('=== TESTING API CONNECTIVITY ===');
    
    try {
        // Test movies
        console.log('Testing movies API...');
        const moviesResponse = await fetch('http://localhost:5000/api/movies/');
        const moviesData = await moviesResponse.json();
        console.log('✅ Movies API working:', moviesData);
        
        // Test auditoriums  
        console.log('Testing auditoriums API...');
        const auditoriumsResponse = await fetch('http://localhost:5000/api/auditoriums/');
        const auditoriumsData = await auditoriumsResponse.json();
        console.log('✅ Auditoriums API working:', auditoriumsData);
        
        // Test screenings
        console.log('Testing screenings API...');
        const screeningsResponse = await fetch('http://localhost:5000/api/screenings/');
        const screeningsData = await screeningsResponse.json();
        console.log('✅ Screenings API working:', screeningsData);
        
        console.log('=== ALL APIS WORKING ===');
        return true;
        
    } catch (error) {
        console.error('❌ API Test failed:', error);
        return false;
    }
}

// Exponer función de test globalmente
window.testAPI = testAPI;

// Función para probar creación de función usando endpoint de test
function testCreateScreeningTest() {
    console.log('🧪 Probando creación de función con endpoint de test...');
    
    const testData = {
        scr_mov_id: "1", // Primer película
        scr_aud_id: "1", // Primer auditorio
        scr_date: "2024-01-15",
        scr_time: "20:00",
        scr_price: 10.50,
        scr_status: "scheduled"
    };
    
    console.log('📤 Datos de prueba:', testData);
    console.log('🔗 URL:', CONFIG.API_BASE_URL + '/api/screenings/test');
    
    fetch(CONFIG.API_BASE_URL + '/api/screenings/test', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(testData)
    })
    .then(async response => {
        console.log('📥 Respuesta recibida:', response.status, response.statusText);
        const text = await response.text();
        console.log('📄 Contenido de respuesta:', text);
        
        if (response.ok) {
            console.log('✅ Función creada exitosamente con endpoint de test');
            return JSON.parse(text);
        } else {
            console.error('❌ Error en endpoint de test:', response.status, text);
            throw new Error(`HTTP ${response.status}: ${text}`);
        }
    })
    .then(data => {
        console.log('🎉 Resultado exitoso:', data);
    })
    .catch(error => {
        console.error('💥 Error completo:', error);
    });
}

// Exponer función de test
window.testCreateScreeningTest = testCreateScreeningTest;
