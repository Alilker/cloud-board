let currentTopicName;

document.addEventListener('DOMContentLoaded', function() {

    // Button declarations
    const createTopicSubmit = document.querySelector('#create-topic-submit');
    const editTopicSubmit = document.querySelector('#topic-changes-submit');

    // Get team ID and current team name from hidden inputs
    const currentTeamName = document.getElementById('team-name')?.value.trim();

    // Function for displaying errors
    function showError(message) {
        const errorModal = new bootstrap.Modal(document.querySelector('#error-modal'));
        const errorMessage = document.querySelector('#error-modal .errors');
        errorMessage.innerHTML = message;
        errorModal.show();
    }


    // Function for create team form submission initialization
    function initializeCreateNewTopic() {

        let topicName;
        document.addEventListener('input', function() {
            topicName = document.getElementById('new-topic-name')?.value.trim();
            createTopicSubmit.disabled = (topicName === '');
        });

        createTopicSubmit.addEventListener('click', function(event) {
            event.preventDefault();
            topicName = document.getElementById('new-topic-name')?.value.trim();
            // Submit create topic form
            fetch(`/create_topic_api/${currentTeamName}/${currentTopicName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    "topic_name": topicName
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

    // Function for create team form submission initialization
    function initializeEditTopic() {


        editTopicSubmit.addEventListener('click', function(event) {
            event.preventDefault();

            const topicName = document.getElementById('edit-topic-name')?.value.trim();
            // Submit create topic form
            fetch(`/edit_topic_api/${currentTeamName}/${currentTopicName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    "topic_name": topicName
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

// I couldn't get this to work inside of the other DOM content loader, but since it's
// not a big deal I just left it like this
let topicChangesSubmit;
document.addEventListener('DOMContentLoaded', function() {
    topicChangesSubmit = document.getElementById('topic-changes-submit');
    topicChangesSubmit.disabled = true;
});

// Function to check if only one checkbox is checked
function checkboxCountChecker() {
    const checkedCount = document.querySelectorAll('input[type="checkbox"][name="topic-checkbox"]:checked').length;
    const currentTopicName = document.querySelector('input[type="checkbox"][name="topic-checkbox"]:checked')?.value;
    topicChangesSubmit.disabled = (checkedCount !== 1);
}

