// ==================== Campus Management System - Main JavaScript ====================

// Auto-dismiss messages after 5 seconds
document.addEventListener('DOMContentLoaded', function() {
    const messages = document.querySelectorAll('.alert');
    if (messages) {
        messages.forEach(function(message) {
            setTimeout(function() {
                message.style.animation = 'slideOutRight 0.5s ease-out';
                setTimeout(function() {
                    message.remove();
                }, 500);
            }, 5000);
        });
    }

    // Add active class to current nav link
    const currentLocation = window.location.pathname;
    const navLinks = document.querySelectorAll('header nav ul li a');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.style.background = 'rgba(255, 255, 255, 0.3)';
            link.style.borderColor = 'rgba(255, 255, 255, 0.4)';
        }
    });

    // Smooth scroll for anchor links
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

    // Add hover effect animations
    const cards = document.querySelectorAll('.dashboard-card, .stat-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-8px) scale(1.02)';
        });
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });

    // Form validation enhancement (exclude login and register forms)
    const forms = document.querySelectorAll('form:not(#loginForm):not(#registerForm)');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = this.querySelectorAll('input[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = '#ef4444';
                    input.style.animation = 'shake 0.5s';
                } else {
                    input.style.borderColor = '#10b981';
                }
            });

            if (!isValid) {
                e.preventDefault();
                showNotification('Please fill in all required fields', 'error');
            }
        });
    });

    // Input focus animations
    const inputs = document.querySelectorAll('input, textarea, select');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.01)';
        });
        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    });
});

// Show notification function
function showNotification(message, type = 'info') {
    const messagesContainer = document.querySelector('.messages') || createMessagesContainer();
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.innerHTML = `<strong>${type === 'success' ? '✓' : type === 'error' ? '✗' : 'ℹ'}</strong> ${message}`;
    messagesContainer.appendChild(alert);

    setTimeout(() => {
        alert.style.animation = 'slideOutRight 0.5s ease-out';
        setTimeout(() => alert.remove(), 500);
    }, 5000);
}

function createMessagesContainer() {
    const container = document.createElement('div');
    container.className = 'messages';
    document.body.appendChild(container);
    return container;
}

// Add CSS animations dynamically
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }
`;
document.head.appendChild(style);

// Table search functionality
function searchTable(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);
    
    if (!input || !table) return;
    
    input.addEventListener('keyup', function() {
        const filter = this.value.toLowerCase();
        const rows = table.getElementsByTagName('tr');
        
        for (let i = 1; i < rows.length; i++) {
            const row = rows[i];
            const cells = row.getElementsByTagName('td');
            let found = false;
            
            for (let j = 0; j < cells.length; j++) {
                const cell = cells[j];
                if (cell.textContent.toLowerCase().indexOf(filter) > -1) {
                    found = true;
                    break;
                }
            }
            
            row.style.display = found ? '' : 'none';
        }
    });
}

// Confirm delete action
function confirmDelete(message = 'Are you sure you want to delete this item?') {
    return confirm(message);
}

// Print table functionality
function printTable(tableId) {
    const table = document.getElementById(tableId);
    if (!table) return;
    
    const printWindow = window.open('', '', 'height=600,width=800');
    printWindow.document.write('<html><head><title>Print</title>');
    printWindow.document.write('<style>table { width: 100%; border-collapse: collapse; } th, td { border: 1px solid #ddd; padding: 8px; text-align: left; } th { background-color: #6366f1; color: white; }</style>');
    printWindow.document.write('</head><body>');
    printWindow.document.write(table.outerHTML);
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.print();
}

console.log('🎓 Campus Management System - JavaScript Loaded Successfully!');
