document.addEventListener('DOMContentLoaded', function() {
    const itemsPerPage = 5;
    const items = document.querySelectorAll('.card');
    
    if (items.length <= itemsPerPage) return; // No pagination needed
    
    let currentPage = 1;
    const totalPages = Math.ceil(items.length / itemsPerPage);
    
    // Create pagination container
    const nav = document.createElement('nav');
    nav.innerHTML = `
        <ul class="pagination justify-content-center">
            <li class="page-item"><button class="page-link" id="prev-btn">Previous</button></li>
            <li class="page-item"><span class="page-link" id="page-info">Page 1 of ${totalPages}</span></li>
            <li class="page-item"><button class="page-link" id="next-btn">Next</button></li>
        </ul>
    `;

    // Add pagination at the bottom of the main content
    const main = document.querySelector('main') || document.body;
    main.appendChild(nav);

    const prevButton = document.getElementById('prev-btn');
    const nextButton = document.getElementById('next-btn');
    const pageInfo = document.getElementById('page-info');
    
    // Show page function
    function showPage(page) {
        const start = (page - 1) * itemsPerPage;
        const end = start + itemsPerPage;
        
        items.forEach((item, index) => {
            item.style.display = (index >= start && index < end) ? 'block' : 'none';
        });
        
        // Update pagination info
        pageInfo.textContent = `Page ${page} of ${totalPages}`;
        prevButton.disabled = page === 1;
        nextButton.disabled = page === totalPages;
    }
    
    // Event listeners
    prevButton.addEventListener('click', () => {
        if (currentPage > 1) {
            currentPage--;
            showPage(currentPage);
        }
    });
    
    nextButton.addEventListener('click', () => {
        if (currentPage < totalPages) {
            currentPage++;
            showPage(currentPage);
        }
    });
    
    // Show first page
    showPage(1);
});
