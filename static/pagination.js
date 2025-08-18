document.addEventListener('DOMContentLoaded', function() {
    const itemsPerPage = 5;
    const items = document.querySelectorAll('.card');

    // If there's only one page, no pagination is needed
    if (items.length <= itemsPerPage) {
        return;
    }

    // Calculate the total number of pages and initialize current page counter
    let currentPage = 1;
    const totalPages = Math.ceil(items.length / itemsPerPage);

    // Initialize pagination elements
    const paginationContainer = document.querySelector('.pagination');
    const prevButton = document.getElementById('prev-btn');
    const nextButton = document.getElementById('next-btn');
    const pageInfo = document.getElementById('page-info');
    
    // Show pagination and set initial page info
    paginationContainer.removeAttribute('hidden');
    pageInfo.textContent = `Page 1 of ${totalPages}`;



    // Show page function
    function showPage(page) {
        const start = (page - 1) * itemsPerPage;
        const end = start + itemsPerPage;

        // Show or hide items
        items.forEach((item, index) => {
            item.style.display = (index >= start && index < end) ? 'block' : 'none';
        });
        
        // Update sections (dedicated section for teams.html)
        const yourTeamsSection = document.getElementById('your-teams-section');
        const otherTeamsSection = document.getElementById('other-teams-section');

        // If the your teams section exists, check for visible cards and update the container
        if (yourTeamsSection) {
            const cards = yourTeamsSection.querySelectorAll('.card');
            let hasVisibleCards = false;
            for (let i = 0; i < cards.length; i++) {

                if (cards[i].style.display !== 'none') {
                    hasVisibleCards = true;
                    break;
                }
            }
            yourTeamsSection.style.display = hasVisibleCards ? 'block' : 'none';
        }

        // If the other teams section exists, check for visible cards and update the container
        if (otherTeamsSection) {
            const cards = otherTeamsSection.querySelectorAll('.card');
            let hasVisibleCards = false;
            for (let i = 0; i < cards.length; i++) {
                if (cards[i].style.display !== 'none') {
                    hasVisibleCards = true;
                    break;
                }
            }
            otherTeamsSection.style.display = hasVisibleCards ? 'block' : 'none';
        }
        
        // Update pagination controls
        pageInfo.textContent = `Page ${page} of ${totalPages}`;
        prevButton.disabled = page === 1;
        nextButton.disabled = page === totalPages;

    }

    // Function for initializing pagination by adding event listeners to the page buttons
    function updatePagination() {

        // Add the button event listeners
        prevButton.onclick = () => {
            if (currentPage > 1) {
                currentPage--;
                showPage(currentPage);
            }
        };
    
        nextButton.onclick = () => {
            if (currentPage < totalPages) {
                currentPage++;
                showPage(currentPage);
            }
        };
    };
    
    // Initialize functionality based on execution order
    showPage(1);
    updatePagination();
});
