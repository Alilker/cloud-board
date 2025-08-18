document.addEventListener('DOMContentLoaded', function() {

    // Button declarations
    const createTeamSubmit = document.querySelector('#submit-create-team');
    const joinCodeSubmit = document.querySelector('#join-code-submit');

    // Function for create team button state management
    function updateCreateSubmit() {
        const teamName = document.getElementById('team-name')?.value.trim() || '';
        
        if (createTeamSubmit) {
            createTeamSubmit.disabled = !teamName;
        }
    }

    // Function for join code button state management
    function updateJoinSubmit() {
        const teamName = document.getElementById('join-team-name')?.value.trim() || '';
        const teamCode = document.getElementById('join-team-code')?.value.trim() || '';
        
        if (joinCodeSubmit) {
            joinCodeSubmit.disabled = !(teamName && teamCode);
        }
    }

    // Function for error display using Bootstrap modal
    function showError(message) {
        const errorModal = new bootstrap.Modal(document.querySelector('#error-modal'));
        const errorMessage = document.querySelector('#error-modal .errors');
        errorMessage.innerHTML = message;
        errorModal.show();
    }

    // Function to leave a team
    function leaveTeam(teamId) {
        fetch('/leave_team', {
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
                showError(data.error || 'Error leaving team');
            }
        })
        .catch(() => {
            showError('Network error occurred');
        });
    }

    // Function to initialize leave team modal
    function initializeLeaveTeamModal() {
        const leaveModal = document.getElementById('leave-teams-modal');
        const confirmationText = document.getElementById('leave-confirmation-text');
        const leaveConfirmButton = document.getElementById('leave-button-confirmation');
        
        let currentTeamId = null;
        let currentTeamName = null;

        if (leaveModal) {
            leaveModal.addEventListener('show.bs.modal', function (event) {
                const button = event.relatedTarget;
                currentTeamId = button.getAttribute('data-team-id');
                currentTeamName = button.getAttribute('data-team-name');
                
                if (confirmationText && currentTeamName) {
                    confirmationText.textContent = `Are you sure you want to leave ${currentTeamName}?`;
                }
            });
        }

        // Confirmation button click handler
        if (leaveConfirmButton) {
            leaveConfirmButton.addEventListener('click', function() {
                if (currentTeamId) {
                    leaveTeam(currentTeamId);
                }
            });
        }
    }

    // Function for join team form submission initialization
    function initializeJoinTeam() {
        if (joinCodeSubmit) {
            joinCodeSubmit.addEventListener('click', function(event) {
                event.preventDefault();

                const teamName = document.querySelector('#join-team-name').value.trim();
                const teamCode = document.querySelector('#join-team-code').value.trim();

                fetch('/join_code', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ "team_name": teamName, "team_code": teamCode })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        window.location.reload();
                    } 
                    else {
                        showError(data.error || 'Error joining team');
                    }
                })
                .catch(() => {
                    showError('Network error occurred');
                });
            });
        }
    }

    // Function for create team form submission initialization
    function initializeCreateTeam() {
        if (createTeamSubmit) {
            createTeamSubmit.addEventListener('click', function(event) {
                event.preventDefault();
                
                const teamName = document.getElementById('team-name')?.value.trim();
                const teamCode = document.getElementById('team-code')?.value.trim();
                const teamDescription = document.getElementById('team-description')?.value.trim();
                const teamAccessType = document.getElementById('team-access-type')?.value;

                fetch('/create_team', {
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
                        showError(data.error || 'Error creating team');
                    }
                })
                .catch(() => {
                    showError('Network error occurred');
                });
            });
        }
    }

    // Input change listeners for button states
    document.addEventListener('input', function(event) {
        if (event.target.id === 'team-name' || event.target.id === 'team-code' || event.target.id === 'team-description') {
            updateCreateSubmit();
        } 
        else if (event.target.id === 'join-team-name' || event.target.id === 'join-team-code') {
            updateJoinSubmit();
        }
    });

    // Initialize functionality
    initializeLeaveTeamModal();
    initializeJoinTeam();
    initializeCreateTeam();
    updateCreateSubmit();
    updateJoinSubmit();

});
