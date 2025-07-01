// Versión mínima del componente Screenings para debug
console.log('Cargando screenings-minimal.js');

class ScreeningsMinimal {
    constructor() {
        console.log('Constructor ScreeningsMinimal ejecutado');
        this.movies = [];
        this.auditoriums = [];
        this.screenings = [];
    }
    
    async loadData() {
        console.log('loadData ejecutado');
        try {
            // Cargar películas
            if (typeof CONFIG !== 'undefined') {
                const response = await fetch(`${CONFIG.API_BASE_URL}/movies/`);
                if (response.ok) {
                    const data = await response.json();
                    this.movies = data.movies || [];
                    console.log('Películas cargadas:', this.movies.length);
                }
            }
            return Promise.resolve();
        } catch (error) {
            console.error('Error en loadData:', error);
            return Promise.reject(error);
        }
    }
}

console.log('Creando instancia ScreeningsMinimal');
try {
    window.ScreeningsMinimal = new ScreeningsMinimal();
    console.log('✅ ScreeningsMinimal creado exitosamente');
} catch (error) {
    console.error('❌ Error creando ScreeningsMinimal:', error);
}
