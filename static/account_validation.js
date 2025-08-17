document.addEventListener('DOMContentLoaded', function() {

    const accountSubmit = document.querySelector('#account-submit');
    const accountValidation = { username: true, password: true, confirmation: true };

    // Button state management with validation state
    function updateAccountSubmit() {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();
        const confirmation = document.getElementById('confirmation').value.trim();
        const currentPassword = document.querySelector('input[name="current_password"]').value.trim();
        
        // Need current password and at least one change
        const hasChanges = username || password;
        const allValid = accountValidation.username && accountValidation.password && accountValidation.confirmation;
        
        accountSubmit.disabled = !(currentPassword && hasChanges && allValid);
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
            
            if (data.success) {
                element.innerHTML = "<i class='text-success'><strong>Looks Good!</strong></i>";
            } 
            else {
                element.innerHTML = `<i class='text-danger'><strong>${data.error}</strong></i>`;
            }
            
            accountValidation[key] = !!data.success;
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

    // Function for validating password confirmation
    function validatePasswordConfirmation() {
        const password = document.getElementById('password').value;
        const confirmation = document.getElementById('confirmation').value;
        const element = document.getElementById('confirmation-feedback');
        
        // If no password is being changed, confirmation is not needed
        if (!password && !confirmation) {
            element.innerHTML = "";
            element.classList.remove('text-feedback');
            accountValidation.confirmation = true;
        } 

        // If password is provided but no confirmation
        else if (password && !confirmation) {
            element.innerHTML = "<i class='text-danger'><strong>Please confirm your new password</strong></i>";
            accountValidation.confirmation = false;
            element.classList.add('text-feedback');
        }

        // If confirmation is provided but no password
        else if (!password && confirmation) {
            element.innerHTML = "<i class='text-danger'><strong>Please enter a new password first</strong></i>";
            accountValidation.confirmation = false;
            element.classList.add('text-feedback');
        }

        // If both are provided, check if they match
        else if (password !== confirmation) {
            element.innerHTML = "<i class='text-danger'><strong>Passwords do not match</strong></i>";
            accountValidation.confirmation = false;
            element.classList.add('text-feedback');
        } 
        else {
            element.innerHTML = "<i class='text-success'><strong>Passwords match!</strong></i>";
            accountValidation.confirmation = true;
            element.classList.add('text-feedback');
        }
        
        updateAccountSubmit();
    }

    // Listen for input changes and validate
    document.addEventListener('input', function(event) {
        const inputValue = event.target.value;
        const inputId = event.target.id;
        const inputName = event.target.name;

        if (inputId === 'username') {
            validateInput('/account_check_username', {'username': inputValue}, 'username-feedback',
                'username', updateAccountSubmit);
        } 
        else if (inputId === 'password') {
            validateInput('/account_check_password', {'password': inputValue}, 'password-feedback',
                'password', updateAccountSubmit);
            
            // Also validate confirmation when password changes
            validatePasswordConfirmation();
        } 
        else if (inputId === 'confirmation') {
            validatePasswordConfirmation();
        } 
        else if (inputName === 'current_password') {
            updateAccountSubmit();
        }
    });

    // Set initial button state
    updateAccountSubmit();

    // Function to show error modal
    function showAccountErrorModal(errors) {
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
                errorMessage.innerHTML = `<div class="alert alert-danger">An error occurred while updating your account.</div>`;
            }
        } else {
            // Handle single error string (backward compatibility)
            errorMessage.innerHTML = `<div class="alert alert-danger">${errors}</div>`;
        }
        
        errorModal.show();
    }

    // Initialize account form submission
    if (accountSubmit) {
        accountSubmit.addEventListener('click', function(event) {
            event.preventDefault();

            // Get the form values
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const confirmation = document.getElementById('confirmation').value;
            const currentPassword = document.querySelector('input[name="current_password"]').value;

            // Pack the form data
            const data = {
                username: username,
                password: password,
                confirmation: confirmation,
                current_password: currentPassword
            };

            // Submit form data
            fetch('/account', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    if (data.redirect) {
                        window.location.href = '/account';
                    } 
                    else {
                        window.location.reload();
                    }
                } 
                else {
                    // Handle both single error and multiple errors from server
                    const errors = data.errors || [data.error] || ['An error occurred while updating your account'];
                    showAccountErrorModal(errors);
                }
            })
            .catch(error => {
                console.error('Fetch error:', error);
                showAccountErrorModal(['A network error occurred while updating your account']);
            });
        });
    }

});
