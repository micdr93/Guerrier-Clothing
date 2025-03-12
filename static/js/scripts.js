// Replace your entire script.js file with this code

// Global flag to prevent multiple initializations
let quantityHandlersInitialized = false;

document.addEventListener('DOMContentLoaded', () => {
  // Mobile search functionality
  const searchToggler = document.getElementById('search-toggler');
  const mobileSearch = document.getElementById('mobile-search');

  if (searchToggler && mobileSearch) {
      searchToggler.addEventListener('click', () => {
          const bsCollapse = new bootstrap.Collapse(mobileSearch, { toggle: true });
      });
  }

  // Only initialize quantity inputs once
  if (!quantityHandlersInitialized) {
    initQuantityInputs();
    quantityHandlersInitialized = true;
  }
  
  // AJAX add to bag functionality
  initAddToBagAjax();
  
  // AJAX update/remove from bag functionality
  initUpdateRemoveBagAjax();
});

// Handle quantity input functionality
function initQuantityInputs() {
  console.log("Initializing quantity inputs - removing old handlers first");
  
  // First, remove ALL existing handlers by cloning and replacing elements
  document.querySelectorAll('.increment-qty, .decrement-qty').forEach(button => {
    const newButton = button.cloneNode(true);
    if (button.parentNode) {
      button.parentNode.replaceChild(newButton, button);
    }
  });
  
  document.querySelectorAll('.qty_input').forEach(input => {
    const newInput = input.cloneNode(true);
    if (input.parentNode) {
      input.parentNode.replaceChild(newInput, input);
    }
  });
  
  // Now add fresh handlers with stopPropagation to prevent bubbling
  document.querySelectorAll('.increment-qty').forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation(); // Prevent event bubbling
      
      const itemId = this.dataset.item_id;
      // Use closest to find the input in the same form/container only
      const input = this.closest('.d-flex, .input-group').querySelector('.qty_input');
      
      if (input) {
        const currentValue = parseInt(input.value);
        if (currentValue < 99) {
          input.value = currentValue + 1;
          console.log(`Incremented to ${input.value}`);
        }
      }
    });
  });
  
  document.querySelectorAll('.decrement-qty').forEach(button => {
    button.addEventListener('click', function(e) {
      e.preventDefault();
      e.stopPropagation(); // Prevent event bubbling
      
      const itemId = this.dataset.item_id;
      // Use closest to find the input in the same form/container only
      const input = this.closest('.d-flex, .input-group').querySelector('.qty_input');
      
      if (input) {
        const currentValue = parseInt(input.value);
        if (currentValue > 1) {
          input.value = currentValue - 1;
          console.log(`Decremented to ${input.value}`);
        }
      }
    });
  });
}

function handleEnableDisable(itemId) {
  // Intentionally left blank - we'll handle enabling/disabling in the click handlers directly
}

// AJAX add to bag functionality
function initAddToBagAjax() {
  document.querySelectorAll('form[action^="/bag/add/"]').forEach(form => {
      form.addEventListener('submit', function(e) {
          e.preventDefault();
          
          // Extract the product ID from the form action URL
          const productId = this.action.match(/\/bag\/add\/(\d+)\//)[1];
          const quantity = this.querySelector('input[name="quantity"]').value;
          const productSize = this.querySelector('select[name="product_size"]')?.value;
          
          // Create form data to send
          const formData = new FormData();
          formData.append('quantity', quantity);
          if (productSize) {
              formData.append('product_size', productSize);
          }
          
          // Get CSRF token
          const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
          
          // Send AJAX request
          fetch(this.action, {
              method: 'POST',
              headers: {
                  'X-CSRFToken': csrfToken,
                  'X-Requested-With': 'XMLHttpRequest'
              },
              body: formData
          })
          .then(response => {
              if (!response.ok) {
                  throw new Error('Network response was not ok');
              }
              return response.json();
          })
          .then(data => {
              if (data.success) {
                  // Update mini-bag count in navbar if it exists
                  const bagCount = document.getElementById('bag-count');
                  if (bagCount) {
                      bagCount.textContent = data.item_count;
                  }
                  
                  // Show success message
                  showMessage('success', `Added to your bag!`);
              } else {
                  showMessage('error', data.error || 'There was an error adding this item');
              }
          })
          .catch(error => {
              console.error('Error:', error);
              showMessage('error', 'Something went wrong. Please try again.');
          });
      });
  });
}

// AJAX update/remove bag functionality
function initUpdateRemoveBagAjax() {
  // Update quantity in bag
  document.querySelectorAll('.update-qty').forEach(button => {
      button.addEventListener('click', function(e) {
          e.preventDefault();
          const form = this.closest('form');
          const url = form.action;
          const formData = new FormData(form);
          
          fetch(url, {
              method: 'POST',
              headers: {
                  'X-CSRFToken': getCSRFToken(),
                  'X-Requested-With': 'XMLHttpRequest'
              },
              body: formData
          })
          .then(response => response.json())
          .then(data => {
              if (data.success) {
                  // Refresh the page to show updated cart
                  location.reload();
              }
          })
          .catch(error => {
              console.error('Error:', error);
              showMessage('error', 'Error updating cart');
          });
      });
  });
  
  // Remove item from bag
  document.querySelectorAll('.remove-item').forEach(button => {
      button.addEventListener('click', function(e) {
          e.preventDefault();
          const productId = this.dataset.product_id;
          const size = this.dataset.size || null;
          const url = `/bag/remove/${productId}/`;
          
          const formData = new FormData();
          if (size) formData.append('size', size);
          
          fetch(url, {
              method: 'POST',
              headers: {
                  'X-CSRFToken': getCSRFToken(),
                  'X-Requested-With': 'XMLHttpRequest'
              },
              body: formData
          })
          .then(response => response.json())
          .then(data => {
              if (data.success) {
                  // Refresh the page to show updated cart
                  location.reload();
              }
          })
          .catch(error => {
              console.error('Error:', error);
              showMessage('error', 'Error removing item');
          });
      });
  });
}

// Helper function to display messages
function showMessage(type, message) {
  const messageContainer = document.createElement('div');
  messageContainer.className = `alert alert-${type === 'success' ? 'success' : 'danger'} position-fixed`;
  messageContainer.style.top = '10px';
  messageContainer.style.right = '10px';
  messageContainer.style.zIndex = '9999';
  messageContainer.innerHTML = message;
  
  document.body.appendChild(messageContainer);
  
  // Auto dismiss after 3 seconds
  setTimeout(() => {
      messageContainer.style.opacity = '0';
      messageContainer.style.transition = 'opacity 0.5s ease';
      
      setTimeout(() => {
          document.body.removeChild(messageContainer);
      }, 500);
  }, 3000);
}

// Helper function to get CSRF token
function getCSRFToken() {
  const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
  return csrfToken ? csrfToken.value : '';
}

// Call this if you need to reinitialize (e.g. after AJAX content loads)
function reinitializeQuantityControls() {
  // Force reinitialization
  quantityHandlersInitialized = false;
  initQuantityInputs();
  quantityHandlersInitialized = true;
}