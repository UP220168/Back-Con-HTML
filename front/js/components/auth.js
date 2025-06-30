// Componente de Autenticación
class Auth {
    constructor() {
        this.isLoginMode = true;
        this.init();
    }

    init() {
        log('Initializing Auth component');
        this.setupEventListeners();
        this.checkAuthStatus();
    }

    setupEventListeners() {
        // Form submission
        const authForm = document.getElementById('auth-form');
        if (authForm) {
            authForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmit();
            });
        }

        // Switch between login/register
        const switchLink = document.getElementById('auth-switch-link');
        if (switchLink) {
            switchLink.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleMode();
            });
        }

        // Logout button
        const logoutBtn = document.getElementById('logout-btn');
        if (logoutBtn) {
            logoutBtn.addEventListener('click', () => {
                this.logout();
            });
        }
    }

    toggleMode() {
        this.isLoginMode = !this.isLoginMode;
        this.updateUI();
    }

    updateUI() {
        const title = document.getElementById('auth-title');
        const submitBtn = document.getElementById('auth-submit');
        const switchText = document.getElementById('auth-switch-text');
        const switchLink = document.getElementById('auth-switch-link');
        const nameGroup = document.getElementById('name-group');
        const phoneGroup = document.getElementById('phone-group');

        if (this.isLoginMode) {
            title.textContent = 'Iniciar Sesión';
            submitBtn.textContent = 'Iniciar Sesión';
            switchText.textContent = '¿No tienes cuenta?';
            switchLink.textContent = 'Registrarse';
            nameGroup.style.display = 'none';
            phoneGroup.style.display = 'none';
        } else {
            title.textContent = 'Registrarse';
            submitBtn.textContent = 'Registrarse';
            switchText.textContent = '¿Ya tienes cuenta?';
            switchLink.textContent = 'Iniciar Sesión';
            nameGroup.style.display = 'block';
            phoneGroup.style.display = 'block';
        }
    }

    async handleFormSubmit() {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        if (!email || !password) {
            this.showError('Por favor completa todos los campos requeridos');
            return;
        }

        try {
            showLoading(true);

            if (this.isLoginMode) {
                await this.login(email, password);
            } else {
                const name = document.getElementById('name').value;
                const phone = document.getElementById('phone').value;
                
                if (!name || !phone) {
                    this.showError('Por favor completa todos los campos');
                    return;
                }

                await this.register(email, password, name, phone);
            }

        } catch (error) {
            log('Auth error', 'error', error);
            this.showError(error.message || 'Error en la autenticación');
        } finally {
            showLoading(false);
        }
    }

    async login(email, password) {
        try {
            log('Attempting login...');
            
            // Llamar a la API de login
            const response = await AuthAPI.login(email, password);
            
            if (response.access_token) {
                // Guardar token y datos del usuario
                UserStorage.setAuthToken(response.access_token);
                UserStorage.setUser({
                    id: response.user.usr_id,
                    email: response.user.usr_email,
                    name: response.user.usr_name,
                    phone: response.user.usr_phone
                });

                this.showSuccess('¡Inicio de sesión exitoso!');
                
                // Redirigir al dashboard
                setTimeout(() => {
                    window.navigation.navigateTo('dashboard');
                    this.updateAuthUI();
                }, 1000);

            } else {
                throw new Error('No se recibió token de autenticación');
            }

        } catch (error) {
            throw new Error('Email o contraseña incorrectos');
        }
    }

    async register(email, password, name, phone) {
        try {
            log('Attempting registration...');

            const userData = {
                usr_email: email,
                usr_password: password,
                usr_name: name,
                usr_phone: phone
            };

            const response = await AuthAPI.register(userData);
            
            this.showSuccess('¡Registro exitoso! Ya puedes iniciar sesión.');
            
            // Cambiar a modo login
            setTimeout(() => {
                this.isLoginMode = true;
                this.updateUI();
                this.clearForm();
            }, 1500);

        } catch (error) {
            throw new Error('Error en el registro: ' + error.message);
        }
    }

    logout() {
        UserStorage.logout();
        this.updateAuthUI();
        window.navigation.navigateTo('auth');
        this.showSuccess('Sesión cerrada correctamente');
    }

    checkAuthStatus() {
        if (UserStorage.isLoggedIn()) {
            this.updateAuthUI();
        }
    }

    updateAuthUI() {
        const userNameEl = document.getElementById('user-name');
        const logoutBtn = document.getElementById('logout-btn');
        
        if (UserStorage.isLoggedIn()) {
            const user = UserStorage.getUser();
            if (userNameEl) {
                userNameEl.textContent = user.name || user.email;
            }
            if (logoutBtn) {
                logoutBtn.style.display = 'block';
            }
        } else {
            if (userNameEl) {
                userNameEl.textContent = 'Usuario';
            }
            if (logoutBtn) {
                logoutBtn.style.display = 'none';
            }
        }
    }

    clearForm() {
        document.getElementById('email').value = '';
        document.getElementById('password').value = '';
        document.getElementById('name').value = '';
        document.getElementById('phone').value = '';
    }

    showError(message) {
        showModal(`
            <div style="text-align: center; padding: 20px;">
                <div style="color: #e74c3c; font-size: 3rem; margin-bottom: 15px;">❌</div>
                <h3 style="color: #e74c3c; margin-bottom: 10px;">Error</h3>
                <p>${message}</p>
            </div>
        `);
    }

    showSuccess(message) {
        showModal(`
            <div style="text-align: center; padding: 20px;">
                <div style="color: #27ae60; font-size: 3rem; margin-bottom: 15px;">✅</div>
                <h3 style="color: #27ae60; margin-bottom: 10px;">Éxito</h3>
                <p>${message}</p>
            </div>
        `);
    }
}

// Crear instancia global
window.Auth = new Auth();
