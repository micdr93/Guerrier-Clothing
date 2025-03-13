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

  // Handle wishlist toggle actions
  function handleWishlistToggle(event) {
      event.preventDefault();
      event.stopPropagation(); // Stop event from bubbling up
      
      let productId = this.dataset.productId;
      let actionUrl = this.dataset.action;
      let heartIcon = this.querySelector('i');

      // Create FormData instead of JSON
      const formData = new FormData();
      
      fetch(actionUrl, {
          method: "POST",
          headers: {
              "X-CSRFToken": getCSRFToken(),
              "X-Requested-With": "XMLHttpRequest"
          },
          body: formData // Send FormData instead of JSON
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
                  // Update action URL to remove
                  this.dataset.action = `/wishlist/remove/${productId}/`;
              } else {
                  this.classList.remove("in-wishlist");
                  heartIcon.classList.remove("fa-solid");
                  heartIcon.classList.add("fa-regular");
                  // Update action URL to add
                  this.dataset.action = `/wishlist/add/${productId}/`;
                  
                  // Remove the product from the page if on wishlist page
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

  // Setup wishlist toggles
  function setupWishlistToggles() {
      document.querySelectorAll(".wishlist-toggle").forEach(button => {
          // Remove any existing event listeners to prevent duplicates
          button.removeEventListener('click', handleWishlistToggle);
          // Add event listener
          button.addEventListener('click', handleWishlistToggle);
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