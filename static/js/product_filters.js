document.addEventListener('DOMContentLoaded', function() {
    // Preserve sorting parameters when filtering
    const filterForm = document.getElementById('product-filter-form');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            // Get current URL parameters
            const urlParams = new URLSearchParams(window.location.search);
            const sort = urlParams.get('sort');
            const direction = urlParams.get('direction');
            
            // If we have sorting parameters, add them to the form
            if (sort && direction) {
                const sortInput = document.createElement('input');
                sortInput.type = 'hidden';
                sortInput.name = 'sort';
                sortInput.value = sort;
                
                const directionInput = document.createElement('input');
                directionInput.type = 'hidden';
                directionInput.name = 'direction';
                directionInput.value = direction;
                
                filterForm.appendChild(sortInput);
                filterForm.appendChild(directionInput);
            }
        });
    }

    // Mobile filter toggle button
    const filterToggleBtn = document.createElement('button');
    filterToggleBtn.className = 'btn btn-primary d-md-none position-fixed';
    filterToggleBtn.style.bottom = '20px';
    filterToggleBtn.style.right = '20px';
    filterToggleBtn.style.zIndex = '1000';
    filterToggleBtn.innerHTML = '<i class="fas fa-filter"></i> Filters';
    document.body.appendChild(filterToggleBtn);
    
    // Mobile filter sidebar
    const filterSidebar = document.getElementById('filter-sidebar');
    if (filterSidebar && filterToggleBtn) {
        // Initially hide on mobile
        if (window.innerWidth < 768) {
            filterSidebar.style.display = 'none';
        }
        
        // Toggle filter sidebar on mobile
        filterToggleBtn.addEventListener('click', function() {
            if (filterSidebar.style.display === 'none') {
                filterSidebar.style.display = 'block';
                filterToggleBtn.innerHTML = '<i class="fas fa-times"></i> Close';
            } else {
                filterSidebar.style.display = 'none';
                filterToggleBtn.innerHTML = '<i class="fas fa-filter"></i> Filters';
            }
        });
        
        // Handle window resize
        window.addEventListener('resize', function() {
            if (window.innerWidth >= 768) {
                filterSidebar.style.display = 'block';
                filterToggleBtn.style.display = 'none';
            } else {
                filterSidebar.style.display = 'none';
                filterToggleBtn.style.display = 'block';
            }
        });
    }
    
    // Add event listeners to clear individual filters
    const clearPriceBtn = document.createElement('button');
    clearPriceBtn.className = 'btn btn-sm btn-outline-secondary float-end';
    clearPriceBtn.innerHTML = 'Clear';
    clearPriceBtn.addEventListener('click', function(e) {
        e.preventDefault();
        document.getElementById('price_min').value = '';
        document.getElementById('price_max').value = '';
    });
    
    const priceHeading = document.querySelector('.filter-heading');
    if (priceHeading) {
        priceHeading.appendChild(clearPriceBtn);
    }
});