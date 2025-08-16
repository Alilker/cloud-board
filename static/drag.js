function allowDrop(ev) {
    ev.preventDefault();
}

function dragEnter(ev) {
    ev.preventDefault();
    // Find the closest card-list (in case we're hovering over a card inside it)
    let cardList = ev.target.closest('.card-list');
    if (cardList) {
        cardList.classList.add('drag-over');
    }
}

function dragLeave(ev) {
    // Only remove highlight if we're actually leaving the card-list container
    // (not just moving from one card to another inside it)
    if (!ev.currentTarget.contains(ev.relatedTarget)) {
        ev.currentTarget.classList.remove('drag-over');
    }
}

function drag(ev) {
    // Ensure we always get the parent .card
    let card = ev.target.closest(".card");
    if (!card) {
        console.error('No card found for drag event');
        return;
    }
    
    card.classList.add('dragging');
    ev.dataTransfer.setData("note_id", card.id);
    console.log('Dragging card:', card.id);
}

function dragEnd(ev) {
    let card = ev.target.closest(".card");
    if (card) {
        card.classList.remove('dragging');
    }
    // Remove drag-over class from all lists
    document.querySelectorAll('.card-list').forEach(list => {
        list.classList.remove('drag-over');
    });
}

function drop(ev, newColumnId) {
    ev.preventDefault();
    ev.stopPropagation(); // Prevent event bubbling

    // Find the actual drop zone (card-list) even if we dropped on a card inside it
    let dropZone = ev.target.closest('.card-list');
    if (!dropZone) {
        console.error('Drop target is not a valid drop zone');
        return;
    }

    let noteId = ev.dataTransfer.getData("note_id");
    if (!noteId) {
        console.error('No note_id found in dataTransfer');
        return;
    }

    let cardElement = document.getElementById(noteId);
    if (!cardElement) {
        console.error('Card element not found:', noteId);
        return;
    }

    // Move in the UI to the correct container
    if (newColumnId == "delete") {
        cardElement.remove();
    }
    else {
        dropZone.appendChild(cardElement);
    }
    dropZone.classList.remove('drag-over');

    let numericId = noteId.replace("card-", "");

    console.log('Moving card', numericId, 'to column', newColumnId);

    // Update DB via AJAX
    fetch(`/move_note`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ note_id: numericId, column_id: newColumnId })
    })
    .then(res => res.json())
    .then(data => {
        console.log('Server response:', data);
    })
    .catch(err => {
        console.error('AJAX error:', err);
        // Optionally revert the UI change if server update fails
    });
}