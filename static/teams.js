document.addEventListener('DOMContentLoaded', function() {
    let selectionMode = false;
    let selectedTeamIds = new Set();

    const leaveButtonToggle = document.querySelector('#toggle-leave');
    const leaveButton = document.querySelector('#leave-button');
    const leaveButtonConfirmation = document.querySelector('#leave-button-confirmation');

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

    const errors = JSON.parse(localStorage.getItem('leaveErrors') || '[]');
    const errorTeamNames = JSON.parse(localStorage.getItem('errorTeamNames') || '[]');
    if (errors.length) {
        const errorModal = new bootstrap.Modal(document.querySelector('#leave-team-error'));
        const errorMessages = errors.map((err, i) => `${err} (From team: ${errorTeamNames[i]})`);
        document.querySelector('#leave-team-error .leave-errors').innerHTML = errorMessages.join('<br>');
        errorModal.show();
        localStorage.removeItem('errorTeamNames');
        localStorage.removeItem('leaveErrors');
    }

    document.addEventListener('paginationPageChange', function(e) {
    if (selectionMode) {
        setTimeout(restoreSelections, 10);
    }
    });

    if (document.querySelectorAll('.card').length !== 0) {
        leaveButtonToggle.disabled = false;
        leaveButtonToggle.hidden = false;
    }

    const cards = document.querySelectorAll('.card-body');

    for (let card of cards) {
        card.addEventListener('click', function() {
            if (!selectionMode)
                return;
                
            const teamId = card.querySelector('input[name="team[]"]').value;
            
            if (selectedTeamIds.has(teamId)) {
                selectedTeamIds.delete(teamId);
                card.classList.remove('toggled-leave-team');
            } else {
                selectedTeamIds.add(teamId);
                card.classList.add('toggled-leave-team');
            }

            const selectedCards = document.querySelectorAll('.toggled-leave-team').length;
            leaveButton.disabled = selectedCards === 0;
        });
    }

    leaveButtonToggle.addEventListener('click', function() {
        selectionMode = !selectionMode;
        leaveButtonToggle.textContent = selectionMode ? "Cancel Selection" : "Select teams to leave!";
        leaveButton.classList.toggle('visible', selectionMode);
        leaveButton.disabled = true;
        leaveButtonToggle.classList.toggle('btn-danger', !selectionMode);
        leaveButtonToggle.classList.toggle('btn-secondary', selectionMode);

        if (!selectionMode) {
            selectedTeamIds.clear();
            for (let card of cards) {
                card.classList.remove('toggled-leave-team');
            }
        }
    });

    leaveButtonConfirmation.addEventListener('click', function() {
        const cardsForLeaving = Array.from(document.querySelectorAll('.toggled-leave-team'));
        let completedRequests = 0;
        let errors = [];
        let errorTeamNames = [];

        for (let card of cardsForLeaving) {
            const teamId = card.querySelector('input[name="team[]"]').value;

            fetch('/leave_team', {
                 method: 'POST',
                 headers: {
                     'Content-Type': 'application/json'
                 },
                 body: JSON.stringify({ 'team_id': teamId })
            })
            .then(res => res.json())
            .then(data => {
                completedRequests++;
                if (!data.success) {
                    errors.push(data.error || "An error occurred while leaving the teams.")
                    errorTeamNames.push(data.name || "Unknown Team");
                }
                if (completedRequests === cardsForLeaving.length) {
                    if (errors.length > 0) {
                        localStorage.setItem('leaveErrors', JSON.stringify(errors));
                        localStorage.setItem('errorTeamNames', JSON.stringify(errorTeamNames));
                    } 
                    selectedTeamIds.clear();
                    window.location.reload();
                }
            })
            .catch(() => {
                completedRequests++;
                errors.push("An error occurred while leaving the teams.");
                errorTeamNames.push("Unknown Team");
                if (completedRequests === cardsForLeaving.length) {
                    if (errors.length > 0) {
                        localStorage.setItem('leaveErrors', JSON.stringify(errors));
                        localStorage.setItem('errorTeamNames', JSON.stringify(errorTeamNames));
                    }
                    selectedTeamIds.clear();
                    window.location.reload();
                }
            });
        }
    });

    function sendFetch(url, payload, feedbackElementId) {
        fetch(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(res => res.json())
        .then(data => {
            const element = document.getElementById(feedbackElementId);
            if (data.success) {
                element.innerHTML = "<i class='text-success'><strong>Looks Good!</strong></i>";
            } else {
                element.innerHTML = `<i class='text-danger'><strong>${data.error}</strong></i>`;
            }
            element.classList.add('text-feedback');
        })
        .catch(error => console.error('Fetch error:', error));
    }

    document.addEventListener('focusout', function (event) {
        if (event.target.id === 'team-name') {
            sendFetch('/check_name', {'name': event.target.value }, 'team-name-feedback');
        }
        
        if (event.target.id === 'team-code') {
            sendFetch('/check_code', {'code': event.target.value }, 'team-code-feedback');
        }
    });
});