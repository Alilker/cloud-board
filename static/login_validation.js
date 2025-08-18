document.addEventListener('DOMContentLoaded', function() {

    // Button declarations
    const loginSubmit = document.querySelector('#login-submit');

    // Function to listen for input changes and validate
    function listenForInputChanges() {
        document.addEventListener('input', function(event) {
            if (event.target.id === 'username' || event.target.id === 'password') {
                updateLoginSubmit();
            }
        });
    }

    // Function for login button state management
    function updateLoginSubmit() {
        const username = document.getElementById('username').value.trim();
        const password = document.getElementById('password').value.trim();
        loginSubmit.disabled = !(username && password);
    }


    // Function to show error modal
    function showLoginErrorModal(errors) {
        const errorModal = new bootstrap.Modal(document.querySelector('#error-modal'));
        const errorMessage = document.querySelector('#error-modal .errors');

        const listItems = errors.map(error => `<li>${error}</li>`).join('');
        errorMessage.innerHTML = `<ul class="mb-0">${listItems}</ul>`;

        errorModal.show();
    }

    // Function for login form submission initialization
    function initializeLoginForm() {
        if (loginSubmit) {
            loginSubmit.addEventListener('click', function(event) {
                event.preventDefault();

                // Get the form values
                const username = document.getElementById('username').value;
                const password = document.getElementById('password').value;


                // Pack the form data
                const data = {
                    username: username,
                    password: password,
                };

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
                    }
                    else {
                        // Handle errors
                        const errors = data.error || 'Login failed. Please check your credentials and try again.';
                        showLoginErrorModal([errors]);
                    }
                })
                .catch(error => {
                    showLoginErrorModal(['A network error occurred. Please try again.']);
                });
            });
        }
    };

    // Initialize functionality based on execution order
    listenForInputChanges();
    updateLoginSubmit();
    initializeLoginForm();
});