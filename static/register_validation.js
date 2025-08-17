document.addEventListener('DOMContentLoaded', function() {

    const registerSubmit = document.querySelector('#register-submit');
    const registerValidation = { username: false, password: false, confirmation: false };

    // Button state management with validation state
    function updateRegisterSubmit() {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();
        const confirmation = document.getElementById('confirmation').value.trim();
        
        // All fields must be filled and valid
        const hasAllFields = username && password && confirmation;
        const allValid = registerValidation.username && registerValidation.password && registerValidation.confirmation;
        
        registerSubmit.disabled = !(hasAllFields && allValid);
    }

    // Function for validating inputted fields
    function validateInput(url, payload, feedbackElementId, key, updateFunction) {
        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            const element = document.getElementById(feedbackElementId);
            
            // Output based on success
            if (data.success) {
                element.innerHTML = "<i class='text-success'><strong>Looks Good!</strong></i>";
            } 
            else {
                element.innerHTML = `<i class='text-danger'><strong>${data.error}</strong></i>`;
            }

            // Update button status via validation state
            registerValidation[key] = !!data.success;
            updateFunction();
            element.classList.add('text-feedback');
        })
        .catch(error => {
            console.error('Validation error:', error);
            const element = document.getElementById(feedbackElementId);
            element.innerHTML = "<i class='text-danger'><strong>Network error occurred. Please try again later.</strong></i>";
            element.classList.add('text-feedback');
        });
    }

    // Password confirmation validation
    function validatePasswordConfirmation() {
        const password = document.getElementById('password').value;
        const confirmation = document.getElementById('confirmation').value;
        const element = document.getElementById('confirmation-feedback');
        
        if (!confirmation) {
            element.innerHTML = "<i class='text-danger'><strong>Password confirmation is required</strong></i>";
            registerValidation.confirmation = false;
        } 
        else if (password !== confirmation) {
            element.innerHTML = "<i class='text-danger'><strong>Passwords do not match</strong></i>";
            registerValidation.confirmation = false;
        } 
        else {
            element.innerHTML = "<i class='text-success'><strong>Passwords match!</strong></i>";
            registerValidation.confirmation = true;
        }
        
        element.classList.add('text-feedback');
        updateRegisterSubmit();
    }

    // Listen for input changes and validate
    document.addEventListener('input', function(event) {
        const inputValue = event.target.value;
        const inputId = event.target.id;

        if (inputId === 'username') {
            validateInput('/register_check_username', {'username': inputValue}, 'username-feedback',
                'username', updateRegisterSubmit);
        } 
        else if (inputId === 'password') {
            validateInput('/register_check_password', {'password': inputValue}, 'password-feedback',
                'password', updateRegisterSubmit);
        } 
        else if (inputId === 'confirmation') {
            validatePasswordConfirmation();
        }
    });

    // Set initial button state
    updateRegisterSubmit();

    // Function to show error modal
    function showRegisterErrorModal(errors) {
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
                errorMessage.innerHTML = `<div class="alert alert-danger">Registration failed. Please try again.</div>`;
            }
        } else {
            // Handle single error string (backward compatibility)
            errorMessage.innerHTML = `<div class="alert alert-danger">${errors}</div>`;
        }
        
        errorModal.show();
    }

    // Initialize register form submission
    if (registerSubmit) {
        registerSubmit.addEventListener('click', function(event) {
            event.preventDefault();

            // Get the form values
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const confirmation = document.getElementById('confirmation').value;

            // Pack form values
            const data = {
                username: username,
                password: password,
                confirmation: confirmation
            };

            // Submit form data
            fetch('/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.href = data.redirect || '/';
                } 
                else {
                    // Handle both single error and multiple errors from server
                    const errors = data.errors || [data.error] || ['Registration failed. Please try again.'];
                    showRegisterErrorModal(errors);
                }
            })
            .catch(error => {
                console.error('Register error:', error);
                showRegisterErrorModal(['A network error occurred during registration']);
            });
        });
    }

});
