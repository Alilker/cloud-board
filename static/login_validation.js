document.addEventListener('DOMContentLoaded', function() {

    // Button declarations
    const loginSubmit = document.querySelector('#login-submit');

    // Function for displaying errors
    function showError(message) {
        const errorModal = new bootstrap.Modal(document.querySelector('#error-modal'));
        const errorMessage = document.querySelector('#error-modal .errors');

        errorMessage.innerHTML = message;
        errorModal.show();
    }

    // Function for login form submission initialization
    function initializeLoginForm() {

        document.addEventListener('input', function(event) {
            if (event.target.id === 'username' || event.target.id === 'password') {
                const username = document.getElementById('username').value.trim();
                const password = document.getElementById('password').value.trim();
                
                loginSubmit.disabled = !(username && password);
            }
        });

        loginSubmit.addEventListener('click', function(event) {
            event.preventDefault();

            // Get the form values
            const username = document.getElementById('username').value.trim();
            const password = document.getElementById('password').value.trim();


            // Pack the form data
            const data = {
                username: username,
                password: password,
            };

            // Submit form data
            fetch('/login_api', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.href = '/';
                }
                else {
                    showError(data.error || 'An error occurred, please try again later');
                }
            })
            .catch(error => {
                console.error(error);
                showError('A network error occurred, please try again.');
            });
        });
    };

    // Initialize functionality based on execution order
    initializeLoginForm();
});