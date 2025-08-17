document.addEventListener('DOMContentLoaded', function() {
    
    const loginSubmit = document.querySelector('#login-submit');

    // Button state management
    function updateLoginSubmit() {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();
        loginSubmit.disabled = !(username && password);
    }

    // Listen for input changes
    document.addEventListener('input', function(event) {
        if (event.target.id === 'username' || event.target.id === 'password') {
            updateLoginSubmit();
        }
    });

    // Set initial button state
    updateLoginSubmit();

    // Function to show error modal
    function showLoginErrorModal(errors) {
        const errorModal = new bootstrap.Modal(document.querySelector('#error-modal'));
        const errorMessage = document.querySelector('#error-modal .errors');
        
        // Handle both single error strings and arrays of errors
        if (Array.isArray(errors)) {
            if (errors.length > 1) {
                const listItems = errors.map(error => `<li>${error}</li>`).join('');
                errorMessage.innerHTML = `<div class="alert alert-danger"><ul class="mb-0">${listItems}</ul></div>`;
            } else if (errors.length === 1) {
                errorMessage.innerHTML = `<div class="alert alert-danger">${errors[0]}</div>`;
            } else {
                errorMessage.innerHTML = `<div class="alert alert-danger">Login failed. Please try again.</div>`;
            }
        } else {
            // Handle single error string (backward compatibility)
            errorMessage.innerHTML = `<div class="alert alert-danger">${errors}</div>`;
        }
        
        errorModal.show();
    }

    // Initialize login form submission
    if (loginSubmit) {
        loginSubmit.addEventListener('click', function(event) {
            event.preventDefault();

            // Get form data
            const form = document.getElementById('login-form');
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());

            // Submit form data
            fetch('/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.href = data.redirect || '/';
                } else {
                    // Handle both single error and multiple errors from server
                    const errors = data.errors || [data.error] || ['Login failed. Please check your credentials and try again.'];
                    showLoginErrorModal(errors);
                }
            })
            .catch(error => {
                console.error('Login error:', error);
                showLoginErrorModal(['A network error occurred. Please try again.']);
            });
        });
    }
});