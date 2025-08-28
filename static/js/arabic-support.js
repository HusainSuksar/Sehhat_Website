/**
 * Arabic Language Support System
 * Umoor Sehhat Healthcare Management
 */

// ============================================
// ARABIC LANGUAGE MANAGER
// ============================================

class ArabicLanguageManager {
    constructor() {
        this.currentLanguage = localStorage.getItem('preferred-language') || 'en';
        this.translations = new Map();
        this.init();
    }

    init() {
        this.loadTranslations();
        this.setupLanguageToggle();
        this.applyLanguage(this.currentLanguage);
    }

    loadTranslations() {
        // Common UI translations
        this.translations.set('en', {
            // Navigation
            'Dashboard': 'Dashboard',
            'Appointments': 'Appointments',
            'Patients': 'Patients',
            'Schedule': 'Schedule',
            'Analytics': 'Analytics',
            'Profile': 'Profile',
            'Logout': 'Logout',
            'Login': 'Login',
            
            // Common Actions
            'Save': 'Save',
            'Cancel': 'Cancel',
            'Delete': 'Delete',
            'Edit': 'Edit',
            'View': 'View',
            'Add': 'Add',
            'Search': 'Search',
            'Filter': 'Filter',
            'Export': 'Export',
            'Print': 'Print',
            
            // Status
            'Active': 'Active',
            'Inactive': 'Inactive',
            'Pending': 'Pending',
            'Completed': 'Completed',
            'Scheduled': 'Scheduled',
            'Cancelled': 'Cancelled',
            
            // Forms
            'Name': 'Name',
            'Email': 'Email',
            'Phone': 'Phone',
            'Address': 'Address',
            'Date': 'Date',
            'Time': 'Time',
            'Notes': 'Notes',
            'Required': 'Required',
            
            // Messages
            'Success': 'Success',
            'Error': 'Error',
            'Warning': 'Warning',
            'Information': 'Information',
            'Loading': 'Loading...',
            'Please wait': 'Please wait...',
            'Are you sure?': 'Are you sure?',
            'Confirm': 'Confirm',
            
            // Medical Terms
            'Doctor': 'Doctor',
            'Patient': 'Patient',
            'Appointment': 'Appointment',
            'Medical Record': 'Medical Record',
            'Prescription': 'Prescription',
            'Diagnosis': 'Diagnosis',
            'Treatment': 'Treatment',
            'Consultation': 'Consultation',
            'Emergency': 'Emergency',
            'Vital Signs': 'Vital Signs',
            
            // Moze/Admin Terms
            'Moze Center': 'Moze Center',
            'Team Members': 'Team Members',
            'Coordinator': 'Coordinator',
            'Capacity': 'Capacity',
            'Utilization': 'Utilization',
            'Reports': 'Reports',
            'Administration': 'Administration'
        });

        this.translations.set('ar', {
            // Navigation
            'Dashboard': 'لوحة التحكم',
            'Appointments': 'المواعيد',
            'Patients': 'المرضى',
            'Schedule': 'الجدول الزمني',
            'Analytics': 'التحليلات',
            'Profile': 'الملف الشخصي',
            'Logout': 'تسجيل الخروج',
            'Login': 'تسجيل الدخول',
            
            // Common Actions
            'Save': 'حفظ',
            'Cancel': 'إلغاء',
            'Delete': 'حذف',
            'Edit': 'تعديل',
            'View': 'عرض',
            'Add': 'إضافة',
            'Search': 'بحث',
            'Filter': 'تصفية',
            'Export': 'تصدير',
            'Print': 'طباعة',
            
            // Status
            'Active': 'نشط',
            'Inactive': 'غير نشط',
            'Pending': 'في الانتظار',
            'Completed': 'مكتمل',
            'Scheduled': 'مجدول',
            'Cancelled': 'ملغي',
            
            // Forms
            'Name': 'الاسم',
            'Email': 'البريد الإلكتروني',
            'Phone': 'الهاتف',
            'Address': 'العنوان',
            'Date': 'التاريخ',
            'Time': 'الوقت',
            'Notes': 'ملاحظات',
            'Required': 'مطلوب',
            
            // Messages
            'Success': 'نجح',
            'Error': 'خطأ',
            'Warning': 'تحذير',
            'Information': 'معلومات',
            'Loading': 'جاري التحميل...',
            'Please wait': 'يرجى الانتظار...',
            'Are you sure?': 'هل أنت متأكد؟',
            'Confirm': 'تأكيد',
            
            // Medical Terms
            'Doctor': 'طبيب',
            'Patient': 'مريض',
            'Appointment': 'موعد',
            'Medical Record': 'السجل الطبي',
            'Prescription': 'وصفة طبية',
            'Diagnosis': 'التشخيص',
            'Treatment': 'العلاج',
            'Consultation': 'استشارة',
            'Emergency': 'طوارئ',
            'Vital Signs': 'العلامات الحيوية',
            
            // Moze/Admin Terms
            'Moze Center': 'مركز موزة',
            'Team Members': 'أعضاء الفريق',
            'Coordinator': 'منسق',
            'Capacity': 'السعة',
            'Utilization': 'الاستخدام',
            'Reports': 'التقارير',
            'Administration': 'الإدارة'
        });
    }

    setupLanguageToggle() {
        // Create language toggle button
        const navbar = document.querySelector('.navbar-nav');
        if (navbar) {
            const langToggle = document.createElement('li');
            langToggle.className = 'nav-item dropdown';
            langToggle.innerHTML = `
                <a class="nav-link dropdown-toggle" href="#" id="languageDropdown" role="button" data-bs-toggle="dropdown">
                    <i class="fas fa-globe me-1"></i>
                    <span id="currentLangText">${this.currentLanguage === 'ar' ? 'العربية' : 'English'}</span>
                </a>
                <ul class="dropdown-menu">
                    <li><a class="dropdown-item" href="#" onclick="arabicManager.switchLanguage('en')">
                        <i class="fas fa-flag-usa me-2"></i>English
                    </a></li>
                    <li><a class="dropdown-item" href="#" onclick="arabicManager.switchLanguage('ar')">
                        <i class="fas fa-flag me-2"></i>العربية
                    </a></li>
                </ul>
            `;
            
            // Insert before the user dropdown
            const userDropdown = navbar.querySelector('.nav-item.dropdown');
            if (userDropdown) {
                navbar.insertBefore(langToggle, userDropdown);
            } else {
                navbar.appendChild(langToggle);
            }
        }
    }

    switchLanguage(lang) {
        if (lang !== this.currentLanguage) {
            this.currentLanguage = lang;
            localStorage.setItem('preferred-language', lang);
            this.applyLanguage(lang);
            
            // Show notification
            const message = lang === 'ar' ? 'تم تغيير اللغة إلى العربية' : 'Language changed to English';
            if (window.notificationManager) {
                window.notificationManager.success(message);
            }
        }
    }

    applyLanguage(lang) {
        const isArabic = lang === 'ar';
        const body = document.body;
        const html = document.documentElement;

        // Set document direction and language
        html.setAttribute('lang', lang);
        html.setAttribute('dir', isArabic ? 'rtl' : 'ltr');
        body.classList.toggle('rtl', isArabic);
        body.classList.toggle('arabic', isArabic);

        // Apply font family
        if (isArabic) {
            body.style.fontFamily = "'Noto Sans Arabic', 'Cairo', Arial, sans-serif";
        } else {
            body.style.fontFamily = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
        }

        // Update current language text
        const currentLangText = document.getElementById('currentLangText');
        if (currentLangText) {
            currentLangText.textContent = isArabic ? 'العربية' : 'English';
        }

        // Translate elements with data-translate attribute
        this.translateElements();

        // Apply RTL styles
        this.applyRTLStyles(isArabic);

        // Update form placeholders and labels
        this.updateFormElements(lang);
    }

    translateElements() {
        const elements = document.querySelectorAll('[data-translate]');
        const translations = this.translations.get(this.currentLanguage) || this.translations.get('en');

        elements.forEach(element => {
            const key = element.getAttribute('data-translate');
            if (translations[key]) {
                element.textContent = translations[key];
            }
        });
    }

    applyRTLStyles(isRTL) {
        let rtlStyles = document.getElementById('rtl-styles');
        
        if (isRTL) {
            if (!rtlStyles) {
                rtlStyles = document.createElement('style');
                rtlStyles.id = 'rtl-styles';
                document.head.appendChild(rtlStyles);
            }

            rtlStyles.textContent = `
                /* RTL Layout Adjustments */
                .rtl .navbar-brand {
                    margin-right: 0;
                    margin-left: auto;
                }
                
                .rtl .nav-link {
                    text-align: right;
                }
                
                .rtl .dropdown-menu {
                    right: 0;
                    left: auto;
                }
                
                .rtl .sidebar {
                    right: 0;
                    left: auto;
                }
                
                .rtl .main-content {
                    margin-right: 280px;
                    margin-left: 0;
                }
                
                @media (max-width: 991.98px) {
                    .rtl .sidebar {
                        right: -100%;
                        left: auto;
                    }
                    
                    .rtl .sidebar.show {
                        right: 0;
                    }
                    
                    .rtl .main-content {
                        margin-right: 0;
                    }
                }
                
                /* Form RTL adjustments */
                .rtl .form-control {
                    text-align: right;
                }
                
                .rtl .input-group-text {
                    border-radius: 0 0.375rem 0.375rem 0;
                }
                
                .rtl .input-group .form-control:not(:last-child) {
                    border-radius: 0.375rem 0 0 0.375rem;
                }
                
                /* Table RTL adjustments */
                .rtl .table th,
                .rtl .table td {
                    text-align: right;
                }
                
                /* Card RTL adjustments */
                .rtl .card-header {
                    text-align: right;
                }
                
                /* Button RTL adjustments */
                .rtl .btn i {
                    margin-right: 0;
                    margin-left: 0.5rem;
                }
                
                /* Navigation RTL adjustments */
                .rtl .nav-item-modern {
                    text-align: right;
                }
                
                .rtl .nav-item-modern:hover {
                    transform: translateX(-4px);
                }
                
                .rtl .nav-item-modern .icon {
                    order: 2;
                }
                
                /* Statistics cards RTL */
                .rtl .stats-card {
                    text-align: right;
                }
                
                /* Notification RTL */
                .rtl .notification-container {
                    right: auto;
                    left: 20px;
                }
                
                .rtl .notification {
                    transform: translateX(-100%);
                }
                
                .rtl .notification.show {
                    transform: translateX(0);
                }
                
                /* Arabic text improvements */
                .arabic {
                    line-height: 1.8;
                }
                
                .arabic h1, .arabic h2, .arabic h3, .arabic h4, .arabic h5, .arabic h6 {
                    font-weight: 600;
                    line-height: 1.6;
                }
                
                .arabic .btn {
                    font-weight: 500;
                }
                
                .arabic .form-label {
                    font-weight: 500;
                }
                
                /* Fix for Arabic numbers */
                .arabic .stats-card-number,
                .arabic .badge,
                .arabic .table td[data-type="number"] {
                    font-family: 'Inter', sans-serif;
                    direction: ltr;
                    display: inline-block;
                }
            `;
        } else if (rtlStyles) {
            rtlStyles.remove();
        }
    }

    updateFormElements(lang) {
        const isArabic = lang === 'ar';
        const translations = this.translations.get(lang) || this.translations.get('en');

        // Update form labels
        document.querySelectorAll('label').forEach(label => {
            const text = label.textContent.trim().replace('*', '');
            if (translations[text]) {
                label.textContent = translations[text];
                if (label.querySelector('.required') || text.includes('*')) {
                    label.innerHTML += ' <span class="text-danger">*</span>';
                }
            }
        });

        // Update placeholders
        document.querySelectorAll('input, textarea, select').forEach(input => {
            if (input.placeholder) {
                const placeholder = input.placeholder;
                if (translations[placeholder]) {
                    input.placeholder = translations[placeholder];
                }
            }
        });

        // Update button text
        document.querySelectorAll('button, .btn').forEach(btn => {
            const text = btn.textContent.trim();
            if (translations[text]) {
                const icon = btn.querySelector('i');
                btn.textContent = translations[text];
                if (icon) {
                    if (isArabic) {
                        btn.appendChild(icon); // Move icon to end for Arabic
                    } else {
                        btn.insertBefore(icon, btn.firstChild); // Move icon to start for English
                    }
                }
            }
        });
    }

    // Utility method to get translation
    translate(key, lang = null) {
        const targetLang = lang || this.currentLanguage;
        const translations = this.translations.get(targetLang) || this.translations.get('en');
        return translations[key] || key;
    }

    // Method to add custom translations
    addTranslations(lang, translations) {
        const existing = this.translations.get(lang) || {};
        this.translations.set(lang, { ...existing, ...translations });
    }

    // Format numbers for Arabic (preserve English numerals)
    formatNumber(number) {
        if (this.currentLanguage === 'ar') {
            return number.toLocaleString('en-US'); // Use English numerals even in Arabic
        }
        return number.toLocaleString();
    }

    // Format dates for Arabic
    formatDate(date, options = {}) {
        const locale = this.currentLanguage === 'ar' ? 'ar-SA' : 'en-US';
        return new Intl.DateTimeFormat(locale, {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            ...options
        }).format(date);
    }

    // Format currency
    formatCurrency(amount, currency = 'USD') {
        const locale = this.currentLanguage === 'ar' ? 'ar-SA' : 'en-US';
        return new Intl.NumberFormat(locale, {
            style: 'currency',
            currency: currency
        }).format(amount);
    }
}

// ============================================
// AUTO-INITIALIZATION
// ============================================

let arabicManager;

document.addEventListener('DOMContentLoaded', function() {
    arabicManager = new ArabicLanguageManager();
    
    // Make available globally
    window.arabicManager = arabicManager;
    
    // Add translate attributes to common elements
    setTimeout(() => {
        // Auto-add translate attributes to common elements
        document.querySelectorAll('h1, h2, h3, h4, h5, h6').forEach(heading => {
            if (!heading.hasAttribute('data-translate')) {
                const text = heading.textContent.trim();
                if (text && arabicManager.translations.get('en')[text]) {
                    heading.setAttribute('data-translate', text);
                }
            }
        });
        
        // Re-translate after adding attributes
        arabicManager.translateElements();
    }, 100);
});

// ============================================
// UTILITY FUNCTIONS FOR TEMPLATES
// ============================================

// Helper function for templates to mark translatable text
function t(key, lang = null) {
    return arabicManager ? arabicManager.translate(key, lang) : key;
}

// Helper function to add translate attribute in templates
function markTranslatable(element, key) {
    if (element && key) {
        element.setAttribute('data-translate', key);
        if (arabicManager) {
            element.textContent = arabicManager.translate(key);
        }
    }
}

// Export for global use
window.t = t;
window.markTranslatable = markTranslatable;