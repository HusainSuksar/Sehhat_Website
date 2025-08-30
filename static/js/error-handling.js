/**
 * Modern Error Handling and User Feedback System
 * Umoor Sehhat Healthcare Management
 */

// ============================================
// NOTIFICATION SYSTEM
// ============================================

class NotificationManager {
    constructor() {
        this.container = this.createContainer();
        this.notifications = new Map();
    }

    createContainer() {
        let container = document.getElementById('notification-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'notification-container';
            container.className = 'notification-container';
            container.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                z-index: 9999;
                max-width: 400px;
                width: 100%;
            `;
            document.body.appendChild(container);
        }
        return container;
    }

    show(message, type = 'info', duration = 5000, options = {}) {
        const id = Date.now() + Math.random();
        const notification = this.createNotification(id, message, type, options, duration);
        
        this.container.appendChild(notification);
        this.notifications.set(id, notification);

        // Animate in
        requestAnimationFrame(() => {
            notification.classList.add('show');
        });

        // Auto remove
        if (duration > 0) {
            setTimeout(() => {
                this.remove(id);
            }, duration);
        }

        return id;
    }

    createNotification(id, message, type, options, duration = 5000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.dataset.id = id;

        const icons = {
            success: '<i class="fas fa-check-circle"></i>',
            error: '<i class="fas fa-exclamation-circle"></i>',
            warning: '<i class="fas fa-exclamation-triangle"></i>',
            info: '<i class="fas fa-info-circle"></i>'
        };

        const colors = {
            success: { bg: '#d1fae5', border: '#059669', text: '#065f46' },
            error: { bg: '#fee2e2', border: '#dc2626', text: '#991b1b' },
            warning: { bg: '#fef3c7', border: '#d97706', text: '#92400e' },
            info: { bg: '#dbeafe', border: '#2563eb', text: '#1e40af' }
        };

        const color = colors[type] || colors.info;

        notification.style.cssText = `
            background: ${color.bg};
            border: 2px solid ${color.border};
            color: ${color.text};
            padding: 16px;
            border-radius: 12px;
            margin-bottom: 12px;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
            display: flex;
            align-items: flex-start;
            gap: 12px;
            transform: translateX(100%);
            opacity: 0;
            transition: all 0.3s ease-out;
            font-size: 14px;
            line-height: 1.5;
            position: relative;
            overflow: hidden;
        `;

        notification.innerHTML = `
            <div class="notification-icon" style="font-size: 18px; margin-top: 2px;">
                ${icons[type] || icons.info}
            </div>
            <div class="notification-content" style="flex: 1;">
                <div class="notification-message" style="font-weight: 500;">
                    ${message}
                </div>
                ${options.description ? `<div class="notification-description" style="margin-top: 4px; opacity: 0.8; font-size: 13px;">${options.description}</div>` : ''}
            </div>
            <button class="notification-close" style="
                background: none;
                border: none;
                font-size: 16px;
                cursor: pointer;
                padding: 0;
                color: inherit;
                opacity: 0.6;
                transition: opacity 0.2s;
            " onclick="notificationManager.remove(${id})">
                <i class="fas fa-times"></i>
            </button>
        `;

        // Add progress bar if duration is set
        if (options.showProgress !== false && options.duration !== 0) {
            const progressBar = document.createElement('div');
            progressBar.style.cssText = `
                position: absolute;
                bottom: 0;
                left: 0;
                height: 3px;
                background: ${color.border};
                opacity: 0.3;
                animation: progressBar ${duration}ms linear;
            `;
            notification.appendChild(progressBar);
        }

        return notification;
    }

    remove(id) {
        const notification = this.notifications.get(id);
        if (notification) {
            notification.style.transform = 'translateX(100%)';
            notification.style.opacity = '0';
            
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
                this.notifications.delete(id);
            }, 300);
        }
    }

    clear() {
        this.notifications.forEach((notification, id) => {
            this.remove(id);
        });
    }

    // Convenience methods
    success(message, options = {}) {
        return this.show(message, 'success', 5000, options);
    }

    error(message, options = {}) {
        return this.show(message, 'error', 0, options); // Don't auto-hide errors
    }

    warning(message, options = {}) {
        return this.show(message, 'warning', 7000, options);
    }

    info(message, options = {}) {
        return this.show(message, 'info', 5000, options);
    }
}

// Global notification manager instance
const notificationManager = new NotificationManager();

// Add CSS for animations
const style = document.createElement('style');
style.textContent = `
    .notification.show {
        transform: translateX(0) !important;
        opacity: 1 !important;
    }
    
    .notification-close:hover {
        opacity: 1 !important;
    }
    
    @keyframes progressBar {
        from { width: 100%; }
        to { width: 0%; }
    }
`;
document.head.appendChild(style);

// ============================================
// FORM VALIDATION SYSTEM
// ============================================

class FormValidator {
    constructor(form, options = {}) {
        this.form = form;
        this.options = {
            showInline: true,
            showSummary: false,
            validateOnInput: true,
            validateOnBlur: true,
            ...options
        };
        this.errors = new Map();
        this.init();
    }

    init() {
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        if (this.options.validateOnInput) {
            this.form.addEventListener('input', (e) => this.handleInput(e));
        }
        
        if (this.options.validateOnBlur) {
            this.form.addEventListener('blur', (e) => this.handleBlur(e), true);
        }
    }

    handleSubmit(e) {
        e.preventDefault();
        
        if (this.validateAll()) {
            this.showLoading();
            this.submitForm();
        } else {
            this.showValidationSummary();
        }
    }

    handleInput(e) {
        if (e.target.matches('input, select, textarea')) {
            this.validateField(e.target);
        }
    }

    handleBlur(e) {
        if (e.target.matches('input, select, textarea')) {
            this.validateField(e.target);
        }
    }

    validateAll() {
        const fields = this.form.querySelectorAll('input, select, textarea');
        let isValid = true;

        fields.forEach(field => {
            if (!this.validateField(field)) {
                isValid = false;
            }
        });

        return isValid;
    }

    validateField(field) {
        const rules = this.getValidationRules(field);
        const errors = [];

        // Required validation
        if (rules.required && !field.value.trim()) {
            errors.push(`${this.getFieldLabel(field)} is required`);
        }

        // Only validate other rules if field has value
        if (field.value.trim()) {
            // Email validation
            if (rules.email && !this.isValidEmail(field.value)) {
                errors.push('Please enter a valid email address');
            }

            // Phone validation
            if (rules.phone && !this.isValidPhone(field.value)) {
                errors.push('Please enter a valid phone number');
            }

            // Min length validation
            if (rules.minLength && field.value.length < rules.minLength) {
                errors.push(`Minimum ${rules.minLength} characters required`);
            }

            // Max length validation
            if (rules.maxLength && field.value.length > rules.maxLength) {
                errors.push(`Maximum ${rules.maxLength} characters allowed`);
            }

            // Pattern validation
            if (rules.pattern && !rules.pattern.test(field.value)) {
                errors.push(rules.patternMessage || 'Invalid format');
            }

            // Custom validation
            if (rules.custom) {
                const customError = rules.custom(field.value);
                if (customError) {
                    errors.push(customError);
                }
            }
        }

        // Update field state
        this.updateFieldState(field, errors);
        
        return errors.length === 0;
    }

    getValidationRules(field) {
        const rules = {};
        
        // HTML5 attributes
        if (field.required) rules.required = true;
        if (field.type === 'email') rules.email = true;
        if (field.type === 'tel') rules.phone = true;
        if (field.minLength) rules.minLength = parseInt(field.minLength);
        if (field.maxLength) rules.maxLength = parseInt(field.maxLength);
        if (field.pattern) rules.pattern = new RegExp(field.pattern);

        // Custom data attributes
        if (field.dataset.required) rules.required = true;
        if (field.dataset.email) rules.email = true;
        if (field.dataset.phone) rules.phone = true;
        if (field.dataset.minLength) rules.minLength = parseInt(field.dataset.minLength);
        if (field.dataset.maxLength) rules.maxLength = parseInt(field.dataset.maxLength);
        if (field.dataset.pattern) rules.pattern = new RegExp(field.dataset.pattern);
        if (field.dataset.patternMessage) rules.patternMessage = field.dataset.patternMessage;

        return rules;
    }

    getFieldLabel(field) {
        const label = field.labels && field.labels[0];
        return label ? label.textContent.replace('*', '').trim() : field.name || field.id || 'Field';
    }

    updateFieldState(field, errors) {
        const fieldGroup = field.closest('.form-group, .mb-3, .form-group-modern');
        const isValid = errors.length === 0;

        // Update field classes
        field.classList.toggle('is-invalid', !isValid);
        field.classList.toggle('is-valid', isValid && field.value.trim());

        // Update error display
        if (this.options.showInline) {
            this.updateInlineErrors(field, errors);
        }

        // Store errors
        if (errors.length > 0) {
            this.errors.set(field.name || field.id, errors);
        } else {
            this.errors.delete(field.name || field.id);
        }
    }

    updateInlineErrors(field, errors) {
        const fieldGroup = field.closest('.form-group, .mb-3, .form-group-modern');
        let errorContainer = fieldGroup?.querySelector('.invalid-feedback, .form-error-message');

        if (errors.length > 0) {
            if (!errorContainer) {
                errorContainer = document.createElement('div');
                errorContainer.className = 'invalid-feedback form-error-message';
                errorContainer.style.cssText = 'display: block; margin-top: 4px; font-size: 14px; color: #dc2626;';
                field.parentNode.appendChild(errorContainer);
            }
            errorContainer.textContent = errors[0];
            errorContainer.style.display = 'block';
        } else if (errorContainer) {
            errorContainer.style.display = 'none';
        }
    }

    showValidationSummary() {
        if (this.errors.size === 0) return;

        const errorMessages = Array.from(this.errors.values()).flat();
        const summary = `Please fix the following errors:\n• ${errorMessages.join('\n• ')}`;
        
        notificationManager.error('Form Validation Failed', {
            description: summary.replace(/\n/g, '<br>')
        });
    }

    showLoading() {
        const submitBtn = this.form.querySelector('[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
        }
    }

    hideLoading() {
        const submitBtn = this.form.querySelector('[type="submit"]');
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = submitBtn.dataset.originalText || 'Submit';
        }
    }

    async submitForm() {
        try {
            const formData = new FormData(this.form);
            const response = await fetch(this.form.action || window.location.href, {
                method: this.form.method || 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': this.getCSRFToken()
                }
            });

            const result = await response.json();

            if (response.ok) {
                this.handleSuccess(result);
            } else {
                this.handleError(result);
            }
        } catch (error) {
            this.handleError({ message: 'Network error occurred. Please try again.' });
        } finally {
            this.hideLoading();
        }
    }

    handleSuccess(result) {
        notificationManager.success(
            result.message || 'Form submitted successfully!',
            { description: result.description }
        );

        if (result.redirect) {
            setTimeout(() => {
                window.location.href = result.redirect;
            }, 1500);
        } else if (this.options.resetOnSuccess !== false) {
            this.form.reset();
        }
    }

    handleError(result) {
        if (result.errors) {
            // Handle field-specific errors
            Object.entries(result.errors).forEach(([field, errors]) => {
                const fieldElement = this.form.querySelector(`[name="${field}"]`);
                if (fieldElement) {
                    this.updateFieldState(fieldElement, Array.isArray(errors) ? errors : [errors]);
                }
            });
        }

        notificationManager.error(
            result.message || 'An error occurred while processing your request.',
            { description: result.description }
        );
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    // Validation helper methods
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }

    isValidPhone(phone) {
        const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
        return phoneRegex.test(phone.replace(/[\s\-\(\)]/g, ''));
    }
}

// ============================================
// AJAX ERROR HANDLING
// ============================================

// Global AJAX error handler
document.addEventListener('DOMContentLoaded', function() {
    // Handle all AJAX errors
    const originalFetch = window.fetch;
    window.fetch = async function(...args) {
        try {
            const response = await originalFetch.apply(this, args);
            
            // Handle HTTP errors
            if (!response.ok) {
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    const errorData = await response.json();
                    throw new Error(errorData.message || `HTTP Error: ${response.status}`);
                } else {
                    throw new Error(`HTTP Error: ${response.status} ${response.statusText}`);
                }
            }
            
            return response;
        } catch (error) {
            console.error('Fetch error:', error);
            
            if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
                notificationManager.error('Network Error', {
                    description: 'Please check your internet connection and try again.'
                });
            } else {
                notificationManager.error('Request Failed', {
                    description: error.message
                });
            }
            
            throw error;
        }
    };
});

// ============================================
// AUTO-INITIALIZATION
// ============================================

document.addEventListener('DOMContentLoaded', function() {
    // Auto-initialize form validation
    const forms = document.querySelectorAll('form[data-validate]');
    forms.forEach(form => {
        new FormValidator(form);
    });

    // Store original button text for loading states
    const submitButtons = document.querySelectorAll('[type="submit"]');
    submitButtons.forEach(btn => {
        btn.dataset.originalText = btn.textContent;
    });
});

// ============================================
// GLOBAL ERROR HANDLER
// ============================================

window.addEventListener('error', function(e) {
    console.error('Global error:', e.error);
    console.error('Error details:', {
        message: e.message,
        filename: e.filename,
        lineno: e.lineno,
        colno: e.colno,
        stack: e.error?.stack
    });
    
    // Temporarily show detailed error instead of generic message
    notificationManager.error('JavaScript Error Detected', {
        description: `${e.message} at ${e.filename}:${e.lineno}:${e.colno}`
    });
});

window.addEventListener('unhandledrejection', function(e) {
    console.error('Unhandled promise rejection:', e.reason);
    notificationManager.error('Request Failed', {
        description: 'A request failed to complete. Please try again.'
    });
});

// ============================================
// UTILITY FUNCTIONS
// ============================================

// Show confirmation dialog
function showConfirmDialog(message, callback) {
    const dialog = document.createElement('div');
    dialog.className = 'modal fade';
    dialog.innerHTML = `
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Confirm Action</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <p>${message}</p>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-danger" id="confirmAction">Confirm</button>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(dialog);
    const modal = new bootstrap.Modal(dialog);
    
    dialog.querySelector('#confirmAction').addEventListener('click', () => {
        callback();
        modal.hide();
    });

    dialog.addEventListener('hidden.bs.modal', () => {
        document.body.removeChild(dialog);
    });

    modal.show();
}

// Export for global use
window.notificationManager = notificationManager;
window.FormValidator = FormValidator;
window.showConfirmDialog = showConfirmDialog;