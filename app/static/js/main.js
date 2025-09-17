/**
 * Main JavaScript file for AutonoWrite
 * Handles common UI interactions and initializations
 */

document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Auto-dismiss alerts after 5 seconds
    var alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add animation to elements with animate-fade-in class
    var animatedElements = document.querySelectorAll('.animate-fade-in');
    animatedElements.forEach(function(element, index) {
        element.style.animationDelay = (index * 0.1) + 's';
    });

    // Handle form validation
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Handle file input changes
    var fileInputs = document.querySelectorAll('.custom-file-input');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            var fileName = this.files[0] ? this.files[0].name : 'Nenhum arquivo selecionado';
            var label = this.nextElementSibling;
            label.textContent = fileName;
        });
    });

    // Handle password visibility toggle
    var passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(function(toggle) {
        toggle.addEventListener('click', function() {
            var input = this.previousElementSibling;
            var icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });

    // Handle sidebar toggle for mobile
    var sidebarToggler = document.getElementById('sidebarToggle');
    if (sidebarToggler) {
        sidebarToggler.addEventListener('click', function() {
            document.body.classList.toggle('sidebar-toggled');
            document.querySelector('.sidebar').classList.toggle('toggled');
            
            if (document.querySelector('.sidebar .collapse')) {
                document.querySelector('.sidebar .collapse').classList.remove('show');
            }
        });
    }

    // Close responsive menu when a scroll trigger link is clicked
    var scrollLinks = document.querySelectorAll('.js-scroll-trigger');
    scrollLinks.forEach(function(link) {
        link.addEventListener('click', function() {
            var navbarCollapse = document.querySelector('.navbar-collapse');
            if (navbarCollapse.classList.contains('show')) {
                var bsCollapse = new bootstrap.Collapse(navbarCollapse);
                bsCollapse.hide();
            }
        });
    });

    // Handle active state for navigation items
    var currentPath = window.location.pathname;
    var navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(function(link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
            link.setAttribute('aria-current', 'page');
            
            // If it's a dropdown item, also activate the parent
            var parent = link.closest('.dropdown-menu');
            if (parent) {
                var dropdownToggle = parent.previousElementSibling;
                if (dropdownToggle) {
                    dropdownToggle.classList.add('active');
                }
            }
        }
    });

    // Initialize any charts if Chart.js is loaded
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }
});

/**
 * Initialize any charts on the page
 */
function initializeCharts() {
    // Example chart initialization
    var ctx = document.getElementById('myChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Content Quality',
                    data: [65, 72, 78, 75, 82, 89],
                    borderColor: '#4e73df',
                    backgroundColor: 'rgba(78, 115, 223, 0.1)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                }
            }
        });
    }
}

/**
 * Format bytes to human readable format
 * @param {number} bytes
 * @param {number} decimals
 * @returns {string}
 */
function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * Debounce function to limit the rate at which a function can fire
 * @param {Function} func
 * @param {number} wait
 * @returns {Function}
 */
function debounce(func, wait) {
    let timeout;
    return function() {
        const context = this;
        const args = arguments;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), wait);
    };
}

// Make functions available globally
window.formatBytes = formatBytes;
window.debounce = debounce;
