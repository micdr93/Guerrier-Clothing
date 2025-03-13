document.addEventListener('DOMContentLoaded', function() {
    // Setup Quantity Buttons
    function setupQuantityButtons() {
        const decrementBtns = document.querySelectorAll('.decrement-qty');
        const incrementBtns = document.querySelectorAll('.increment-qty');
        const quantityInputs = document.querySelectorAll('.qty_input');

        decrementBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const input = this.nextElementSibling;
                let currentValue = parseInt(input.value) || 1;
                if (currentValue > 1) {
                    input.value = currentValue - 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
        });

        incrementBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const input = this.previousElementSibling;
                let currentValue = parseInt(input.value) || 1;
                input.value = currentValue + 1;
                input.dispatchEvent(new Event('change'));
            });
        });

        quantityInputs.forEach(input => {
            input.addEventListener('change', function() {
                let value = parseInt(this.value);
                if (isNaN(value) || value < 1) {
                    this.value = 1;
                }
                this.value = Math.round(this.value);
            });
        });
    }

    // Wishlist Toggle Handlers
    function setupWishlistToggles() {
        document.querySelectorAll(".wishlist-toggle").forEach(button => {
            // Remove any existing listener (if any) to prevent duplicates
            button.removeEventListener('click', handleWishlistToggle);
            button.addEventListener('click', handleWishlistToggle);
        });
    }

    function handleWishlistToggle(event) {
        event.preventDefault();
        event.stopPropagation();
        const productId = this.dataset.productId;
        const actionUrl = this.dataset.action;
        const heartIcon = this.querySelector('i');
        const formData = new FormData(); // Empty formData

        fetch(actionUrl, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCSRFToken(),
                "X-Requested-With": "XMLHttpRequest"
            },
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                // Fallback to full page load if AJAX fails
                window.location.href = actionUrl;
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                if (data.in_wishlist) {
                    this.classList.add("in-wishlist");
                    heartIcon.classList.remove("fa-regular");
                    heartIcon.classList.add("fa-solid");
                    this.dataset.action = `/wishlist/remove/${productId}/`;
                } else {
                    this.classList.remove("in-wishlist");
                    heartIcon.classList.remove("fa-solid");
                    heartIcon.classList.add("fa-regular");
                    this.dataset.action = `/wishlist/add/${productId}/`;
                    
                    // Optionally remove the product from the page on wishlist pages
                    if (window.location.pathname.includes('/wishlist/')) {
                        const productElement = this.closest('.col-sm-6, .col-md-4, .col-lg-3');
                        if (productElement) {
                            productElement.remove();
                        }
                    }
                }
                showMessage('success', data.message);
            } else {
                showMessage('error', data.message || 'Error updating wishlist');
            }
        })
        .catch(error => {
            console.error("Error:", error);
            showMessage('error', 'Something went wrong with the wishlist action');
        });
    }

    // Helper to retrieve CSRF Token
    function getCSRFToken() {
        const csrfElem = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfElem ? csrfElem.value : "";
    }

    // Message display function
    function showMessage(type, message) {
        const messageContainer = document.createElement('div');
        messageContainer.className = `alert alert-${type === 'success' ? 'success' : 'danger'} position-fixed`;
        messageContainer.style.top = '10px';
        messageContainer.style.right = '10px';
        messageContainer.style.zIndex = '9999';
        messageContainer.innerHTML = message;
        document.body.appendChild(messageContainer);
        
        setTimeout(() => {
            messageContainer.style.opacity = '0';
            messageContainer.style.transition = 'opacity 0.5s ease';
            setTimeout(() => {
                document.body.removeChild(messageContainer);
            }, 500);
        }, 3000);
    }

    // Initialize all scripts
    function initializeScripts() {
        setupQuantityButtons();
        setupWishlistToggles();
    }

    initializeScripts();
});
