/* jshint esversion: 6 */
document.addEventListener('DOMContentLoaded', function() {
    // -----------------------------
    // Quantity Buttons Functionality
    // -----------------------------
    function setupQuantityButtons() {
        const decrementBtns = document.querySelectorAll('.decrement-qty');
        const incrementBtns = document.querySelectorAll('.increment-qty');
        const quantityInputs = document.querySelectorAll('.qty_input');

        decrementBtns.forEach(btn => {
            btn.addEventListener('click', function(event) {
                event.preventDefault();
                // Use closest() to reliably find the common parent container
                const inputGroup = this.closest('.input-group');
                if (!inputGroup) {
                    console.error('No .input-group found for decrement button.');
                    return;
                }
                const input = inputGroup.querySelector('.qty_input');
                if (!input) {
                    console.error('Quantity input not found in decrement button container.');
                    return;
                }
                const minVal = parseInt(input.getAttribute('min'), 10) || 1;
                let currentValue = parseInt(input.value, 10) || minVal;
                if (currentValue > minVal) {
                    input.value = currentValue - 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
        });

        incrementBtns.forEach(btn => {
            btn.addEventListener('click', function(event) {
                event.preventDefault();
                const inputGroup = this.closest('.input-group');
                if (!inputGroup) {
                    console.error('No .input-group found for increment button.');
                    return;
                }
                const input = inputGroup.querySelector('.qty_input');
                if (!input) {
                    console.error('Quantity input not found in increment button container.');
                    return;
                }
                const maxVal = parseInt(input.getAttribute('max'), 10) || 99;
                let currentValue = parseInt(input.value, 10) || 1;
                if (currentValue < maxVal) {
                    input.value = currentValue + 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
        });

        quantityInputs.forEach(input => {
            input.addEventListener('change', function() {
                const minVal = parseInt(this.getAttribute('min'), 10) || 1;
                const maxVal = parseInt(this.getAttribute('max'), 10) || 99;
                let value = parseInt(this.value, 10);
                if (isNaN(value) || value < minVal) {
                    this.value = minVal;
                } else if (value > maxVal) {
                    this.value = maxVal;
                } else {
                    this.value = Math.round(value);
                }
            });
        });
    }

    // -----------------------------
    // Wishlist Toggle Functionality
    // -----------------------------
    function setupWishlistToggles() {
        document.querySelectorAll(".wishlist-toggle").forEach(button => {
            // Remove any existing listener to prevent duplicates
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
        const formData = new FormData(); // no extra data needed

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
                // Fallback to a full page reload if AJAX fails
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
                    
                    // Optionally remove the product element if on a wishlist page
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
            console.error("Wishlist toggle error:", error);
            showMessage('error', 'Something went wrong with the wishlist action');
        });
    }

    // Helper function to retrieve CSRF Token from the page
    function getCSRFToken() {
        const csrfElem = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfElem ? csrfElem.value : "";
    }

    // Function to display messages to the user
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

    // -----------------------------
    // Initialize all functionalities
    // -----------------------------
    function initializeScripts() {
        setupQuantityButtons();
        setupWishlistToggles();
    }

    initializeScripts();
});
