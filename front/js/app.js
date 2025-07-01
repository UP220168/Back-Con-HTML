// Archivo principal de la aplicación
class App {
    constructor() {
        this.init();
    }

    init() {
        log('Initializing Cinema Management App');
        
        // Verificar que todos los componentes estén cargados
        this.checkDependencies();
        
        // Configurar eventos globales
        this.setupGlobalEvents();
        
        // Verificar estado de autenticación
        this.checkAuthenticationStatus();
        
        log('App initialized successfully');
    }

    checkDependencies() {
        const requiredComponents = [
            'Navigation',
            'Dashboard', 
            'Booking',
            'Movies',
            'Screenings',
            'Auth'
        ];

        const missingComponents = requiredComponents.filter(component => !window[component]);
        
        if (missingComponents.length > 0) {
            log('Missing components:', 'warn', missingComponents);
        } else {
            log('All components loaded successfully');
        }
        
        // Log específico para Screenings
        if (window.Screenings) {
            log('Screenings component is available');
        } else {
            log('Screenings component is missing', 'error');
        }
    }

    setupGlobalEvents() {
        // Manejo de errores no capturados
        window.addEventListener('error', (event) => {
            log('Uncaught error:', 'error', {
                message: event.message,
                filename: event.filename,
                line: event.lineno,
                column: event.colno
            });
        });

        // Manejo de promesas rechazadas
        window.addEventListener('unhandledrejection', (event) => {
            log('Unhandled promise rejection:', 'error', event.reason);
            event.preventDefault();
        });

        // Manejo de cambios de conectividad
        window.addEventListener('online', () => {
            log('Connection restored');
            this.showConnectionStatus(true);
        });

        window.addEventListener('offline', () => {
            log('Connection lost');
            this.showConnectionStatus(false);
        });

        // Manejo de visibilidad de la página
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'visible') {
                this.onPageVisible();
            } else {
                this.onPageHidden();
            }
        });
    }

    checkAuthenticationStatus() {
        if (UserStorage.isLoggedIn()) {
            log('User is logged in');
            if (window.Auth) {
                window.Auth.updateAuthUI();
            }
        } else {
            log('User is not logged in');
        }
    }

    showConnectionStatus(isOnline) {
        const message = isOnline ? 'Conexión restaurada' : 'Sin conexión a internet';
        const type = isOnline ? 'success' : 'warning';
        
        showNotification(message, type);
    }

    onPageVisible() {
        log('Page became visible');
        // Actualizar datos si es necesario
        if (window.AppNavigation && window.AppNavigation.getCurrentPage() === 'dashboard') {
            // Refrescar dashboard cuando la página se vuelve visible
            setTimeout(() => {
                if (window.Dashboard) {
                    window.Dashboard.refresh();
                }
            }, 1000);
        }
    }

    onPageHidden() {
        log('Page became hidden');
        // Pausar timers o procesos si es necesario
    }

    // Método para mostrar notificaciones
    showNotification(message, type = 'info', duration = CONFIG.UI.NOTIFICATION_DURATION) {
        log(`Notification [${type}]: ${message}`);
        
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-icon">${this.getNotificationIcon(type)}</span>
                <span class="notification-message">${message}</span>
                <button class="notification-close">&times;</button>
            </div>
        `;

        // Agregar estilos si no existen
        this.addNotificationStyles();

        // Agregar al DOM
        document.body.appendChild(notification);

        // Auto-remover después del tiempo especificado
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, duration);

        // Permitir cerrar manualmente
        const closeBtn = notification.querySelector('.notification-close');
        closeBtn.addEventListener('click', () => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        });
    }

    getNotificationIcon(type) {
        const icons = {
            success: '✅',
            error: '❌',
            warning: '⚠️',
            info: 'ℹ️'
        };
        return icons[type] || icons.info;
    }

    addNotificationStyles() {
        if (document.getElementById('notification-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'notification-styles';
        styles.textContent = `
            .notification {
                position: fixed;
                top: 90px;
                right: 20px;
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
                z-index: 10001;
                min-width: 300px;
                max-width: 500px;
                animation: slideInRight 0.3s ease;
            }

            .notification-success {
                border-left: 4px solid #27ae60;
            }

            .notification-error {
                border-left: 4px solid #e74c3c;
            }

            .notification-warning {
                border-left: 4px solid #f39c12;
            }

            .notification-info {
                border-left: 4px solid #3498db;
            }

            .notification-content {
                display: flex;
                align-items: center;
                padding: 15px;
                gap: 10px;
            }

            .notification-icon {
                font-size: 1.2rem;
            }

            .notification-message {
                flex: 1;
                font-size: 14px;
                color: #2c3e50;
            }

            .notification-close {
                background: none;
                border: none;
                font-size: 18px;
                color: #7f8c8d;
                cursor: pointer;
                padding: 0;
                width: 20px;
                height: 20px;
                display: flex;
                align-items: center;
                justify-content: center;
            }

            .notification-close:hover {
                color: #2c3e50;
            }

            @keyframes slideInRight {
                from {
                    transform: translateX(100%);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
        `;
        document.head.appendChild(styles);
    }

    // Método para debug
    debug() {
        return {
            config: CONFIG,
            storage: {
                user: UserStorage.getUser(),
                isLoggedIn: UserStorage.isLoggedIn(),
                settings: SettingsStorage.getSettings()
            },
            navigation: window.AppNavigation ? window.AppNavigation.getCurrentPage() : null
        };
    }
}

// Función global para mostrar notificaciones
function showNotification(message, type = 'info') {
    if (window.app) {
        window.app.showNotification(message, type);
    } else {
        console.log(`[${type.toUpperCase()}] ${message}`);
    }
}

// Inicializar aplicación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.app = new App();
    
    // Exponer función de debug globalmente
    window.debug = () => window.app.debug();
    
    log('DOM loaded and app initialized');
});

// Manejar carga completa de la página
window.addEventListener('load', () => {
    log('Page fully loaded');
    
    // Ocultar loading inicial si existe
    showLoading(false);
});
