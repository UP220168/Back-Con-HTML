// Manejo de navegación
class Navigation {
    constructor() {
        this.currentPage = 'dashboard';
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialPage();
    }

    setupEventListeners() {
        // Navegación del header
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.dataset.page;
                this.navigateTo(page);
            });
        });

        // Navegación del sidebar
        document.querySelectorAll('.sidebar-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.dataset.page;
                this.navigateTo(page);
            });
        });

        // Manejo del historial del navegador
        window.addEventListener('popstate', () => {
            this.loadFromUrl();
        });
    }

    navigateTo(page) {
        if (page === this.currentPage) return;

        log(`Navigating to page: ${page}`);

        // Actualizar estado
        this.currentPage = page;

        // Actualizar URL
        const url = page === 'dashboard' ? '/' : `#${page}`;
        history.pushState({ page }, '', url);

        // Mostrar página
        this.showPage(page);

        // Actualizar navegación activa
        this.updateActiveNavigation(page);

        // Cargar datos de la página si es necesario
        this.loadPageData(page);
    }

    showPage(page) {
        // Ocultar todas las páginas
        document.querySelectorAll('.page').forEach(pageEl => {
            pageEl.classList.remove('active');
        });

        // Mostrar página seleccionada
        const pageElement = document.getElementById(`${page}-page`);
        if (pageElement) {
            pageElement.classList.add('active');
        } else {
            log(`Page element not found: ${page}-page`, 'warn');
            // Fallback al dashboard
            document.getElementById('dashboard-page').classList.add('active');
        }
    }

    updateActiveNavigation(page) {
        // Actualizar header navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.page === page) {
                link.classList.add('active');
            }
        });

        // Actualizar sidebar navigation
        document.querySelectorAll('.sidebar-link').forEach(link => {
            link.classList.remove('active');
            if (link.dataset.page === page) {
                link.classList.add('active');
            }
        });
    }

    loadPageData(page) {
        switch (page) {
            case 'dashboard':
                if (window.Dashboard) {
                    Dashboard.loadData();
                }
                break;
            case 'booking':
                if (window.Booking) {
                    Booking.loadData();
                }
                break;
            case 'movies':
                if (window.Movies) {
                    Movies.loadData();
                }
                break;
            case 'screenings':
                if (window.Screenings) {
                    Screenings.loadData();
                }
                break;
            case 'auth':
                if (window.Auth) {
                    Auth.init();
                }
                break;
            default:
                log(`No data loader defined for page: ${page}`, 'info');
        }
    }

    loadInitialPage() {
        this.loadFromUrl();
    }

    loadFromUrl() {
        const hash = window.location.hash.substring(1);
        const page = hash || 'dashboard';
        
        this.currentPage = page;
        this.showPage(page);
        this.updateActiveNavigation(page);
        this.loadPageData(page);
    }

    getCurrentPage() {
        return this.currentPage;
    }
}

// Función para mostrar/ocultar loading
function showLoading(show = true) {
    const loadingEl = document.getElementById('loading');
    if (loadingEl) {
        loadingEl.style.display = show ? 'flex' : 'none';
    }
}

// Función para mostrar modal
function showModal(content, title = '') {
    const modal = document.getElementById('modal');
    const modalBody = document.getElementById('modal-body');
    
    if (title) {
        modalBody.innerHTML = `<h3>${title}</h3><div>${content}</div>`;
    } else {
        modalBody.innerHTML = content;
    }
    
    modal.style.display = 'flex';
    
    // Cerrar modal al hacer clic en la X o fuera del modal
    const closeBtn = modal.querySelector('.close');
    const handleClose = () => {
        modal.style.display = 'none';
        closeBtn.removeEventListener('click', handleClose);
        modal.removeEventListener('click', handleOutsideClick);
    };
    
    const handleOutsideClick = (e) => {
        if (e.target === modal) {
            handleClose();
        }
    };
    
    closeBtn.addEventListener('click', handleClose);
    modal.addEventListener('click', handleOutsideClick);
}

// Función para formatear números como moneda
function formatCurrency(amount, currency = 'MXN') {
    return new Intl.NumberFormat('es-MX', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 2
    }).format(amount);
}

// Función para formatear fechas
function formatDate(date, format = 'DD/MM/YYYY') {
    if (!date) return '-';
    
    const d = new Date(date);
    if (isNaN(d.getTime())) return '-';
    
    return d.toLocaleDateString('es-ES');
}

// Función para formatear tiempo
function formatTime(time) {
    if (!time) return '-';
    
    // Si es un string de tiempo (HH:MM:SS)
    if (typeof time === 'string' && time.includes(':')) {
        return time.substring(0, 5); // Devolver solo HH:MM
    }
    
    return time;
}

// Inicializar navegación cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.navigation = new Navigation();
});
