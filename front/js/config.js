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
        const moviesResponse = await fetch(`${CONFIG.API_BASE_URL}/movies/`);
        const moviesData = await moviesResponse.json();
        console.log('✅ Movies API working:', moviesData);
        
        // Test auditoriums  
        console.log('Testing auditoriums API...');
        const auditoriumsResponse = await fetch(`${CONFIG.API_BASE_URL}/auditoriums/`);
        const auditoriumsData = await auditoriumsResponse.json();
        console.log('✅ Auditoriums API working:', auditoriumsData);
        
        // Test screenings
        console.log('Testing screenings API...');
        const screeningsResponse = await fetch(`${CONFIG.API_BASE_URL}/screenings/`);
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

// Función para revisar todos los registros de la base de datos
async function reviewDatabaseRecords() {
    console.log('=== REVISANDO REGISTROS DE LA BASE DE DATOS ===');
    
    try {
        // 1. Revisar películas
        console.log('📽️ Consultando películas...');
        const moviesResponse = await fetch(`${CONFIG.API_BASE_URL}/movies/?limit=50`);
        const moviesData = await moviesResponse.json();
        console.log(`✅ Total de películas: ${moviesData.movies?.length || 0}`);
        if (moviesData.movies?.length > 0) {
            console.log('🎬 Películas disponibles:');
            moviesData.movies.forEach((movie, index) => {
                console.log(`  ${index + 1}. ${movie.mov_title} (${movie.mov_genre}) - Estado: ${movie.mov_status}`);
            });
        }
        
        // 2. Revisar auditorios
        console.log('\n🏛️ Consultando auditorios...');
        const auditoriumsResponse = await fetch(`${CONFIG.API_BASE_URL}/auditoriums/?limit=50`);
        const auditoriumsData = await auditoriumsResponse.json();
        console.log(`✅ Total de auditorios: ${auditoriumsData.auditoriums?.length || 0}`);
        if (auditoriumsData.auditoriums?.length > 0) {
            console.log('🎭 Auditorios disponibles:');
            auditoriumsData.auditoriums.forEach((aud, index) => {
                console.log(`  ${index + 1}. ${aud.aud_name} - Capacidad: ${aud.aud_total_rows}x${aud.aud_seats_per_row} = ${aud.total_capacity || 'N/A'} asientos`);
            });
        }
        
        // 3. Revisar funciones (screenings)
        console.log('\n🎪 Consultando funciones...');
        const screeningsResponse = await fetch(`${CONFIG.API_BASE_URL}/screenings/?limit=50`);
        const screeningsData = await screeningsResponse.json();
        console.log(`✅ Total de funciones: ${screeningsData.screenings?.length || 0}`);
        if (screeningsData.screenings?.length > 0) {
            console.log('🎫 Funciones programadas:');
            screeningsData.screenings.forEach((screening, index) => {
                console.log(`  ${index + 1}. Película ID: ${screening.scr_mov_id?.substring(0, 8)}... - Fecha: ${screening.scr_date} ${screening.scr_time} - Precio: $${screening.scr_price} - Estado: ${screening.scr_status}`);
            });
        }
        
        // 4. Revisar boletos
        console.log('\n🎟️ Consultando boletos...');
        const ticketsResponse = await fetch(`${CONFIG.API_BASE_URL}/tickets/`);
        const ticketsData = await ticketsResponse.json();
        console.log(`✅ Total de boletos: ${ticketsData?.length || 0}`);
        if (ticketsData?.length > 0) {
            console.log('🎟️ Primeros boletos:');
            ticketsData.slice(0, 5).forEach((ticket, index) => {
                console.log(`  ${index + 1}. Fila ${ticket.tic_row}, Asiento ${ticket.tic_seat} - Función: ${ticket.tic_scr_id?.substring(0, 8)}... - Estado: ${ticket.tic_status}`);
            });
        }
        
        // 5. Revisar ventas
        console.log('\n💰 Consultando ventas...');
        const salesResponse = await fetch(`${CONFIG.API_BASE_URL}/sales/`);
        const salesData = await salesResponse.json();
        console.log(`✅ Total de ventas: ${salesData?.length || 0}`);
        if (salesData?.length > 0) {
            console.log('💳 Ventas registradas:');
            salesData.slice(0, 5).forEach((sale, index) => {
                console.log(`  ${index + 1}. Venta ID: ${sale.sal_id?.substring(0, 8)}... - Total: $${sale.sal_total} - Fecha: ${sale.sal_date}`);
            });
        }
        
        // 6. Revisar usuarios
        console.log('\n👥 Consultando usuarios...');
        const usersResponse = await fetch(`${CONFIG.API_BASE_URL}/users/?skip=0&limit=50`);
        const usersData = await usersResponse.json();
        console.log(`✅ Total de usuarios: ${usersData.users?.length || usersData?.length || 0}`);
        if (usersData.users?.length > 0 || usersData?.length > 0) {
            console.log('👤 Usuarios registrados:');
            const usersList = usersData.users || usersData || [];
            usersList.slice(0, 5).forEach((user, index) => {
                console.log(`  ${index + 1}. ${user.usr_name || user.name || 'Sin nombre'} - Email: ${user.usr_email || user.email || 'Sin email'}`);
            });
        }
        
        console.log('\n=== RESUMEN DE LA BASE DE DATOS ===');
        console.log(`📽️ Películas: ${moviesData.movies?.length || 0}`);
        console.log(`🏛️ Auditorios: ${auditoriumsData.auditoriums?.length || 0}`);
        console.log(`🎪 Funciones: ${screeningsData.screenings?.length || 0}`);
        console.log(`🎟️ Boletos: ${ticketsData?.length || 0}`);
        console.log(`💰 Ventas: ${salesData?.length || 0}`);
        console.log(`👥 Usuarios: ${usersData.users?.length || usersData?.length || 0}`);
        
        return {
            movies: moviesData.movies || [],
            auditoriums: auditoriumsData.auditoriums || [],
            screenings: screeningsData.screenings || [],
            tickets: ticketsData || [],
            sales: salesData || [],
            users: usersData.users || usersData || []
        };
        
    } catch (error) {
        console.error('❌ Error revisando registros:', error);
        return null;
    }
}

// Función para crear datos de prueba si no existen
async function createTestDataIfNeeded() {
    console.log('🧪 Verificando si necesitamos crear datos de prueba...');
    
    try {
        const data = await reviewDatabaseRecords();
        
        if (!data) {
            console.log('❌ No se pudieron obtener los datos');
            return;
        }
        
        // Si no hay funciones, crear algunas de prueba
        if (data.screenings.length === 0 && data.movies.length > 0 && data.auditoriums.length > 0) {
            console.log('🎬 Creando funciones de prueba...');
            
            const movie = data.movies[0];
            const auditorium = data.auditoriums[0];
            
            const testScreenings = [
                {
                    scr_mov_id: movie.mov_id,
                    scr_aud_id: auditorium.aud_id,
                    scr_date: "2025-07-02",
                    scr_time: "15:00:00",
                    scr_price: 12.50,
                    scr_status: "scheduled"
                },
                {
                    scr_mov_id: movie.mov_id,
                    scr_aud_id: auditorium.aud_id,
                    scr_date: "2025-07-02",
                    scr_time: "18:00:00",
                    scr_price: 15.00,
                    scr_status: "scheduled"
                },
                {
                    scr_mov_id: movie.mov_id,
                    scr_aud_id: auditorium.aud_id,
                    scr_date: "2025-07-03",
                    scr_time: "20:00:00",
                    scr_price: 18.00,
                    scr_status: "scheduled"
                }
            ];
            
            for (const screening of testScreenings) {
                try {
                    const response = await fetch(`${CONFIG.API_BASE_URL}/screenings/`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(screening)
                    });
                    
                    if (response.ok) {
                        const result = await response.json();
                        console.log(`✅ Función creada: ${screening.scr_date} ${screening.scr_time}`);
                    } else {
                        console.log(`❌ Error creando función: ${response.status}`);
                    }
                } catch (error) {
                    console.log(`❌ Error en solicitud: ${error.message}`);
                }
            }
            
            console.log('🎉 Datos de prueba creados. Ejecuta reviewDatabaseRecords() de nuevo para ver los cambios.');
        } else {
            console.log('✅ Ya existen datos suficientes para el booking');
        }
        
    } catch (error) {
        console.error('❌ Error creando datos de prueba:', error);
    }
}

// Exponer funciones globalmente
window.reviewDatabaseRecords = reviewDatabaseRecords;
window.createTestDataIfNeeded = createTestDataIfNeeded;

// Exponer función de test
window.testCreateScreeningTest = testCreateScreeningTest;
