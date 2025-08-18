document.addEventListener('DOMContentLoaded', function() {

    // Button declarations
    const accountSubmit = document.querySelector('#account-submit');

    // Function to listen for input changes and validate
    function listenForInputChanges() {
        document.addEventListener('input', function(event) {
            const inputId = event.target.id;
            const inputName = event.target.name;

            if (inputId === 'username') {
                validateUsername();
                updateAccountSubmit();
            } 
            else if (inputId === 'password') {
                validatePassword();
                updateAccountSubmit();
            } 
            else if (inputId === 'confirmation') {
                validatePasswordConfirmation();
                updateAccountSubmit();
            } 
            else if (inputName === 'current_password') {
                updateAccountSubmit();
            }
        });
    };

    // Function for account button state management
    function updateAccountSubmit() {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();
        const confirmation = document.getElementById('confirmation').value.trim();
        const currentPassword = document.querySelector('input[name="current_password"]').value.trim();
        
        // Need current password and at least one change
        const hasChanges = username || password;
        
        // Check if validations pass for fields that have values
        const usernameValid = !username || document.getElementById('username-feedback').innerHTML.includes('Looks Good!');
        const passwordValid = !password || document.getElementById('password-feedback').innerHTML.includes('Looks Good!');
        
        // For confirmation: only check if password is being changed
        let confirmationValid = true;
        if (password) {

            // If password is entered, confirmation must be provided and match
            confirmationValid = confirmation && document.getElementById('confirmation-feedback').innerHTML.includes('Passwords match!');
        }
         else if (confirmation) {

            // If confirmation is entered but no password, it's invalid
            confirmationValid = false;
        }
        
        // Enable button only if current password provided, has changes, AND all validations pass
        accountSubmit.disabled = !(currentPassword && hasChanges && usernameValid && passwordValid && confirmationValid);
    }

    // Function for validating username in real time (optional field for account changes)
    function validateUsername() {
        const username = document.getElementById('username').value.trim();
        const element = document.getElementById('username-feedback');
        
        if (!username) {
            element.innerHTML = "";
            element.classList.remove('text-feedback');
            return;
        }
        
        const usernameLength = username.length;
        if (usernameLength < 5) {
            element.innerHTML = `<i class='text-danger'><strong>Username is ${usernameLength} characters, must be at least 5 characters</strong></i>`;
        } 
        else if (usernameLength > 15) {
            element.innerHTML = `<i class='text-danger'><strong>Username is ${usernameLength} characters, limit is 15</strong></i>`;
        } 
        else {
            element.innerHTML = "<i class='text-success'><strong>Looks Good!</strong></i>";
        }
        
        element.classList.add('text-feedback');
    }

    // Function for validating password in real time (optional field for account changes)
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
        const passwordLength = password.length;
        
        if (passwordLength < 8) {
            element.innerHTML = `<i class='text-danger'><strong>Password is ${passwordLength} characters, must be at least 8 characters</strong></i>`;
        } 
        else if (passwordLength > 20) {
            element.innerHTML = `<i class='text-danger'><strong>Password is ${passwordLength} characters, limit is 20</strong></i>`;
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

    // Function for validating password confirmation in real time
    function validatePasswordConfirmation() {
        const password = document.getElementById('password').value;
        const confirmation = document.getElementById('confirmation').value;
        const element = document.getElementById('confirmation-feedback');
        
        // If no password is being changed, confirmation is not needed
        if (!password && !confirmation) {
            element.innerHTML = "";
            element.classList.remove('text-feedback');
        } 

        // If password is provided but no confirmation
        else if (password && !confirmation) {
            element.innerHTML = "<i class='text-danger'><strong>Please confirm your new password</strong></i>";
            element.classList.add('text-feedback');
        }

        // If confirmation is provided but no password
        else if (!password && confirmation) {
            element.innerHTML = "<i class='text-danger'><strong>Please enter a new password first</strong></i>";
            element.classList.add('text-feedback');
        }

        // If both are provided, check if they match
        else if (password !== confirmation) {
            element.innerHTML = "<i class='text-danger'><strong>Passwords do not match</strong></i>";
            element.classList.add('text-feedback');
        } 
        else {
            element.innerHTML = "<i class='text-success'><strong>Passwords match!</strong></i>";
            element.classList.add('text-feedback');
        }
    }

    // Function to show error modal
    function showError(message) {
        const errorModal = new bootstrap.Modal(document.querySelector('#error-modal'));
        const errorMessage = document.querySelector('#error-modal .errors');
        errorMessage.innerHTML = message;
        errorModal.show();
    }

    // Initialize account form submission
    function initializeAccountForm() {
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
                    new_password: password,
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
                        window.location.reload();
                    } 
                    else {
                        // Handle errors
                        showError(data.error || 'An error occurred, please try again!');
                    }
                })
                .catch(error => {
                    console.error(error);
                    showError('A network error occurred, please try again!');
                });
            });
        }
    };

    // Initialize functionality based on execution order
    listenForInputChanges();
    updateAccountSubmit();
    initializeAccountForm();
});
