document.addEventListener('DOMContentLoaded', function() {

    // Button declarations
    const createTeamSubmit = document.querySelector('#submit-create-team');
    const joinCodeSubmit = document.querySelector('#join-code-submit');

    // Variable globalization
    let teamId = null;
    let currentTeamName = null;

    // Function to listen for input changes and validate
    function listenForInputChanges() {
        document.addEventListener('input', function(event) {
            if (event.target.id === 'create-team-name' || event.target.id === 'create-team-code' || event.target.id === 'create-team-description') {
                const teamName = document.getElementById('create-team-name')?.value.trim() || '';
                const accessType = document.getElementById('create-team-access-type')?.value.trim() || '';
                createTeamSubmit.disabled = !(teamName && accessType);
            } 
            else if (event.target.id === 'join-team-name' || event.target.id === 'join-team-code') {
                const teamName = document.getElementById('join-team-name')?.value.trim() || '';
                const teamCode = document.getElementById('join-team-code')?.value.trim() || '';
                joinCodeSubmit.disabled = !(teamName && teamCode);
            }
        });
    }

    // Function for displaying errors
    function showError(message) {
        const errorModal = new bootstrap.Modal(document.querySelector('#error-modal'));
        const errorMessage = document.querySelector('#error-modal .errors');

        errorMessage.innerHTML = message;
        errorModal.show();
    }

    // Function to leave a team
    function leaveTeam(teamId, currentTeamName) {

    }

    // Function to initialize leave team modal
    function initializeLeaveTeamModal() {
        const leaveModal = document.getElementById('leave-teams-modal');
        const confirmationText = document.getElementById('leave-confirmation-text');
        const leaveConfirmButton = document.getElementById('leave-button-confirmation');

        leaveModal.addEventListener('show.bs.modal', function (event) {
            const leaveTeamButton = event.relatedTarget;
            currentTeamName = leaveTeamButton.getAttribute('data-team-name');
            teamId = leaveTeamButton.getAttribute('data-team-id');

            if (confirmationText && currentTeamName) {
                confirmationText.textContent = `Are you sure you want to leave ${currentTeamName}?`;
            }
        });


        // Confirmation button click handler
        leaveConfirmButton.addEventListener('click', function() {

            fetch(`/leave_team_api/${currentTeamName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 'team_id': teamId })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.reload();
                } 
                else {
                    showError(data.error || 'An error occured, please try again');
                }
            })
            .catch(error => {
                console.error(error);
                showError('A network error occurred, please try again!');
            });
        });
    }

    // Function for join team form submission initialization
    function initializeJoinTeam() {
        joinCodeSubmit.addEventListener('click', function(event) {
            event.preventDefault();

            const teamName = document.querySelector('#join-team-name').value.trim();
            const teamCode = document.querySelector('#join-team-code').value.trim();

            fetch('/join_code_api', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    "team_name": teamName, 
                    "team_code": teamCode 
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.reload();
                } 
                else {
                    showError(data.error || 'An error occurred, please try again');
                }
            })
            .catch(error => {
                console.error(error);
                showError('A network error occurred, please try again!');
            });
        });
    }

    // Function for create team form submission initialization
    function initializeCreateTeam() {
        createTeamSubmit.addEventListener('click', function(event) {
            event.preventDefault();
            
            const teamName = document.getElementById('create-team-name')?.value.trim();
            const teamCode = document.getElementById('create-team-code')?.value.trim();
            const teamDescription = document.getElementById('create-team-description')?.value.trim();
            const teamAccessType = document.getElementById('create-team-access-type')?.value.trim();

            fetch('/create_team_api', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    "team_name": teamName, 
                    "team_code": teamCode,
                    "team_description": teamDescription,
                    "team_access_type": teamAccessType
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.reload();
                } 
                else {
                    showError(data.error || 'An error occurred, please try again later');
                }
            })
            .catch((error) => {
                console.error(error);
                showError('A network error occurred, please try again later');
            });
        });
    }

    // Initialize functionality
    listenForInputChanges();
    initializeJoinTeam();
    initializeCreateTeam();
    initializeLeaveTeamModal();
});
