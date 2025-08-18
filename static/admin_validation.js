document.addEventListener('DOMContentLoaded', function() {

    // Button declarations
    const editTeamSubmit = document.querySelector('#submit-edit-team');
    const editMembersSubmit = document.querySelector('#submit-member-changes');
    
    const teamId = document.getElementById('team-id').value;
    const currentTeamName = document.getElementById('current-team-name').value;


    // Function to listen for input changes and validate
    function listenForInputChanges() {
        document.addEventListener('input', function() {
            editTeamSubmit.disabled = false;
        });
    }

    // Function for displaying errors
    function showError(message) {
        const errorModal = new bootstrap.Modal(document.querySelector('#error-modal'));
        const errorMessage = document.querySelector('#error-modal .errors');
        errorMessage.innerHTML = message;
        errorModal.show();
    }

    // Function to delete a team
    function deleteTeam(teamId, teamName) {
        fetch(`/delete_team/${teamName}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 'team_id': teamId })
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                window.location.href = '/teams';
            } 
            else {
                showError(data.error || 'Error deleting team, please try again!');
            }
        })
        .catch(error => {
            console.error(error);
            showError('Network error occurred, please try again!');
        });
    }

    // Function to edit member privileges
    function initializeEditTeamMember() {
        editMembersSubmit.addEventListener('click', function(event) {
            event.preventDefault();
            
            const checkedBox = document.querySelector('input[name="member-checkbox"]:checked');
            const memberId = checkedBox.value;
            const newPrivilege = checkedBox.parentElement.querySelector('select').value;

            fetch(`/manage_member/${currentTeamName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    'team_id': teamId,
                    'member_id': memberId,
                    'privilege': newPrivilege
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.href = `/manage_team/${currentTeamName}`;
                } 
                else {
                    showError(data.error || 'An error occurred, please try again!');
                }
            })
            .catch(error => {
                console.error(error);
                showError('Network error occurred, please try again!');
            });
        });
    };

    // Function to initialize delete team modal
    function initializeDeleteTeamModal() {
        const deleteModal = document.getElementById('delete-teams-modal');
        const confirmationText = document.getElementById('delete-confirmation-text');
        const deleteConfirmButton = document.getElementById('delete-button-confirmation');

        if (deleteModal) {
            deleteModal.addEventListener('show.bs.modal', function (event) {
                const button = event.relatedTarget;
                if (confirmationText && currentTeamName) {
                    confirmationText.textContent = `Are you sure you want to delete ${currentTeamName}?`;
                }
            });
        }

        // Confirmation button click handler
        if (deleteConfirmButton) {
            deleteConfirmButton.addEventListener('click', function() {
                deleteTeam(teamId, currentTeamName);
            });
        }
    }

    // Function for create team form submission initialization
    function initializeEditTeam() {
        if (editTeamSubmit) {
            editTeamSubmit.addEventListener('click', function(event) {
                event.preventDefault();
                
                const teamId = document.getElementById('team-id')?.value.trim();
                const teamName = document.getElementById('team-name')?.value.trim();
                const teamCode = document.getElementById('team-code')?.value.trim();
                const teamDescription = document.getElementById('team-description')?.value.trim();
                const teamAccessType = document.getElementById('team-access-type')?.value;

                fetch(`/manage_team/${document.getElementById('current-team-name').value}`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        "team_id": teamId,
                        "team_name": teamName, 
                        "team_code": teamCode,
                        "team_description": teamDescription,
                        "team_access_type": teamAccessType
                    })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        window.location.href = data.redirect;
                    } 
                    else {
                        showError(data.error || 'Error creating team, please try again later');
                    }
                })
                .catch(error => {
                    console.error(error);
                    showError('Network error occurred, please try again later');
                });
            });
        }
    }

    // Initialize functionality
    listenForInputChanges();
    initializeEditTeamMember();
    initializeEditTeam();
    initializeDeleteTeamModal();
});

