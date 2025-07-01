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
