(function() {
    'use strict';

    class AutoPagination {
        constructor() {
            this.currentPage = 1;
            this.itemsPerPage = 5;
            this.itemSelector = '.card';
            this.paginationSelector = '.pagination';
            this.allItems = [];
            this.paginationContainer = null;
            
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.init());
            } else {
                this.init();
            }
        }

        init() {
            this.allItems = Array.from(document.querySelectorAll(this.itemSelector));
            if (this.allItems.length === 0) return;
            this.setupPaginationContainer();
            this.updatePagination();
            this.showPage(this.currentPage);
        }

        setupPaginationContainer() {
            this.paginationContainer = document.querySelector(this.paginationSelector);
            
            if (!this.paginationContainer) {
                const nav = document.createElement('nav');
                nav.setAttribute('aria-label', 'Pagination navigation');
                const ul = document.createElement('ul');
                ul.className = 'pagination justify-content-center';
                nav.appendChild(ul);
                
                const container = [
                    document.querySelector('.teams-container'),
                    document.querySelector('.container'),
                    document.querySelector('main'),
                    document.body
                ].find(el => el !== null) || document.body;
                
                container.appendChild(nav);
                this.paginationContainer = ul;
            }
        }

        updatePagination() {
            const totalPages = Math.ceil(this.allItems.length / this.itemsPerPage);
            
            if (totalPages <= 1) {
                this.paginationContainer.style.display = 'none';
                return;
            }
            
            this.paginationContainer.style.display = 'flex';
            this.paginationContainer.innerHTML = '';
            
            this.addPreviousButton();
            this.addPageNumbers(totalPages);
            this.addNextButton(totalPages);
        }

        addPreviousButton() {
            const li = document.createElement('li');
            li.className = `page-item ${this.currentPage === 1 ? 'disabled' : ''}`;
            const btn = document.createElement('button');
            btn.className = 'page-link';
            btn.textContent = 'Previous';
            btn.onclick = () => this.currentPage > 1 && this.goToPage(this.currentPage - 1);
            li.appendChild(btn);
            this.paginationContainer.appendChild(li);
        }

        addNextButton(totalPages) {
            const li = document.createElement('li');
            li.className = `page-item ${this.currentPage === totalPages ? 'disabled' : ''}`;
            const btn = document.createElement('button');
            btn.className = 'page-link';
            btn.textContent = 'Next';
            btn.onclick = () => this.currentPage < totalPages && this.goToPage(this.currentPage + 1);
            li.appendChild(btn);
            this.paginationContainer.appendChild(li);
        }

        addPageNumbers(totalPages) {
            const startPage = Math.max(1, this.currentPage - 2);
            const endPage = Math.min(totalPages, this.currentPage + 2);
            
            if (startPage > 1) {
                this.addPageButton(1);
                if (startPage > 2) this.addEllipsis();
            }
            
            for (let i = startPage; i <= endPage; i++) {
                this.addPageButton(i);
            }
            
            if (endPage < totalPages) {
                if (endPage < totalPages - 1) this.addEllipsis();
                this.addPageButton(totalPages);
            }
        }

        addPageButton(pageNum) {
            const li = document.createElement('li');
            li.className = `page-item ${this.currentPage === pageNum ? 'active' : ''}`;
            const btn = document.createElement('button');
            btn.className = 'page-link';
            btn.textContent = pageNum;
            btn.onclick = () => this.goToPage(pageNum);
            li.appendChild(btn);
            this.paginationContainer.appendChild(li);
        }
        
        addEllipsis() {
            const li = document.createElement('li');
            li.className = 'page-item disabled';
            const span = document.createElement('span');
            span.className = 'page-link';
            span.textContent = '...';
            li.appendChild(span);
            this.paginationContainer.appendChild(li);
        }
        
        goToPage(page) {
            this.currentPage = page;
            this.showPage(this.currentPage);
            this.updatePagination();
            
            document.dispatchEvent(new CustomEvent('paginationPageChange', {
                detail: { 
                    page: this.currentPage,
                    totalPages: this.getTotalPages()
                }
            }));
        }
    
        showPage(page) {
            const startIndex = (page - 1) * this.itemsPerPage;
            const endIndex = startIndex + this.itemsPerPage;
            
            this.allItems.forEach(item => item.style.display = 'none');
            
            for (let i = startIndex; i < endIndex && i < this.allItems.length; i++) {
                this.allItems[i].style.display = 'block';
            }
        }

        getCurrentPage() {
            return this.currentPage;
        }

        getTotalPages() {
            return Math.ceil(this.allItems.length / this.itemsPerPage);
        }

        refresh() {
            this.allItems = Array.from(document.querySelectorAll(this.itemSelector));
            this.updatePagination();
            this.showPage(this.currentPage);
        }

        destroy() {
            if (this.paginationContainer) this.paginationContainer.remove();
            this.allItems.forEach(item => item.style.display = 'block');
        }
    }

    window.AutoPagination = new AutoPagination();
})();