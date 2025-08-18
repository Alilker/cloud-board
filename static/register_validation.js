document.addEventListener('DOMContentLoaded', function() {

    const registerSubmit = document.querySelector('#register-submit');

    // Function for register button state management
    function updateRegisterSubmit() {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();
        const confirmation = document.getElementById('confirmation').value.trim();
        
        // Check if all fields are filled
        const allFieldsFilled = username && password && confirmation;
        
        // Check if all validations pass (show "Looks Good!")
        const usernameValid = !username || document.getElementById('username-feedback').innerHTML.includes('Looks Good!');
        const passwordValid = !password || document.getElementById('password-feedback').innerHTML.includes('Looks Good!');
        const confirmationValid = !confirmation || document.getElementById('confirmation-feedback').innerHTML.includes('Passwords match!');
        
        // Enable button only if all fields are filled AND all validations pass
        registerSubmit.disabled = !(allFieldsFilled && usernameValid && passwordValid && confirmationValid);
    }

    // Function for validating username in real time
    function validateUsername() {
        const username = document.getElementById('username').value.trim();
        const element = document.getElementById('username-feedback');
        
        if (!username) {
            element.innerHTML = "";
            element.classList.remove('text-feedback');
            return;
        }
        
        if (username.length < 5) {
            element.innerHTML = "<i class='text-danger'><strong>Username must be at least 5 characters</strong></i>";
        } 
        else if (username.length > 15) {
            element.innerHTML = "<i class='text-danger'><strong>Username must be 15 characters or less</strong></i>";
        } 
        else {
            element.innerHTML = "<i class='text-success'><strong>Looks Good!</strong></i>";
        }
        
        element.classList.add('text-feedback');
    }

    // Function for validating inputted password real time
    function validatePassword() {
        const password = document.getElementById('password').value;
        const element = document.getElementById('password-feedback');
        
        if (!password) {
            element.innerHTML = "";
            element.classList.remove('text-feedback');
            return;
        }

        // Password must contain 8 characters, at least one number, one uppercase letter, and one lowercase letter with no spaces
        const pattern = /(?=.*\d)(?=.*[a-z])(?=.*[A-Z])\S{8,}/;
        
        if (password.length < 8) {
            element.innerHTML = "<i class='text-danger'><strong>Password must be at least 8 characters</strong></i>";
        } 
        else if (password.length > 20) {
            element.innerHTML = "<i class='text-danger'><strong>Password must be 20 characters or less</strong></i>";
        } 
        else if (!pattern.test(password)) {
            element.innerHTML = "<i class='text-danger'><strong>Password must contain 8 characters, at least one number, one uppercase letter, and one lowercase letter, with no spaces</strong></i>";
        } 
        else {
            element.innerHTML = "<i class='text-success'><strong>Looks Good!</strong></i>";
        }
        
        element.classList.add('text-feedback');
        
        // Re-validate confirmation when password changes
        validatePasswordConfirmation();
    }

    // Function for password confirmation validation
    function validatePasswordConfirmation() {
        const password = document.getElementById('password').value;
        const confirmation = document.getElementById('confirmation').value;
        const element = document.getElementById('confirmation-feedback');
        
        if (!confirmation) {
            element.innerHTML = "";
            element.classList.remove('text-feedback');
            return;
        }
        
        if (password !== confirmation) {
            element.innerHTML = "<i class='text-danger'><strong>Passwords do not match</strong></i>";
        } 
        else {
            element.innerHTML = "<i class='text-success'><strong>Passwords match!</strong></i>";
        }
        
        element.classList.add('text-feedback');
    }

    // Listen for input changes and validate
    function validateInput() {
        document.addEventListener('input', function(event) {
            const inputId = event.target.id;

            if (inputId === 'username') {
                validateUsername();
                updateRegisterSubmit();
            } 
            else if (inputId === 'password') {
                validatePassword();
                updateRegisterSubmit();
            } 
            else if (inputId === 'confirmation') {
                validatePasswordConfirmation();
                updateRegisterSubmit();
            }
        });
    };

    // Function to show error modal
    function showRegisterErrorModal(errors) {
        const errorModal = new bootstrap.Modal(document.querySelector('#error-modal'));
        const errorMessage = document.querySelector('#error-modal .errors');

        const listItems = errors.map(error => `<li>${error}</li>`).join('');
        errorMessage.innerHTML = `<ul class="mb-0">${listItems}</ul>`;

        errorModal.show();
    }

    // Initialize register form submission
    function initializeRegisterForm() {
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
                        // Handle errors
                        const errors = data.error || 'Registration failed. Please try again.';
                        showRegisterErrorModal([errors]);
                    }
                })
                .catch(() => {
                    showRegisterErrorModal(['A network error occurred during registration']);
                });
            });
        };
    }

    // Set initial button state
    validateInput();
    updateRegisterSubmit();
    initializeRegisterForm();
});
