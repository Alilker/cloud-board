document.addEventListener('DOMContentLoaded', function() {
    let selectionMode = false;
    let selectedTeamIds = new Set();

    const leaveButtonToggle = document.getElementById('toggle-leave');
    const leaveButton = document.getElementById('leave-button');
    const leaveButtonConfirmation = document.getElementById('leave-button-confirmation');

    function restoreSelections() {
        const cards = document.getElementsByClassName('card-body');
        
        for (let card of cards) {
            if (card.closest('.card').style.display === 'none') continue;

            const teamId = card.querySelector('input[name="team[]"]').value;
            if (selectedTeamIds.has(teamId)) {
                card.classList.add('toggled-leave-team');
            }
        }
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

    const cards = document.getElementsByClassName('card-body');

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

            const selectedCards = document.getElementsByClassName('toggled-leave-team').length;
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
        const cardsForLeaving = Array.from(document.getElementsByClassName('toggled-leave-team'));
        let completedRequests = 0;

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
                        alert("Failed to leave team.");
                    }
                    if (completedRequests === cardsForLeaving.length) {
                        selectedTeamIds.clear();
                        window.location.reload();
                    }
                })
                .catch(() => {
                    completedRequests++;
                    alert("Failed to leave team.");
                    if (completedRequests === cardsForLeaving.length) {
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
            const elementId = document.getElementById(feedbackElementId);
            if (data.success) {
                elementId.innerHTML = "<i class='text-success'><strong>Looks Good!</strong></i>";
            } else {
                elementId.innerHTML = `<i class='text-danger'><strong>${data.error}</strong></i>`;
            }
            elementId.classList.add('text-feedback');
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