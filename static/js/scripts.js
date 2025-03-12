document.addEventListener('DOMContentLoaded', () => {
  // Mobile search functionality
  const searchToggler = document.getElementById('search-toggler');
  const mobileSearch = document.getElementById('mobile-search');

  if (searchToggler && mobileSearch) {
      searchToggler.addEventListener('click', () => {
          const bsCollapse = new bootstrap.Collapse(mobileSearch, { toggle: true });
      });
  }

  // Quantity input handling for product detail page
  initQuantityInputs();
  
  // AJAX add to bag functionality
  initAddToBagAjax();
  
  // AJAX update/remove from bag functionality
  initUpdateRemoveBagAjax();
});

// Handle quantity input functionality
function initQuantityInputs() {
  // Handle quantity increments and decrements
  document.querySelectorAll('.increment-qty, .decrement-qty').forEach(button => {
      button.addEventListener('click', function(e) {
          e.preventDefault();
          const itemId = this.dataset.item_id;
          const input = document.querySelector(`.qty_input[data-item_id="${itemId}"]`);
          const currentValue = parseInt(input.value);
          
          if (this.classList.contains('increment-qty') && currentValue < 99) {
              input.value = currentValue + 1;
          } else if (this.classList.contains('decrement-qty') && currentValue > 1) {
              input.value = currentValue - 1;
          }
          
          // Update any enabled/disabled states
          handleEnableDisable(itemId);
      });
  });
  
  // Initialize all quantity inputs
  document.querySelectorAll('.qty_input').forEach(input => {
      input.addEventListener('change', function() {
          const itemId = this.dataset.item_id;
          handleEnableDisable(itemId);
      });
      
      // Set initial state
      const itemId = input.dataset.item_id;
      handleEnableDisable(itemId);
  });
}

function handleEnableDisable(itemId) {
  const input = document.querySelector(`.qty_input[data-item_id="${itemId}"]`);
  if (!input) return;
  
  const currentValue = parseInt(input.value);
  const minusDisabled = currentValue < 2;
  const plusDisabled = currentValue > 98;
  
  const minusButton = document.querySelector(`.decrement-qty[data-item_id="${itemId}"]`);
  const plusButton = document.querySelector(`.increment-qty[data-item_id="${itemId}"]`);
  
  if (minusButton) minusButton.disabled = minusDisabled;
  if (plusButton) plusButton.disabled = plusDisabled;
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