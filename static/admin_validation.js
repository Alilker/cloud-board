document.addEventListener('DOMContentLoaded', function() {

    // Button declarations
    const editTeamSubmit = document.querySelector('#submit-edit-team');
    const editMembersSubmit = document.querySelector('#submit-member-changes');
    
    // Get team ID and current team name from hidden inputs
    const teamId = document.getElementById('team-id')?.value;
    const currentTeamName = document.getElementById('current-team-name')?.value;


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

        // Submit delete team form
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

            // Submit manage member form
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

        deleteModal.addEventListener('show.bs.modal', function (event) {
            const button = event.relatedTarget;
            if (confirmationText && currentTeamName) {
                confirmationText.textContent = `Are you sure you want to delete ${currentTeamName}?`;
            }
        });

        // Confirmation button click handler
        deleteConfirmButton.addEventListener('click', function() {
            deleteTeam(teamId, currentTeamName);
        });
    }

    // Function for create team form submission initialization
    function initializeEditTeam(teamId) {
        editTeamSubmit.addEventListener('click', function(event) {
            event.preventDefault();
            
            const teamName = document.getElementById('team-name')?.value.trim();
            const teamCode = document.getElementById('team-code')?.value.trim();
            const teamDescription = document.getElementById('team-description')?.value.trim();
            const teamAccessType = document.getElementById('team-access-type')?.value;

            // Submit manage team form
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
    listenForInputChanges();
    initializeEditTeamMember();
    initializeEditTeam(teamId);
    initializeDeleteTeamModal();

});

// I couldn't get this to work inside of the other DOM content loader, but since it's
// not a big deal I just left it like this
let submitMemberChanges;
document.addEventListener('DOMContentLoaded', function() {
    submitMemberChanges = document.getElementById('submit-member-changes');
    submitMemberChanges.disabled = true;
});

// Function to check if only one checkbox is checked
function checkboxCountChecker(event) {
    const checkedCount = document.querySelectorAll('input[type="checkbox"][name="member-checkbox"]:checked').length;
    submitMemberChanges.disabled = (checkedCount !== 1);
}

