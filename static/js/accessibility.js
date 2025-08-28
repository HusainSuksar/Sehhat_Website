/**
 * Accessibility Enhancement System
 * Umoor Sehhat Healthcare Management
 * WCAG 2.1 AA Compliant
 */

// ============================================
// ACCESSIBILITY MANAGER
// ============================================

class AccessibilityManager {
    constructor() {
        this.preferences = this.loadPreferences();
        this.focusVisible = true;
        this.highContrast = false;
        this.reducedMotion = false;
        this.largeText = false;
        this.init();
    }

    init() {
        this.setupAccessibilityPanel();
        this.enhanceKeyboardNavigation();
        this.improveScreenReaderSupport();
        this.addFocusManagement();
        this.setupColorContrastEnhancement();
        this.setupMotionReduction();
        this.setupTextSizeControls();
        this.applyStoredPreferences();
        this.monitorSystemPreferences();
    }

    loadPreferences() {
        const stored = localStorage.getItem('accessibility-preferences');
        return stored ? JSON.parse(stored) : {
            highContrast: false,
            reducedMotion: false,
            largeText: false,
            focusVisible: true,
            announcements: true
        };
    }

    savePreferences() {
        localStorage.setItem('accessibility-preferences', JSON.stringify(this.preferences));
    }

    setupAccessibilityPanel() {
        // Create accessibility toggle button
        const accessibilityBtn = document.createElement('button');
        accessibilityBtn.id = 'accessibility-toggle';
        accessibilityBtn.className = 'accessibility-toggle';
        accessibilityBtn.setAttribute('aria-label', 'Open accessibility options');
        accessibilityBtn.innerHTML = '<i class="fas fa-universal-access" aria-hidden="true"></i>';
        
        accessibilityBtn.style.cssText = `
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background: #2563eb;
            color: white;
            border: none;
            border-radius: 50%;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
            cursor: pointer;
            z-index: 1000;
            font-size: 24px;
            transition: all 0.3s ease;
        `;

        // Create accessibility panel
        const panel = document.createElement('div');
        panel.id = 'accessibility-panel';
        panel.className = 'accessibility-panel';
        panel.setAttribute('role', 'dialog');
        panel.setAttribute('aria-labelledby', 'accessibility-title');
        panel.setAttribute('aria-hidden', 'true');
        
        panel.innerHTML = `
            <div class="accessibility-panel-content">
                <div class="accessibility-panel-header">
                    <h3 id="accessibility-title">Accessibility Options</h3>
                    <button class="accessibility-close" aria-label="Close accessibility panel">
                        <i class="fas fa-times" aria-hidden="true"></i>
                    </button>
                </div>
                <div class="accessibility-panel-body">
                    <div class="accessibility-option">
                        <label class="accessibility-label">
                            <input type="checkbox" id="high-contrast-toggle" ${this.preferences.highContrast ? 'checked' : ''}>
                            <span class="accessibility-text">High Contrast</span>
                            <span class="accessibility-description">Increases color contrast for better visibility</span>
                        </label>
                    </div>
                    
                    <div class="accessibility-option">
                        <label class="accessibility-label">
                            <input type="checkbox" id="reduced-motion-toggle" ${this.preferences.reducedMotion ? 'checked' : ''}>
                            <span class="accessibility-text">Reduce Motion</span>
                            <span class="accessibility-description">Minimizes animations and transitions</span>
                        </label>
                    </div>
                    
                    <div class="accessibility-option">
                        <label class="accessibility-label">
                            <input type="checkbox" id="large-text-toggle" ${this.preferences.largeText ? 'checked' : ''}>
                            <span class="accessibility-text">Large Text</span>
                            <span class="accessibility-description">Increases text size for better readability</span>
                        </label>
                    </div>
                    
                    <div class="accessibility-option">
                        <label class="accessibility-label">
                            <input type="checkbox" id="focus-visible-toggle" ${this.preferences.focusVisible ? 'checked' : ''}>
                            <span class="accessibility-text">Focus Indicators</span>
                            <span class="accessibility-description">Shows focus outlines for keyboard navigation</span>
                        </label>
                    </div>
                    
                    <div class="accessibility-option">
                        <label class="accessibility-label">
                            <input type="checkbox" id="announcements-toggle" ${this.preferences.announcements ? 'checked' : ''}>
                            <span class="accessibility-text">Screen Reader Announcements</span>
                            <span class="accessibility-description">Provides additional context for screen readers</span>
                        </label>
                    </div>
                    
                    <div class="accessibility-shortcuts">
                        <h4>Keyboard Shortcuts</h4>
                        <ul>
                            <li><kbd>Alt + A</kbd> - Open accessibility panel</li>
                            <li><kbd>Alt + H</kbd> - Skip to main content</li>
                            <li><kbd>Alt + M</kbd> - Open main navigation</li>
                            <li><kbd>Tab</kbd> - Navigate forward</li>
                            <li><kbd>Shift + Tab</kbd> - Navigate backward</li>
                            <li><kbd>Enter/Space</kbd> - Activate buttons and links</li>
                        </ul>
                    </div>
                </div>
            </div>
        `;

        // Add styles
        const styles = document.createElement('style');
        styles.textContent = `
            .accessibility-panel {
                position: fixed;
                top: 0;
                right: -400px;
                width: 400px;
                height: 100vh;
                background: white;
                box-shadow: -4px 0 20px rgba(0, 0, 0, 0.15);
                z-index: 1001;
                transition: right 0.3s ease;
                overflow-y: auto;
            }
            
            .accessibility-panel.show {
                right: 0;
            }
            
            .accessibility-panel-content {
                padding: 0;
            }
            
            .accessibility-panel-header {
                padding: 24px;
                border-bottom: 1px solid #e2e8f0;
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: #f8fafc;
            }
            
            .accessibility-panel-header h3 {
                margin: 0;
                font-size: 18px;
                font-weight: 600;
                color: #1e293b;
            }
            
            .accessibility-close {
                background: none;
                border: none;
                font-size: 20px;
                cursor: pointer;
                padding: 8px;
                border-radius: 4px;
                color: #64748b;
            }
            
            .accessibility-close:hover {
                background: #e2e8f0;
                color: #1e293b;
            }
            
            .accessibility-panel-body {
                padding: 24px;
            }
            
            .accessibility-option {
                margin-bottom: 24px;
            }
            
            .accessibility-label {
                display: block;
                cursor: pointer;
                padding: 16px;
                border: 2px solid #e2e8f0;
                border-radius: 8px;
                transition: all 0.2s ease;
            }
            
            .accessibility-label:hover {
                border-color: #2563eb;
                background: #f8fafc;
            }
            
            .accessibility-label input {
                margin-right: 12px;
                transform: scale(1.2);
            }
            
            .accessibility-text {
                font-weight: 500;
                color: #1e293b;
                display: block;
                margin-bottom: 4px;
            }
            
            .accessibility-description {
                font-size: 14px;
                color: #64748b;
                display: block;
            }
            
            .accessibility-shortcuts {
                margin-top: 32px;
                padding-top: 24px;
                border-top: 1px solid #e2e8f0;
            }
            
            .accessibility-shortcuts h4 {
                font-size: 16px;
                font-weight: 600;
                margin-bottom: 16px;
                color: #1e293b;
            }
            
            .accessibility-shortcuts ul {
                list-style: none;
                padding: 0;
                margin: 0;
            }
            
            .accessibility-shortcuts li {
                padding: 8px 0;
                font-size: 14px;
                color: #64748b;
            }
            
            .accessibility-shortcuts kbd {
                background: #f1f5f9;
                padding: 2px 6px;
                border-radius: 4px;
                font-family: monospace;
                font-size: 12px;
                color: #475569;
                border: 1px solid #cbd5e1;
            }
            
            @media (max-width: 480px) {
                .accessibility-panel {
                    width: 100vw;
                    right: -100vw;
                }
            }
        `;

        document.head.appendChild(styles);
        document.body.appendChild(accessibilityBtn);
        document.body.appendChild(panel);

        // Event listeners
        accessibilityBtn.addEventListener('click', () => this.togglePanel());
        panel.querySelector('.accessibility-close').addEventListener('click', () => this.togglePanel());
        
        // Option toggles
        document.getElementById('high-contrast-toggle').addEventListener('change', (e) => {
            this.toggleHighContrast(e.target.checked);
        });
        
        document.getElementById('reduced-motion-toggle').addEventListener('change', (e) => {
            this.toggleReducedMotion(e.target.checked);
        });
        
        document.getElementById('large-text-toggle').addEventListener('change', (e) => {
            this.toggleLargeText(e.target.checked);
        });
        
        document.getElementById('focus-visible-toggle').addEventListener('change', (e) => {
            this.toggleFocusVisible(e.target.checked);
        });
        
        document.getElementById('announcements-toggle').addEventListener('change', (e) => {
            this.toggleAnnouncements(e.target.checked);
        });
    }

    togglePanel() {
        const panel = document.getElementById('accessibility-panel');
        const isOpen = panel.classList.contains('show');
        
        panel.classList.toggle('show');
        panel.setAttribute('aria-hidden', isOpen ? 'true' : 'false');
        
        if (!isOpen) {
            // Focus first checkbox when opening
            setTimeout(() => {
                panel.querySelector('input[type="checkbox"]').focus();
            }, 300);
        }
    }

    enhanceKeyboardNavigation() {
        // Skip to main content link
        const skipLink = document.createElement('a');
        skipLink.href = '#main-content';
        skipLink.className = 'skip-link';
        skipLink.textContent = 'Skip to main content';
        skipLink.style.cssText = `
            position: absolute;
            top: -40px;
            left: 6px;
            background: #2563eb;
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            border-radius: 0 0 4px 4px;
            z-index: 1000;
            transition: top 0.3s;
        `;
        
        skipLink.addEventListener('focus', () => {
            skipLink.style.top = '0';
        });
        
        skipLink.addEventListener('blur', () => {
            skipLink.style.top = '-40px';
        });
        
        document.body.insertBefore(skipLink, document.body.firstChild);

        // Add main content ID if not exists
        const mainContent = document.querySelector('.main-content, main, #main-content');
        if (mainContent && !mainContent.id) {
            mainContent.id = 'main-content';
        }

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            // Alt + A: Open accessibility panel
            if (e.altKey && e.key === 'a') {
                e.preventDefault();
                this.togglePanel();
            }
            
            // Alt + H: Skip to main content
            if (e.altKey && e.key === 'h') {
                e.preventDefault();
                const mainContent = document.getElementById('main-content');
                if (mainContent) {
                    mainContent.focus();
                    mainContent.scrollIntoView({ behavior: 'smooth' });
                }
            }
            
            // Alt + M: Focus main navigation
            if (e.altKey && e.key === 'm') {
                e.preventDefault();
                const nav = document.querySelector('.navbar-nav, .nav, .navigation');
                if (nav) {
                    const firstLink = nav.querySelector('a, button');
                    if (firstLink) firstLink.focus();
                }
            }
            
            // Escape: Close panels/dropdowns
            if (e.key === 'Escape') {
                const panel = document.getElementById('accessibility-panel');
                if (panel.classList.contains('show')) {
                    this.togglePanel();
                }
            }
        });

        // Improve focus management for dropdowns
        document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
            toggle.addEventListener('keydown', (e) => {
                if (e.key === 'ArrowDown') {
                    e.preventDefault();
                    const menu = toggle.nextElementSibling;
                    if (menu) {
                        menu.classList.add('show');
                        const firstItem = menu.querySelector('.dropdown-item');
                        if (firstItem) firstItem.focus();
                    }
                }
            });
        });
    }

    improveScreenReaderSupport() {
        // Add ARIA labels to common elements
        document.querySelectorAll('button:not([aria-label]):not([aria-labelledby])').forEach(btn => {
            if (!btn.textContent.trim() && btn.querySelector('i')) {
                const icon = btn.querySelector('i');
                const iconClass = icon.className;
                
                // Common icon mappings
                const iconLabels = {
                    'fa-edit': 'Edit',
                    'fa-trash': 'Delete',
                    'fa-eye': 'View',
                    'fa-plus': 'Add',
                    'fa-download': 'Download',
                    'fa-print': 'Print',
                    'fa-search': 'Search',
                    'fa-filter': 'Filter',
                    'fa-times': 'Close',
                    'fa-check': 'Confirm',
                    'fa-arrow-left': 'Go back',
                    'fa-arrow-right': 'Go forward'
                };
                
                for (const [iconClass, label] of Object.entries(iconLabels)) {
                    if (icon.classList.contains(iconClass)) {
                        btn.setAttribute('aria-label', label);
                        break;
                    }
                }
            }
        });

        // Add role and aria-label to tables
        document.querySelectorAll('table').forEach(table => {
            if (!table.hasAttribute('role')) {
                table.setAttribute('role', 'table');
            }
            
            if (!table.hasAttribute('aria-label') && !table.hasAttribute('aria-labelledby')) {
                const caption = table.querySelector('caption');
                const title = table.closest('.card')?.querySelector('.card-header h1, .card-header h2, .card-header h3, .card-header h4, .card-header h5, .card-header h6');
                
                if (caption) {
                    table.setAttribute('aria-labelledby', caption.id || 'table-caption');
                } else if (title) {
                    table.setAttribute('aria-labelledby', title.id || 'table-title');
                } else {
                    table.setAttribute('aria-label', 'Data table');
                }
            }
        });

        // Add ARIA live regions for dynamic content
        const liveRegion = document.createElement('div');
        liveRegion.id = 'aria-live-region';
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.style.cssText = `
            position: absolute;
            left: -10000px;
            width: 1px;
            height: 1px;
            overflow: hidden;
        `;
        document.body.appendChild(liveRegion);

        // Announce important changes
        this.announceToScreenReader = (message, priority = 'polite') => {
            if (!this.preferences.announcements) return;
            
            const region = document.getElementById('aria-live-region');
            region.setAttribute('aria-live', priority);
            region.textContent = message;
            
            // Clear after announcement
            setTimeout(() => {
                region.textContent = '';
            }, 1000);
        };

        // Make it globally available
        window.announceToScreenReader = this.announceToScreenReader;
    }

    addFocusManagement() {
        // Enhanced focus visible styles
        const focusStyles = document.createElement('style');
        focusStyles.id = 'focus-styles';
        focusStyles.textContent = `
            .focus-visible *:focus {
                outline: 3px solid #2563eb !important;
                outline-offset: 2px !important;
                box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2) !important;
            }
            
            .focus-visible button:focus,
            .focus-visible .btn:focus {
                outline: 3px solid #2563eb !important;
                outline-offset: 2px !important;
            }
            
            .focus-visible input:focus,
            .focus-visible select:focus,
            .focus-visible textarea:focus {
                border-color: #2563eb !important;
                box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.2) !important;
            }
            
            .focus-visible a:focus {
                outline: 3px solid #2563eb !important;
                outline-offset: 2px !important;
                text-decoration: underline !important;
            }
        `;
        document.head.appendChild(focusStyles);

        // Focus trap for modals
        this.setupFocusTrap = (element) => {
            const focusableElements = element.querySelectorAll(
                'a[href], button, textarea, input[type="text"], input[type="radio"], input[type="checkbox"], select'
            );
            
            const firstFocusable = focusableElements[0];
            const lastFocusable = focusableElements[focusableElements.length - 1];
            
            element.addEventListener('keydown', (e) => {
                if (e.key === 'Tab') {
                    if (e.shiftKey) {
                        if (document.activeElement === firstFocusable) {
                            lastFocusable.focus();
                            e.preventDefault();
                        }
                    } else {
                        if (document.activeElement === lastFocusable) {
                            firstFocusable.focus();
                            e.preventDefault();
                        }
                    }
                }
            });
        };

        // Auto-setup focus trap for modals
        document.addEventListener('shown.bs.modal', (e) => {
            this.setupFocusTrap(e.target);
        });
    }

    setupColorContrastEnhancement() {
        const contrastStyles = document.createElement('style');
        contrastStyles.id = 'contrast-styles';
        document.head.appendChild(contrastStyles);
    }

    toggleHighContrast(enabled) {
        this.preferences.highContrast = enabled;
        this.savePreferences();
        
        const contrastStyles = document.getElementById('contrast-styles');
        
        if (enabled) {
            contrastStyles.textContent = `
                body.high-contrast {
                    --primary-color: #0000ff !important;
                    --secondary-color: #000000 !important;
                    --success-color: #008000 !important;
                    --warning-color: #ff8c00 !important;
                    --error-color: #ff0000 !important;
                    --text-color: #000000 !important;
                    --bg-color: #ffffff !important;
                    --border-color: #000000 !important;
                }
                
                .high-contrast .card,
                .high-contrast .table,
                .high-contrast .form-control,
                .high-contrast .btn {
                    border: 2px solid #000000 !important;
                }
                
                .high-contrast .btn-primary {
                    background: #0000ff !important;
                    color: #ffffff !important;
                    border: 2px solid #000000 !important;
                }
                
                .high-contrast .btn-secondary {
                    background: #ffffff !important;
                    color: #000000 !important;
                    border: 2px solid #000000 !important;
                }
                
                .high-contrast a {
                    color: #0000ff !important;
                    text-decoration: underline !important;
                }
                
                .high-contrast a:visited {
                    color: #800080 !important;
                }
            `;
            document.body.classList.add('high-contrast');
        } else {
            contrastStyles.textContent = '';
            document.body.classList.remove('high-contrast');
        }
        
        this.announceToScreenReader(`High contrast ${enabled ? 'enabled' : 'disabled'}`);
    }

    setupMotionReduction() {
        const motionStyles = document.createElement('style');
        motionStyles.id = 'motion-styles';
        document.head.appendChild(motionStyles);
    }

    toggleReducedMotion(enabled) {
        this.preferences.reducedMotion = enabled;
        this.savePreferences();
        
        const motionStyles = document.getElementById('motion-styles');
        
        if (enabled) {
            motionStyles.textContent = `
                .reduced-motion *,
                .reduced-motion *::before,
                .reduced-motion *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                    scroll-behavior: auto !important;
                }
            `;
            document.body.classList.add('reduced-motion');
        } else {
            motionStyles.textContent = '';
            document.body.classList.remove('reduced-motion');
        }
        
        this.announceToScreenReader(`Reduced motion ${enabled ? 'enabled' : 'disabled'}`);
    }

    setupTextSizeControls() {
        const textStyles = document.createElement('style');
        textStyles.id = 'text-size-styles';
        document.head.appendChild(textStyles);
    }

    toggleLargeText(enabled) {
        this.preferences.largeText = enabled;
        this.savePreferences();
        
        const textStyles = document.getElementById('text-size-styles');
        
        if (enabled) {
            textStyles.textContent = `
                .large-text {
                    font-size: 120% !important;
                    line-height: 1.6 !important;
                }
                
                .large-text h1 { font-size: 2.8rem !important; }
                .large-text h2 { font-size: 2.4rem !important; }
                .large-text h3 { font-size: 2.0rem !important; }
                .large-text h4 { font-size: 1.6rem !important; }
                .large-text h5 { font-size: 1.4rem !important; }
                .large-text h6 { font-size: 1.2rem !important; }
                
                .large-text .btn {
                    padding: 12px 24px !important;
                    font-size: 1.1rem !important;
                }
                
                .large-text .form-control {
                    padding: 12px 16px !important;
                    font-size: 1.1rem !important;
                }
            `;
            document.body.classList.add('large-text');
        } else {
            textStyles.textContent = '';
            document.body.classList.remove('large-text');
        }
        
        this.announceToScreenReader(`Large text ${enabled ? 'enabled' : 'disabled'}`);
    }

    toggleFocusVisible(enabled) {
        this.preferences.focusVisible = enabled;
        this.savePreferences();
        
        if (enabled) {
            document.body.classList.add('focus-visible');
        } else {
            document.body.classList.remove('focus-visible');
        }
        
        this.announceToScreenReader(`Focus indicators ${enabled ? 'enabled' : 'disabled'}`);
    }

    toggleAnnouncements(enabled) {
        this.preferences.announcements = enabled;
        this.savePreferences();
        
        this.announceToScreenReader(`Screen reader announcements ${enabled ? 'enabled' : 'disabled'}`);
    }

    applyStoredPreferences() {
        this.toggleHighContrast(this.preferences.highContrast);
        this.toggleReducedMotion(this.preferences.reducedMotion);
        this.toggleLargeText(this.preferences.largeText);
        this.toggleFocusVisible(this.preferences.focusVisible);
    }

    monitorSystemPreferences() {
        // Monitor system reduced motion preference
        if (window.matchMedia) {
            const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
            
            const handleChange = (e) => {
                if (e.matches && !this.preferences.reducedMotion) {
                    document.getElementById('reduced-motion-toggle').checked = true;
                    this.toggleReducedMotion(true);
                }
            };
            
            mediaQuery.addListener(handleChange);
            handleChange(mediaQuery);
        }

        // Monitor system high contrast preference
        if (window.matchMedia) {
            const contrastQuery = window.matchMedia('(prefers-contrast: high)');
            
            const handleContrastChange = (e) => {
                if (e.matches && !this.preferences.highContrast) {
                    document.getElementById('high-contrast-toggle').checked = true;
                    this.toggleHighContrast(true);
                }
            };
            
            contrastQuery.addListener(handleContrastChange);
            handleContrastChange(contrastQuery);
        }
    }
}

// ============================================
// AUTO-INITIALIZATION
// ============================================

let accessibilityManager;

document.addEventListener('DOMContentLoaded', function() {
    accessibilityManager = new AccessibilityManager();
    
    // Make available globally
    window.accessibilityManager = accessibilityManager;
    
    // Enhance existing elements
    setTimeout(() => {
        // Add missing alt attributes to images
        document.querySelectorAll('img:not([alt])').forEach(img => {
            img.setAttribute('alt', 'Image');
        });
        
        // Add missing labels to form controls
        document.querySelectorAll('input:not([aria-label]):not([aria-labelledby])').forEach(input => {
            if (!input.labels || input.labels.length === 0) {
                const placeholder = input.getAttribute('placeholder');
                if (placeholder) {
                    input.setAttribute('aria-label', placeholder);
                }
            }
        });
        
        // Add headings hierarchy check
        const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
        let lastLevel = 0;
        
        headings.forEach(heading => {
            const level = parseInt(heading.tagName.charAt(1));
            if (level > lastLevel + 1) {
                console.warn(`Heading hierarchy issue: ${heading.tagName} follows h${lastLevel}`);
            }
            lastLevel = level;
        });
        
    }, 100);
});

// Export for global use
window.AccessibilityManager = AccessibilityManager;