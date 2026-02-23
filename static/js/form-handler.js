// Form submission handler with loading state
document.addEventListener('DOMContentLoaded', function() {
    // Handle all forms with loading state
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            
            if (submitBtn && !submitBtn.disabled) {
                // Store original button content
                const originalContent = submitBtn.innerHTML;
                
                // Disable button and show loading
                submitBtn.disabled = true;
                submitBtn.style.opacity = '0.7';
                submitBtn.style.cursor = 'not-allowed';
                submitBtn.innerHTML = '<span style="display: inline-flex; align-items: center; gap: 0.5rem;"><svg style="animation: spin 1s linear infinite; width: 1rem; height: 1rem;" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle style="opacity: 0.25;" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path style="opacity: 0.75;" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg> Processing...</span>';
                
                // Re-enable after timeout (fallback in case of error)
                setTimeout(function() {
                    if (submitBtn.disabled) {
                        submitBtn.disabled = false;
                        submitBtn.style.opacity = '1';
                        submitBtn.style.cursor = 'pointer';
                        submitBtn.innerHTML = originalContent;
                    }
                }, 30000); // 30 seconds timeout
            }
        });
    });
});

// Add spinning animation
const style = document.createElement('style');
style.textContent = `
    @keyframes spin {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
`;
document.head.appendChild(style);
