// Componente Screenings - Versión simplificada para debug
class Screenings {
    constructor() {
        console.log('✅ Screenings constructor called');
        this.screenings = [];
        this.movies = [];
        this.auditoriums = [];
        this.editingScreening = null;
        
        console.log('✅ Screenings properties initialized');
        
        // Inicializar cuando el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.init());
        } else {
            this.init();
        }
    }

    init() {
        console.log('✅ Screenings init() called');
        this.checkDependencies();
        this.setupEventListeners();
    }
    
    checkDependencies() {
        console.log('✅ Checking dependencies...');
        
        // Verificar showLoading
        if (typeof showLoading === 'undefined') {
            console.warn('showLoading no está disponible, creando función mock');
            window.showLoading = function(show) {
                console.log('showLoading mock:', show);
            };
        }
        
        // Verificar log
        if (typeof log === 'undefined') {
            console.warn('log no está disponible, creando función mock');
            window.log = function(message, type = 'info', data = null) {
                console.log(`[${type.toUpperCase()}]`, message, data);
            };
        }
        
        // Verificar CONFIG
        if (typeof CONFIG === 'undefined') {
            console.error('CONFIG no está disponible - el componente no funcionará correctamente');
        }
    }

    setupEventListeners() {
        console.log('✅ Setting up event listeners...');
        // Función básica - sin eventos complejos por ahora
    }

    // Método para cargar datos cuando se navega a la página
    async loadData() {
        console.log('✅ loadData() called');
        return Promise.resolve();
    }
}

// Crear instancia global de manera segura
try {
    console.log('🔄 Intentando crear instancia de Screenings...');
    window.Screenings = new Screenings();
    console.log('✅ Componente Screenings cargado exitosamente');
} catch (error) {
    console.error('❌ Error cargando componente Screenings:', error);
    
    // Crear un objeto mock básico para evitar errores
    window.Screenings = {
        loadData: function() {
            console.error('Screenings component failed to load');
            return Promise.resolve();
        },
        movies: [],
        auditoriums: [],
        screenings: []
    };
}
