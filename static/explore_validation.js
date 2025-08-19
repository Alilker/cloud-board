document.addEventListener('DOMContentLoaded', function() {

    // Function for displaying errors
    function showError(message) {
        const errorModal = new bootstrap.Modal(document.querySelector('#error-modal'));
        const errorMessage = document.querySelector('#error-modal .errors');
        
        errorMessage.innerHTML = message;
        errorModal.show();
    }

    // Function to initialize join buttons
    function initializeJoinButtons() {
        const joinButtons = document.querySelectorAll('.join-button');

        // Add click listener for every team join button
        joinButtons.forEach(button => {
            button.addEventListener('click', function(event) {
                event.preventDefault();

                const teamId = button.getAttribute('data-team-id');

                // Send request to join team
                fetch('/join_team_api', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ team_id: teamId })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    } 
                    else {
                        showError(data.error || 'An error occured, please try again!');
                    }
                })
                .catch(error => {
                    console.error(error);
                    showError('A network error occurred, please try again!');
                });
            });
        });
    }

    // Initialize functionality
    initializeJoinButtons();
});