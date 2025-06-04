// ASICS Store JavaScript

// Global variables
let cart = JSON.parse(localStorage.getItem('cart')) || [];

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    updateCartBadge();
    initializeTooltips();
    initializeSearchFeatures();
});

// Initialize application
function initializeApp() {
    console.log('ASICS Store initialized');
    
    // Add loading states to buttons
    addLoadingStates();
    
    // Initialize cart functionality
    initializeCart();
    
    // Add smooth scrolling
    addSmoothScrolling();
    
    // Initialize form validation
    initializeFormValidation();
}

// Cart functionality
function initializeCart() {
    // Update cart badge on page load
    updateCartBadge();
    
    // Add event listeners for cart buttons
    document.querySelectorAll('[data-add-to-cart]').forEach(button => {
        button.addEventListener('click', function() {
            const productId = this.getAttribute('data-product-id');
            const quantity = this.getAttribute('data-quantity') || 1;
            addToCart(productId, parseInt(quantity));
        });
    });
}

// Add to cart function
function addToCart(productId, quantity = 1) {
    // Show loading state
    const button = document.querySelector(`[data-product-id="${productId}"]`);
    if (button) {
        const originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Adding...';
        button.disabled = true;
        
        // Simulate API call
        setTimeout(() => {
            // Add to local cart
            const existingItem = cart.find(item => item.productId === productId);
            if (existingItem) {
                existingItem.quantity += quantity;
            } else {
                cart.push({ productId, quantity });
            }
            
            // Save to localStorage
            localStorage.setItem('cart', JSON.stringify(cart));
            
            // Update UI
            updateCartBadge();
            showNotification('Product added to cart!', 'success');
            
            // Restore button
            button.innerHTML = originalText;
            button.disabled = false;
        }, 500);
    }
}

// Remove from cart
function removeFromCart(productId) {
    cart = cart.filter(item => item.productId !== productId);
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartBadge();
    showNotification('Product removed from cart', 'info');
}

// Update cart badge
function updateCartBadge() {
    const badge = document.querySelector('.navbar .badge');
    if (badge) {
        const totalItems = cart.reduce((sum, item) => sum + item.quantity, 0);
        badge.textContent = totalItems;
        
        // Add animation
        if (totalItems > 0) {
            badge.classList.add('animate__animated', 'animate__pulse');
            setTimeout(() => {
                badge.classList.remove('animate__animated', 'animate__pulse');
            }, 1000);
        }
    }
}

// Show notification
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 3 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 3000);
}

// Add loading states to buttons
function addLoadingStates() {
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                const originalText = submitButton.innerHTML;
                submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
                submitButton.disabled = true;
                
                // Restore after 3 seconds (fallback)
                setTimeout(() => {
                    submitButton.innerHTML = originalText;
                    submitButton.disabled = false;
                }, 3000);
            }
        });
    });
}

// Initialize tooltips
function initializeTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Add smooth scrolling
function addSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// Initialize search features
function initializeSearchFeatures() {
    const searchInput = document.querySelector('input[name="search"]');
    if (searchInput) {
        // Add search suggestions (simplified)
        searchInput.addEventListener('input', debounce(function() {
            const query = this.value.trim();
            if (query.length > 2) {
                // In a real app, you'd fetch suggestions from API
                console.log('Searching for:', query);
            }
        }, 300));
    }
}

// Initialize form validation
function initializeFormValidation() {
    // Add custom validation styles
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Real-time validation for specific fields
    document.querySelectorAll('input[type="email"]').forEach(input => {
        input.addEventListener('blur', function() {
            validateEmail(this);
        });
    });
    
    document.querySelectorAll('input[type="password"]').forEach(input => {
        input.addEventListener('input', function() {
            validatePassword(this);
        });
    });
}

// Email validation
function validateEmail(input) {
    const email = input.value;
    const isValid = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    
    if (email && !isValid) {
        input.setCustomValidity('Please enter a valid email address');
        input.classList.add('is-invalid');
    } else {
        input.setCustomValidity('');
        input.classList.remove('is-invalid');
        if (email) input.classList.add('is-valid');
    }
}

// Password validation
function validatePassword(input) {
    const password = input.value;
    const minLength = 8;
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    
    let message = '';
    if (password.length < minLength) {
        message = `Password must be at least ${minLength} characters long`;
    } else if (!hasUpperCase || !hasLowerCase || !hasNumbers) {
        message = 'Password must contain uppercase, lowercase, and numbers';
    }
    
    if (message) {
        input.setCustomValidity(message);
        input.classList.add('is-invalid');
    } else {
        input.setCustomValidity('');
        input.classList.remove('is-invalid');
        if (password) input.classList.add('is-valid');
    }
}

// Utility functions
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Format currency
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(amount);
}

// Format date
function formatDate(date) {
    return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    }).format(new Date(date));
}

// Image lazy loading
function initializeLazyLoading() {
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    // In production, you might want to send this to an error tracking service
});

// Service worker registration (for PWA features)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('SW registered: ', registration);
            })
            .catch(function(registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// Export functions for use in other scripts
window.AsicsStore = {
    addToCart,
    removeFromCart,
    updateCartBadge,
    showNotification,
    formatCurrency,
    formatDate
};