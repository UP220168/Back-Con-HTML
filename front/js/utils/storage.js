// Utilidades para localStorage
class Storage {
    static set(key, value) {
        try {
            const serializedValue = JSON.stringify(value);
            localStorage.setItem(key, serializedValue);
            log(`Stored data in localStorage with key: ${key}`);
        } catch (error) {
            log(`Error storing data in localStorage: ${error.message}`, 'error');
        }
    }

    static get(key, defaultValue = null) {
        try {
            const serializedValue = localStorage.getItem(key);
            if (serializedValue === null) {
                return defaultValue;
            }
            return JSON.parse(serializedValue);
        } catch (error) {
            log(`Error retrieving data from localStorage: ${error.message}`, 'error');
            return defaultValue;
        }
    }

    static remove(key) {
        try {
            localStorage.removeItem(key);
            log(`Removed data from localStorage with key: ${key}`);
        } catch (error) {
            log(`Error removing data from localStorage: ${error.message}`, 'error');
        }
    }

    static clear() {
        try {
            localStorage.clear();
            log('Cleared all localStorage data');
        } catch (error) {
            log(`Error clearing localStorage: ${error.message}`, 'error');
        }
    }

    static exists(key) {
        return localStorage.getItem(key) !== null;
    }
}

// Funciones específicas para manejo de usuario y autenticación
const UserStorage = {
    setUser(userData) {
        Storage.set(CONFIG.STORAGE.USER_KEY, userData);
    },

    getUser() {
        return Storage.get(CONFIG.STORAGE.USER_KEY);
    },

    removeUser() {
        Storage.remove(CONFIG.STORAGE.USER_KEY);
    },

    isLoggedIn() {
        return Storage.exists(CONFIG.STORAGE.USER_KEY) && Storage.exists(CONFIG.STORAGE.AUTH_TOKEN_KEY);
    },

    setAuthToken(token) {
        Storage.set(CONFIG.STORAGE.AUTH_TOKEN_KEY, token);
    },

    getAuthToken() {
        return Storage.get(CONFIG.STORAGE.AUTH_TOKEN_KEY);
    },

    removeAuthToken() {
        Storage.remove(CONFIG.STORAGE.AUTH_TOKEN_KEY);
    },

    logout() {
        this.removeUser();
        this.removeAuthToken();
        log('User logged out - cleared storage');
    }
};

// Funciones para configuraciones de la aplicación
const SettingsStorage = {
    setSettings(settings) {
        const currentSettings = this.getSettings();
        const newSettings = { ...currentSettings, ...settings };
        Storage.set(CONFIG.STORAGE.SETTINGS_KEY, newSettings);
    },

    getSettings() {
        return Storage.get(CONFIG.STORAGE.SETTINGS_KEY, {
            theme: 'light',
            language: 'es',
            dateFormat: 'DD/MM/YYYY',
            currency: 'USD'
        });
    },

    getSetting(key, defaultValue = null) {
        const settings = this.getSettings();
        return settings[key] || defaultValue;
    },

    setSetting(key, value) {
        const settings = this.getSettings();
        settings[key] = value;
        this.setSettings(settings);
    }
};
