document.addEventListener('DOMContentLoaded', function() {

    // Button declarations
    const createTopicSubmit = document.querySelector('#create-topic-submit');
    const editTopicSubmit = document.querySelector('#topic-changes-submit');

    // Get current team name from hidden input
    const teamName = document.getElementById('team-name')?.value.trim();

    // Function for displaying errors
    function showError(message) {
        const errorModal = new bootstrap.Modal(document.querySelector('#error-modal'));
        const errorMessage = document.querySelector('#error-modal .errors');
        
        errorMessage.innerHTML = message;
        errorModal.show();
    }


    // Function for create topic form submission initialization
    function initializeCreateNewTopic() {

        // Enable the submit button when there is input
        let topicName;
        document.addEventListener('input', function() {
            topicName = document.getElementById('new-topic-name')?.value.trim();
            createTopicSubmit.disabled = (topicName === '');
        });

        // On click submit the form
        createTopicSubmit.addEventListener('click', function(event) {
            event.preventDefault();
            topicName = document.getElementById('new-topic-name')?.value.trim();

            fetch(`/create_topic_api/${teamName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    "topic_name": topicName
                })
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    window.location.href = `/edit_team/${teamName}`;
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

    // Function for edit topic form submission initialization
    function initializeEditTopic() {

        // Enable the submit button when there is only one checkbox checked
        document.addEventListener('change', function() {
            const checkedCount = document.querySelectorAll('input[type="checkbox"][name="topic-checkbox"]:checked').length;
            editTopicSubmit.disabled = (checkedCount !== 1);
        });

        // On click submit the form
        editTopicSubmit.addEventListener('click', function(event) {
            event.preventDefault();

            const requestedName = document.getElementById('edit-topic-name')?.value.trim();
            const currentTopicName = document.querySelector('input[type="checkbox"][name="topic-checkbox"]:checked')?.value;

            fetch(`/edit_topic_api/${teamName}/${currentTopicName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    "new_name": requestedName
                })
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
    initializeCreateNewTopic();
    initializeEditTopic();

});

