document.addEventListener('DOMContentLoaded', function() {

    // Button declarations
    const manageTeamSubmit = document.querySelector('#submit-manage-team');
    const manageMembersSubmit = document.querySelector('#submit-member-changes');
    
    // Get current team name from hidden input
    const currentTeamName = document.getElementById('current-team-name')?.value.trim();

    // Function for displaying errors
    function showError(message) {
        const errorModal = new bootstrap.Modal(document.querySelector('#error-modal'));
        const errorMessage = document.querySelector('#error-modal .errors');
        errorMessage.innerHTML = message;
        errorModal.show();
    }

    // Function to manage member privileges
    function initializeManageTeamMember() {

        // Enable the submit button when there is only one checkbox checked
        document.addEventListener('change', function() {
            const checkedCount = document.querySelectorAll('input[type="checkbox"][name="member-checkbox"]:checked').length;
            manageMembersSubmit.disabled = (checkedCount !== 1);
        });

        manageMembersSubmit.addEventListener('click', function(event) {
            event.preventDefault();

            const checkedBox = document.querySelector('input[name="member-checkbox"]:checked');
            const memberId = checkedBox.value.trim();
            const newPrivilege = checkedBox.parentElement.parentElement.querySelector('select').value.trim();

            // Submit manage member form
            fetch(`/manage_member_api/${currentTeamName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
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
    function initializeDeleteTeam() {
        const deleteModal = document.getElementById('delete-teams-modal');
        const confirmationText = document.getElementById('delete-confirmation-text');
        const deleteConfirmButton = document.getElementById('delete-button-confirmation');
        const deleteConfirmInput = document.getElementById('delete-confirmation-input');

        deleteModal.addEventListener('show.bs.modal', function () {
            confirmationText.innerHTML = `Are you sure you want to delete ${currentTeamName}?
            <br><i class="text-danger mt-4">This action cannot be undone!</i>`;
        });

        // Confirmation input checker
        deleteConfirmInput.addEventListener('input', function() {
            deleteConfirmInput.value.trim() === 'DELETE' ? deleteConfirmButton.disabled = false : deleteConfirmButton.disabled = true;
        });

        // Confirmation button click handler
        deleteConfirmButton.addEventListener('click', function() {

            // Submit delete team form
            fetch(`/delete_team_api/${currentTeamName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
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
        });
    }

    // Function for create team form submission initialization
    function initializeManageTeam() {
        let teamName, teamCode, teamDescription, teamAccessType;

        // Enable the submit button when there is any input
        teamName = document.getElementById('manage-team-name');
        teamCode = document.getElementById('manage-team-code');
        teamDescription = document.getElementById('manage-team-description');
        teamAccessType = document.getElementById('manage-team-access-type');

        [teamName, teamCode, teamDescription, teamAccessType].forEach(input => {
            input.addEventListener('input', function() {
                manageTeamSubmit.disabled = false;
            });
        });

        manageTeamSubmit.addEventListener('click', function(event) {
            event.preventDefault();

            // Submit manage team form
            fetch(`/manage_team_api/${currentTeamName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    "team_name": teamName.value.trim(), 
                    "team_code": teamCode.value.trim(),
                    "team_description": teamDescription.value.trim(),
                    "team_access_type": teamAccessType.value.trim()
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.href = data.redirect || '/teams';
                } 
                else {
                    showError(data.error || 'An error occurred, please try again later');
                }
            })
            .catch(error => {
                console.error(error);
                showError('A network error occurred, please try again later');
            });
        });
    }

    // Initialize functionality
    initializeManageTeamMember();
    initializeManageTeam();
    initializeDeleteTeam();
});

