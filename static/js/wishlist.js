document.addEventListener('DOMContentLoaded', function() {
    function setupQuantityButtons() {
        const decrementBtns = document.querySelectorAll('.decrement-qty');
        const incrementBtns = document.querySelectorAll('.increment-qty');
        const quantityInputs = document.querySelectorAll('.qty_input');

        decrementBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const input = this.nextElementSibling;
                let currentValue = parseInt(input.value);
                if (currentValue > 1) {
                    input.value = currentValue - 1;
                    input.dispatchEvent(new Event('change'));
                }
            });
        });

        incrementBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const input = this.previousElementSibling;
                let currentValue = parseInt(input.value);
                input.value = currentValue + 1;
                input.dispatchEvent(new Event('change'));
            });
        });

        // Ensure manual input is valid
        quantityInputs.forEach(input => {
            input.addEventListener('change', function() {
                // Ensure the value is a positive integer
                let value = parseInt(this.value);
                if (isNaN(value) || value < 1) {
                    this.value = 1;
                }
                // Round to nearest integer
                this.value = Math.round(value);
            });
        });
    }

    // Other existing functionality from previous script
    function setupWishlistToggles() {
        document.querySelectorAll(".wishlist-toggle").forEach(button => {
            button.addEventListener("click", function (event) {
                event.preventDefault();
                let productId = this.dataset.productId;
                let actionUrl = this.dataset.action;
                let heartIcon = this.querySelector('i');

                fetch(actionUrl, {
                    method: "POST",
                    headers: {
                        "X-CSRFToken": getCSRFToken(),
                        "Content-Type": "application/json",
                        "X-Requested-With": "XMLHttpRequest"
                    },
                    body: JSON.stringify({})
                })
                .then(response => {
                    if (!response.ok) {
                        // Fallback to standard link if AJAX fails
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
                            this.dataset.action = "{% url 'wishlist:remove_from_wishlist' 999999 %}".replace('999999', productId);
                        } else {
                            this.classList.remove("in-wishlist");
                            heartIcon.classList.remove("fa-solid");
                            heartIcon.classList.add("fa-regular");
                            this.dataset.action = "{% url 'wishlist:add_to_wishlist' 999999 %}".replace('999999', productId);
                            
                            // Remove the product from the page if on wishlist page
                            if (window.location.pathname.includes('/wishlist/')) {
                                this.closest('.col-sm-6').remove();
                            }
                        }
                        
                        showMessage('success', data.in_wishlist 
                            ? 'Added to wishlist!' 
                            : 'Removed from wishlist!');
                    }
                })
                .catch(error => {
                    console.error("Error:", error);
                    showMessage('error', 'Something went wrong with the wishlist action');
                });
            });
        });
    }

    // CSRF Token Retrieval
    function getCSRFToken() {
        let csrfToken = document.querySelector("[name=csrfmiddlewaretoken]");
        return csrfToken ? csrfToken.value : "";
    }

    // Message Display Functionality
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

    // Initialize all functionality
    function initializeScripts() {
        setupQuantityButtons();
        setupWishlistToggles();
    }

    // Run initialization
    initializeScripts();
});