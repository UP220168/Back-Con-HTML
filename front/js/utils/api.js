// Utilidades para API
class ApiClient {
    constructor() {
        this.baseURL = CONFIG.API_BASE_URL;
    }

    // Método para realizar peticiones HTTP
    async request(endpoint, options = {}) {
        const url = buildUrl(endpoint, options.params);
        
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };

        // Agregar token de autenticación si existe
        const token = Storage.get(CONFIG.STORAGE.AUTH_TOKEN_KEY);
        if (token) {
            defaultOptions.headers['Authorization'] = `Bearer ${token}`;
        }

        const finalOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };

        try {
            log(`Making ${finalOptions.method || 'GET'} request to: ${url}`);
            
            const response = await fetch(url, finalOptions);
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.detail || `HTTP Error: ${response.status}`);
            }

            const data = await response.json();
            log('API Response received', 'info', data);
            
            return data;
        } catch (error) {
            log(`API Error: ${error.message}`, 'error', error);
            throw error;
        }
    }

    // Métodos de conveniencia
    async get(endpoint, params = {}) {
        return this.request(endpoint, { 
            method: 'GET',
            params 
        });
    }

    async post(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    }

    async put(endpoint, data = {}) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    }

    async delete(endpoint) {
        return this.request(endpoint, {
            method: 'DELETE'
        });
    }
}

// Instancia global del cliente API
const api = new ApiClient();

// Funciones específicas para los endpoints de reportes
const ReportsAPI = {
    async getSalesTotal(startDate = null, endDate = null) {
        const params = {};
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;
        
        return api.get(CONFIG.ENDPOINTS.SALES_TOTAL, params);
    },

    async getCustomersTotal() {
        return api.get(CONFIG.ENDPOINTS.CUSTOMERS_TOTAL);
    },

    async getSalesByMembership() {
        return api.get(CONFIG.ENDPOINTS.SALES_MEMBERSHIP);
    },

    async getTicketsByMovie() {
        return api.get(CONFIG.ENDPOINTS.TICKETS_BY_MOVIE);
    },

    async getTicketsByAuditorium() {
        return api.get(CONFIG.ENDPOINTS.TICKETS_BY_AUDITORIUM);
    },

    async getMostSoldMovie() {
        return api.get(CONFIG.ENDPOINTS.MOVIES_MOST_SOLD);
    },

    async getLeastSoldMovie() {
        return api.get(CONFIG.ENDPOINTS.MOVIES_LEAST_SOLD);
    },

    async getDashboard() {
        return api.get(CONFIG.ENDPOINTS.DASHBOARD);
    }
};

// Funciones para autenticación
const AuthAPI = {
    async login(email, password) {
        return api.post(CONFIG.ENDPOINTS.LOGIN, { 
            usr_email: email, 
            usr_password: password 
        });
    },

    async register(userData) {
        return api.post(CONFIG.ENDPOINTS.REGISTER, userData);
    }
};

// Funciones para otros endpoints
const MoviesAPI = {
    async getAll(skip = 0, limit = 100) {
        return api.get(CONFIG.ENDPOINTS.MOVIES, { skip, limit });
    },

    async getById(id) {
        return api.get(`${CONFIG.ENDPOINTS.MOVIES}/${id}`);
    }
};

const TicketsAPI = {
    async getAll(skip = 0, limit = 100) {
        return api.get(CONFIG.ENDPOINTS.TICKETS, { skip, limit });
    },

    async getById(id) {
        return api.get(`${CONFIG.ENDPOINTS.TICKETS}/${id}`);
    }
};

// API para Screenings
const ScreeningsAPI = {
    async getAll(skip = 0, limit = 100) {
        return api.get(CONFIG.ENDPOINTS.SCREENINGS, { skip, limit });
    },

    async getById(id) {
        return api.get(`${CONFIG.ENDPOINTS.SCREENINGS}/${id}`);
    },

    async create(data) {
        return api.post(CONFIG.ENDPOINTS.SCREENINGS, data);
    },

    async update(id, data) {
        return api.put(`${CONFIG.ENDPOINTS.SCREENINGS}/${id}`, data);
    },

    async delete(id) {
        return api.delete(`${CONFIG.ENDPOINTS.SCREENINGS}/${id}`);
    }
};

// API para Auditoriums
const AuditoriumsAPI = {
    async getAll(skip = 0, limit = 100) {
        return api.get(CONFIG.ENDPOINTS.AUDITORIUMS, { skip, limit });
    },

    async getById(id) {
        return api.get(`${CONFIG.ENDPOINTS.AUDITORIUMS}/${id}`);
    }
};

// Manejo de errores globales
window.addEventListener('unhandledrejection', event => {
    log('Unhandled promise rejection', 'error', event.reason);
    
    // Mostrar notificación de error al usuario
    showNotification('Error inesperado. Por favor, recarga la página.', 'error');
    
    event.preventDefault();
});

// Función para mostrar notificaciones (será implementada en otro archivo)
function showNotification(message, type = 'info') {
    // Implementación básica
    console.log(`[${type.toUpperCase()}] ${message}`);
}

// Exportar API global para compatibilidad con componentes
window.API = {
    // Cliente base
    client: api,
    
    // APIs específicas
    reports: ReportsAPI,
    auth: AuthAPI,
    movies: MoviesAPI,
    tickets: TicketsAPI,
    screenings: ScreeningsAPI,
    auditoriums: AuditoriumsAPI,
    
    // Métodos directos del cliente
    get: (endpoint, params) => api.get(endpoint, params),
    post: (endpoint, data) => api.post(endpoint, data),
    put: (endpoint, data) => api.put(endpoint, data),
    delete: (endpoint) => api.delete(endpoint),
    request: (endpoint, options) => api.request(endpoint, options)
};
