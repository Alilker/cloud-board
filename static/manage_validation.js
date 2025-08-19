document.addEventListener('DOMContentLoaded', function() {

    // Button declarations
    const manageTeamSubmit = document.querySelector('#submit-manage-team');
    const manageMembersSubmit = document.querySelector('#submit-member-changes');
    
    // Get team ID and current team name from hidden inputs
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

        document.addEventListener('input', function() {
            let teamName = document.getElementById('manage-team-name')?.value.trim();
            let teamCode = document.getElementById('manage-team-code')?.value.trim();
            let teamDescription = document.getElementById('manage-team-description')?.value.trim();
            let teamAccessType = document.getElementById('manage-team-access-type')?.value.trim();
            manageTeamSubmit.disabled = (teamName === '' && teamCode === '' && teamDescription === '' && teamAccessType === '');
        });

        manageTeamSubmit.addEventListener('click', function(event) {
            event.preventDefault();

            // Submit manage team form
            fetch(`/manage_team_api/${currentTeamName}`, {
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

// I couldn't get this to work inside of the other DOM content loader, but since it's
// not a big deal I just left it like this
let manageMembersCheck;
document.addEventListener('DOMContentLoaded', function() {
    manageMembersCheck = document.getElementById('submit-member-changes');
    manageMembersCheck.disabled = true;
});

// Function to check if only one checkbox is checked
function checkboxCountChecker() {
    const checkedCount = document.querySelectorAll('input[type="checkbox"][name="member-checkbox"]:checked').length;
    manageMembersCheck.disabled = (checkedCount !== 1);
}

