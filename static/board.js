document.addEventListener('DOMContentLoaded', function() {

    // Initialize variables that get used in multiple places
    let currentEditNoteId;
    let currentColumnId;

    const teamName = document.getElementById("team-name").value;
    const topicName = document.getElementById("topic-name").value;

    // Function for mobile detection as drag and drop doesn't work on mobile
    // Reference resource: https://www.reddit.com/r/neocities/comments/1c4b0r1/comment/kzmt0sq/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button
    function isMobile() {
        const isMobile = window.matchMedia("(any-hover:none)").matches;

        if (isMobile) {

            // Add mobile-specific column class that changes width
            document.querySelectorAll('.accordion, .delete-column').forEach(accordion => {
                accordion.classList.add('mobile-column');
            });

            // Show mobile warning modal
            const mobileWarningModal = new bootstrap.Modal(document.querySelector('#mobile-warning-modal'));
            mobileWarningModal.show();
        }
    }

    // Function for displaying errors
    function showError(message) {
        const errorModal = new bootstrap.Modal(document.querySelector('#error-modal'));
        const errorMessage = document.querySelector('#error-modal .errors');

        errorMessage.innerHTML = message;
        errorModal.show();
    }

    // Function for initializing note dragging
    function initializeNoteDrag() {

    const privilege = document.getElementById('privilege').value;
    const is_authorized = privilege === 'admin' || privilege === 'edit';

        // Event listeners for drag events
        document.addEventListener('dragstart', function(event) {
            const card = event.target.closest('.draggable-card');
            if (!card) return;

            // Don't allow announcement notes to be dragged if user isn't authorized
            const parentAccordion = card.closest('.accordion');
            if (parentAccordion && parentAccordion.dataset.status === 'announcements' && !is_authorized) {
                event.preventDefault();
                return;
            }

            event.dataTransfer.setData("text", card.dataset.noteId);
        });

        document.addEventListener('dragover', function(event) {
            event.preventDefault();
        });

        document.addEventListener('drop', function(event) {
            
            // Get the closest column and check if it exists
            let dropZone = event.target.closest('.delete-column');
            if (!dropZone) {
                dropZone = event.target.closest('.accordion');
            }
            if (!dropZone) return;

            // Don't allow announcement notes to be dropped if user isn't authorized
            if (dropZone.dataset.status === 'announcement' && !['admin', 'edit'].includes(privilege)) {
                return;
            }

            const draggedNoteId = event.dataTransfer.getData("text");
            const draggedNote = document.querySelector(`[data-note-id="${draggedNoteId}"]`);
            
            dropZone.querySelector('.cards-section').appendChild(draggedNote);
            
            // On drag permanently update note state
            fetch(`/move_note/${teamName}/${topicName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    note_id: draggedNoteId, 
                    column_id: dropZone.dataset.status 
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.reload();
                } 
                else {
                    // Handle errors
                    showError(data.error || 'An error occurred, please try again later');
                }
            })
            .catch(error => {
                console.error('API error:', error);
                showError('A network error occurred, please try again later');
            });
        });
    }

    // Function for initializing the note adding
    function initializeAddNote() {

        const noteText = document.getElementById('add-note-content');
        const addNoteButton = document.getElementById('add-note-button');

        // Edit modal text-area to clear content on open
        document.getElementById('add-note-modal').addEventListener('show.bs.modal', function(event) {
            currentColumnId = event.relatedTarget.dataset.status;
            document.getElementById('add-note-content').value = '';
            document.getElementById('add-note-content').focus();
            addNoteButton.disabled = true;
        });

        // Only accept not empty input
        noteText.addEventListener('input', function() {
            addNoteButton.disabled = (noteText.value.trim() === '');
        });

        // On click create the new note
        document.getElementById('add-note-button').addEventListener('click', function() {
            const noteText = document.getElementById('add-note-content').value.trim();

            fetch(`/create_note/${teamName}/${topicName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    content: noteText, 
                    status: currentColumnId })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.reload();
                } 
                else {
                    // Handle errors
                    showError(data.error || 'An error occurred, please try again later');
                }
            })
            .catch(error => {
                console.error(error);
                showError('A network error occurred, please try again later');
            });
        });
    }

    // Initialize note editing
    function initializeEditNote() {

        const editNoteButton = document.getElementById('edit-note-button');
        const editTextarea = document.getElementById('edit-note-content');

        // Check if a note is clicked
        document.addEventListener('click', function(event) {
            const noteCard = event.target.closest('.draggable-card');
            if (noteCard) {
                currentEditNoteId = noteCard.dataset.noteId;
                document.getElementById('edit-note-content').value = noteCard.querySelector('.card-text').textContent;
                editNoteButton.disabled = true;
                new bootstrap.Modal(document.getElementById('edit-note-modal')).show();
            }
        });

        // Enable the edit button when the textarea is modified in any way
        editTextarea.addEventListener('input', function() {
            editNoteButton.disabled = false;
        });

        // On click save the edited note
        document.getElementById('edit-note-button').addEventListener('click', function() {
            const editContent = document.getElementById('edit-note-content').value.trim();

            fetch(`/edit_note/${teamName}/${topicName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    note_id: currentEditNoteId, 
                    content: editContent })
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
            .catch(error => {
                console.error(error);
                showError('A network error occurred, please try again later');
            });
        });
    }

    // Initialize functionality
    isMobile();
    initializeNoteDrag();
    initializeAddNote();
    initializeEditNote();
});