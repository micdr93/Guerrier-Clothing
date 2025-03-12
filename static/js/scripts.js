document.addEventListener('DOMContentLoaded', () => {
  function setupQuantityControls() {
    document.querySelectorAll('.product-quantity-container').forEach(container => {
      const decrementBtn = container.querySelector('.decrement-qty');
      const incrementBtn = container.querySelector('.increment-qty');
      const quantityInput = container.querySelector('.qty_input');

      decrementBtn.addEventListener('click', function(e) {
        e.preventDefault();
        let currentValue = parseInt(quantityInput.value) || 1;
        if (currentValue > 1) {
          quantityInput.value = currentValue - 1;
        }
      });

      incrementBtn.addEventListener('click', function(e) {
        e.preventDefault();
        let currentValue = parseInt(quantityInput.value) || 1;
        if (currentValue < 99) {
          quantityInput.value = currentValue + 1;
        }
      });
    });
  }

  function initMobileSearch() {
    const searchToggler = document.getElementById('search-toggler');
    const mobileSearch = document.getElementById('mobile-search');

    if (searchToggler && mobileSearch) {
      searchToggler.addEventListener('click', () => {
        const bsCollapse = new bootstrap.Collapse(mobileSearch, { toggle: true });
      });
    }
  }

  function initAddToBagAjax() {
    document.querySelectorAll('form[action^="/bag/add/"]').forEach(form => {
      form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const match = this.action.match(/\/bag\/add\/(\d+)\//);
        if (!match) return;
        
        const productId = match[1];
        const quantity = this.querySelector('input[name="quantity"]').value;
        const productSize = this.querySelector('select[name="product_size"]')?.value;
        
        const formData = new FormData();
        formData.append('quantity', quantity);
        if (productSize) {
            formData.append('product_size', productSize);
        }
        
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
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
                const bagCount = document.getElementById('bag-count');
                if (bagCount) {
                    bagCount.textContent = data.item_count;
                }
                
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

  function initBagUpdates() {
    document.querySelectorAll('.update-qty').forEach(button => {
      button.addEventListener('click', function(e) {
        e.preventDefault();
        const form = this.closest('form');
        if (!form) return;
        
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
                location.reload();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('error', 'Error updating cart');
        });
      });
    });
    
    document.querySelectorAll('.remove-item-form').forEach(form => {
      form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        fetch(form.action, {
          method: 'POST',
          body: new FormData(form),
          headers: {
            'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
            'X-Requested-With': 'XMLHttpRequest'
          }
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            form.closest('.cart-item').remove();
            
            if (document.querySelectorAll('.cart-item').length === 0) {
              location.reload();
            }
          } else {
            showMessage('error', "There was an error removing the product.");
          }
        })
        .catch(error => {
          console.error('Error:', error);
          showMessage('error', 'Error removing item');
        });
      });
    });
    
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

  function initWishlistToggle() {
    document.querySelectorAll('.wishlist-toggle').forEach(button => {
      button.addEventListener('click', function(e) {
        e.preventDefault();
        const productId = this.dataset.product_id;
        const actionUrl = this.dataset.action;
        
        fetch(actionUrl, {
          method: "POST",
          headers: {
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest"
          },
          body: JSON.stringify({})
        })
        .then(response => response.json())
        .then(data => {
          if (data.success) {
            this.classList.toggle('in-wishlist');
            const icon = this.querySelector('i');
            if (icon) {
              icon.classList.toggle('fa-regular');
              icon.classList.toggle('fa-solid');
            }
          }
        })
        .catch(error => console.error("Error:", error));
      });
    });
  }

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

  function getCSRFToken() {
    const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return csrfToken ? csrfToken.value : '';
  }

  setupQuantityControls();
  initMobileSearch();
  initAddToBagAjax();
  initBagUpdates();
  initWishlistToggle();
});