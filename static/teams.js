document.addEventListener('DOMContentLoaded', function() {

    // Initialize variables, selectionMode represents the state of the leave team toggle,
    // selectedTeamIds keeps track of the teams the user has selected to leave
    let selectionMode = false;
    let selectedTeamIds = new Set();

    // Necessary fields for the create team modal and join team modal
    const createValidation = { name: false, code: true, description: true };
    const joinValidation = { name: false, code: false };

    // Button declarations
    const leaveButtonToggle = document.querySelector('#toggle-leave');
    const leaveButton = document.querySelector('#leave-button');
    const leaveButtonConfirmation = document.querySelector('#leave-button-confirmation');
    const createTeamSubmit = document.querySelector('#submit-create-team');
    const joinCodeSubmit = document.querySelector('#join-code-submit');

    // Restore leave selections after the pages change
    function restoreSelections() {
        const cards = document.querySelectorAll('.card-body');
        
        for (let card of cards) {
            if (card.closest('.card').style.display === 'none') continue;

            const teamId = card.querySelector('input[name="team[]"]').value;
            if (selectedTeamIds.has(teamId)) {
                card.classList.add('toggled-leave-team');
            }
        }
    }

    // Call restoreSelections on pagination page change
    function paginationPageChangeDetection() {
        document.addEventListener('paginationPageChange', function() {
            if (selectionMode) {
                setTimeout(restoreSelections, 10);
            }
        });
    };

    // Initialize the leave button toggle and alter the leave button's and the toggle button's appearance
    function initializeLeaveButtonToggle() {
        leaveButtonToggle.addEventListener('click', function() {

            // Toggle the selection mode and change the button's text accordingly
            selectionMode = !selectionMode;
            leaveButtonToggle.textContent = selectionMode ? "Cancel Selection" : "Select Teams To Leave!";

            // Make the leave button visible and enable it
            leaveButton.classList.toggle('visible', selectionMode);
            leaveButton.disabled = true;

            // Update the toggle button's color
            leaveButtonToggle.classList.toggle('btn-danger', !selectionMode);
            leaveButtonToggle.classList.toggle('btn-secondary', selectionMode);

            // If selection mode gets toggled off, remove every card's toggled-leave-team class
            if (!selectionMode) {

                // Make sure to clear the set to avoid memory leaks
                selectedTeamIds.clear();
                const cards = document.querySelectorAll('.card-body');
                for (let card of cards) {
                    card.classList.remove('toggled-leave-team');
                }
            }
        });
    };

    // Initialize card selection for when the leave button is toggled on
    function initializeCardSelection() {
        if (document.querySelectorAll('.card').length !== 0) {

            // If there are selected cards, enable and show the leave button
            leaveButtonToggle.disabled = false;
            leaveButtonToggle.hidden = false;
        }

        const cards = document.querySelectorAll('.card-body');

        // Make every team's card be clickable for selection
        for (let card of cards) {
            card.addEventListener('click', function() {

                // If selection mode is not active, do nothing
                if (!selectionMode)
                    return;
                
                // Get the team's ID
                const teamId = card.querySelector('input[name="team[]"]').value;
                
                // Toggle the team's selection state
                if (selectedTeamIds.has(teamId)) {
                    selectedTeamIds.delete(teamId);
                    card.classList.remove('toggled-leave-team');
                } 
                else {
                    selectedTeamIds.add(teamId);
                    card.classList.add('toggled-leave-team');
                }

                // Update the leave button's disabled state based on the amount of selected cards
                const selectedCards = document.querySelectorAll('.toggled-leave-team').length;
                leaveButton.disabled = selectedCards === 0;
            });
        }
    };

    // Initialize the leave button confirmation
    function initializeLeaveButtonConfirmation() {
        leaveButtonConfirmation.addEventListener('click', function() {
            const cardsForLeaving = Array.from(document.querySelectorAll('.toggled-leave-team'));
            let completedRequests = 0;
            let errors = [];
            let errorTeamNames = [];

            // Sub function for completion and error detection
            function leaveCompletionHandler() {
                if (completedRequests === cardsForLeaving.length) {
                    if (errors.length > 0) {
                        localStorage.setItem('leaveErrors', JSON.stringify(errors));
                        localStorage.setItem('errorTeamNames', JSON.stringify(errorTeamNames));
                    }
                    selectedTeamIds.clear();
                    window.location.reload();
                }
            }

            for (let card of cardsForLeaving) {
                const teamId = card.querySelector('input[name="team[]"]').value;

                // For every selected team, call the leave_team API
                fetch('/leave_team', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ 'team_id': teamId })
                })
                .then(res => res.json())
                .then(data => {

                    // Increment completedRequests to keep track if an error has occured
                    completedRequests++;

                    // For every failed request, push the error message and team name
                    if (!data.success) {
                        errors.push(data.error || "An error occurred while leaving the teams.")
                        errorTeamNames.push(data.name || "Unknown Team");
                    }

                    // Check for completion
                    leaveCompletionHandler();
                })
                .catch(() => {
                    // Increment completedRequests to keep track if an error has occured
                    completedRequests++;

                    // For every failed request, push the error message and team name
                    errors.push("Network error while leaving teams.");
                    errorTeamNames.push("Network Error - Team Unknown");

                    // Check for completion
                    leaveCompletionHandler();
                });
            }
        });
    };

    // Show the error modal if leaving teams caused any errors.
    function showLeaveErrorsModal() {
        // Retrieve error messages from localStorage
        const leaveErrors = JSON.parse(localStorage.getItem('leaveErrors') || '[]');
        const leaveErrorTeamNames = JSON.parse(localStorage.getItem('errorTeamNames') || '[]');

        // Check leaveErrors's length to see if there are any errors
        if (leaveErrors.length) {
            const errorModal = new bootstrap.Modal(document.querySelector('#error-modal'));
            const errorMessages = leaveErrors.map((err, i) => `${err} (From team: ${leaveErrorTeamNames[i]})`);
            
            // Add every error to the modal's inner HTML
            if (leaveErrors.length > 1) {
                const listItems = errorMessages.map(msg => `<li>${msg}</li>`).join('');
                document.querySelector('#error-modal .errors').innerHTML = `<div class="alert alert-danger"><ul class="mb-0">${listItems}</ul></div>`;
            } 
            else {
                document.querySelector('#error-modal .errors').innerHTML = `<div class="alert alert-danger">${errorMessages[0]}</div>`;
            }
            
            // Display the error modal and remove the error information from localStorage
            errorModal.show();
            localStorage.removeItem('errorTeamNames');
            localStorage.removeItem('leaveErrors');
        }
    };

    function showJoinCodeErrorModal(message) {
        
        //Grab the error modal
        const errorModal = new bootstrap.Modal(document.querySelector('#error-modal'));

        // Grab where the error message needs to go
        const errorMessage = document.querySelector('#error-modal .errors');

        // Insert the message and show the modal
        errorMessage.innerHTML = `<div class="alert alert-danger">${message}</div>`;
        errorModal.show();
    }

    function initializeJoinCodeSubmission() {
        joinCodeSubmit.addEventListener('click', function(event) {
            event.preventDefault();

            // Get the team name and code from the input fields
            const teamName = document.querySelector('#join-team-name').value;
            const teamCode = document.querySelector('#join-team-code').value;

            // Call the API to join the team
            fetch('/join_code', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({"team_name": teamName, "team_code": teamCode})
            })
            .then(res => res.json())
            .then(data => {

                // If the join was successful, reload the page
                if (data.success) {
                    window.location.reload();
                } 

                // Else, show the error modal with the error information
                else {
                    showJoinCodeErrorModal(data.error || 'An error occurred while joining the team');
                }
            })

            // Show the error modal for fetch/network errors
            .catch(error => {
                console.error('Fetch error:', error)
                showJoinCodeErrorModal('A network error occurred while joining the team');
            });
        });
    };

    // The button state refreshing functions
    function updateCreateSubmit() {
        const teamName = document.getElementById('team-name')?.value.trim();
        if (createTeamSubmit) {
            createTeamSubmit.disabled = !teamName;
        }
    }

    function updateJoinSubmit() {
        const teamName = document.getElementById('join-team-name')?.value.trim();
        const teamCode = document.getElementById('join-team-code')?.value.trim();
        if (joinCodeSubmit) {
            joinCodeSubmit.disabled = !(teamName && teamCode);
        }
    }


    // Dynamic validation API caller for joining teams and creating teams
    function validateInput(url, payload, feedbackElementId, key, validationObject, updateFunction) {
        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            const element = document.getElementById(feedbackElementId);

            // Alter the element's inner HTML depending on the validation result
            if (data.success) {
                element.innerHTML = "<i class='text-success'><strong>Looks Good!</strong></i>";
            } 
            else {
                element.innerHTML = `<i class='text-danger'><strong>${data.error}</strong></i>`;
            }

            // Check if the validation object criteria is met
            validationObject[key] = !!data.success;

            // Refresh the button via the specified updateFunction
            updateFunction();

            // Add the text-feedback class for text formatting
            element.classList.add('text-feedback');
        })

        // If API call fails log it in the console and inform the user
        .catch(error => {
            console.error('Fetch error:', error);
            element.innerHTML = "<i class='text-danger'><strong>Network error occurred. Please try again later.</strong></i>";
        });
    }

    // Form validation for creating and joining teams via validateInput
    function teamCreateAndJoinValidation () {
        document.addEventListener('input', function(event) {
            
            // Get the input values
            const inputName = event.target.value;
            const inputId = event.target.id;

            // For every possible field, validate the input
            if (inputId === 'team-name') {
                validateInput('/create_check_name', {'name': inputName }, 'team-name-feedback',
                    'name', createValidation, updateCreateSubmit);
            }
            
            else if (inputId === 'team-code') {
                validateInput('/create_check_code', {'code': inputName }, 'team-code-feedback',
                    'code', createValidation, updateCreateSubmit);
            }

            else if (inputId === 'team-description') {
                validateInput('/create_check_description', {'description': inputName }, 'team-description-feedback',
                    'description', createValidation, updateCreateSubmit);
            }

            else if (inputId === 'join-team-name') {
                validateInput('/join_check_name', {'name': inputName }, 'join-team-name-feedback',
                    'name', joinValidation, updateJoinSubmit);
            }

            else if (inputId === 'join-team-code') {
                validateInput('/join_check_code', {'code': inputName }, 'join-team-code-feedback',
                    'code', joinValidation, updateJoinSubmit);
            }
        });
    }


    // Call all of the functions depending on their execution order
    paginationPageChangeDetection();

    initializeLeaveButtonToggle();
    
    initializeCardSelection();
    
    initializeLeaveButtonConfirmation();
    
    showLeaveErrorsModal();
    
    initializeJoinCodeSubmission();
    
    teamCreateAndJoinValidation();
});
