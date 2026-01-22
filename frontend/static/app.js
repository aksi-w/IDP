let currentUser = null;
let authToken = null;

const API_URL = '/api';

function saveToken(token) {
    localStorage.setItem('authToken', token);
    authToken = token;
}

function getToken() {
    if (!authToken) {
        authToken = localStorage.getItem('authToken');
    }
    return authToken;
}

function clearToken() {
    localStorage.removeItem('authToken');
    localStorage.removeItem('currentUser');
    authToken = null;
    currentUser = null;
}

function saveUser(user) {
    localStorage.setItem('currentUser', JSON.stringify(user));
    currentUser = user;
}

function getUser() {
    if (!currentUser) {
        const userData = localStorage.getItem('currentUser');
        if (userData) {
            currentUser = JSON.parse(userData);
        }
    }
    return currentUser;
}

async function apiRequest(endpoint, options = {}) {
    const token = getToken();
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const skipAuthRedirect = options.skipAuthRedirect || false;
    
    try {
        const response = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers
        });
        
        if (response.status === 401 && token && !skipAuthRedirect) {
            clearToken();
            window.location.href = '/';
            return;
        }
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка запроса');
        }
        
        const data = await response.json();
        return data;
    } catch (error) {
        throw error;
    }
}

async function checkAuth() {
    const token = getToken();
    if (!token) {
        if (window.location.pathname !== '/') {
            window.location.href = '/';
        }
        return false;
    }
    return true;
}

function logout() {
    clearToken();
    window.location.href = '/';
}

function formatDate(dateString) {
    if (!dateString) return 'Не указано';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function getInitials(fullName) {
    if (!fullName) return '?';
    const names = fullName.trim().split(' ');
    if (names.length >= 2) {
        return (names[0][0] + names[1][0]).toUpperCase();
    }
    return names[0][0].toUpperCase();
}

function showToast(message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'toast-container';
        document.body.appendChild(container);
    }
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    const icons = {
        success: '✓',
        error: '✕',
        warning: '⚠',
        info: 'ℹ'
    };
    
    toast.innerHTML = `
        <div class="toast-icon">${icons[type] || icons.info}</div>
        <div class="toast-message">${message}</div>
        <button class="toast-close" onclick="this.parentElement.remove()">×</button>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => {
            toast.remove();
        }, 300);
    }, 5000);
}

function showNotification(message, type = 'info') {
    showToast(message, type);
}

function showError(error) {
    const message = error.message || 'Произошла ошибка';
    showToast(message, 'error');
}

function showSuccess(message) {
    showToast(message, 'success');
}

function showWarning(message) {
    showToast(message, 'warning');
}

function showFieldError(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    
    field.classList.add('is-invalid');
    field.classList.remove('is-valid');
    
    let errorDiv = field.parentElement.querySelector('.invalid-feedback');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        field.parentElement.appendChild(errorDiv);
    }
    
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function clearFieldError(fieldId) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    
    field.classList.remove('is-invalid');
    
    const errorDiv = field.parentElement.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

function showFieldSuccess(fieldId) {
    const field = document.getElementById(fieldId);
    if (!field) return;
    
    field.classList.add('is-valid');
    field.classList.remove('is-invalid');
    
    const errorDiv = field.parentElement.querySelector('.invalid-feedback');
    if (errorDiv) {
        errorDiv.style.display = 'none';
    }
}

function clearAllErrors(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const invalidFields = form.querySelectorAll('.is-invalid');
    invalidFields.forEach(field => {
        field.classList.remove('is-invalid');
    });
    
    const validFields = form.querySelectorAll('.is-valid');
    validFields.forEach(field => {
        field.classList.remove('is-valid');
    });
    
    const errorDivs = form.querySelectorAll('.invalid-feedback');
    errorDivs.forEach(div => {
        div.style.display = 'none';
    });
}

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePassword(password) {
    return password && password.length >= 6;
}

function validateRequired(value) {
    return value && value.trim().length > 0;
}

function validateFullName(fullName) {
    if (!fullName || !fullName.trim()) return false;
    const words = fullName.trim().split(/\s+/);
    return words.length >= 2;
}

function addInputValidationListeners(formId) {
    const form = document.getElementById(formId);
    if (!form) return;
    
    const inputs = form.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            if (this.classList.contains('is-invalid')) {
                clearFieldError(this.id);
            }
        });
    });
}

function showConfirm(title, message, options = {}) {
    return new Promise((resolve) => {
        const modalId = 'customConfirmModal' + Date.now();
        const confirmBtn = options.confirmText || 'Да';
        const cancelBtn = options.cancelText || 'Отмена';
        const confirmClass = options.confirmClass || 'btn-danger';
        
        const modal = document.createElement('div');
        modal.className = 'modal fade confirm-dialog';
        modal.id = modalId;
        modal.tabIndex = -1;
        modal.innerHTML = `
            <div class="modal-dialog modal-dialog-centered">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <p class="mb-0">${message}</p>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" id="${modalId}-cancel">
                            ${cancelBtn}
                        </button>
                        <button type="button" class="btn ${confirmClass}" id="${modalId}-confirm">
                            ${confirmBtn}
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        const bsModal = new bootstrap.Modal(modal);
        
        document.getElementById(`${modalId}-confirm`).addEventListener('click', () => {
            bsModal.hide();
            resolve(true);
        });
        
        document.getElementById(`${modalId}-cancel`).addEventListener('click', () => {
            bsModal.hide();
            resolve(false);
        });
        
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
        
        bsModal.show();
    });
}


