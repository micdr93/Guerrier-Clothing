document.addEventListener('DOMContentLoaded', function() {
    function setupQuantityButtons() {
        const decrementBtns = document.querySelectorAll('.decrement-qty');
        const incrementBtns = document.querySelectorAll('.increment-qty');
        const quantityInputs = document.querySelectorAll('.qty_input');

        decrementBtns.forEach(btn => {
            btn.addEventListener('click', function(event) {
                event.preventDefault();
                // Find the .input-group parent, then find the .qty_input inside it
                const inputGroup = this.closest('.input-group');
                if (!inputGroup) {
                    console.error('No input-group found for decrement button.');
                    return;
                }
                const input = inputGroup.querySelector('.qty_input');
                if (!input) {
                    console.error('Quantity input not found for decrement button.');
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
                // Find the .input-group parent, then find the .qty_input inside it
                const inputGroup = this.closest('.input-group');
                if (!inputGroup) {
                    console.error('No input-group found for increment button.');
                    return;
                }
                const input = inputGroup.querySelector('.qty_input');
                if (!input) {
                    console.error('Quantity input not found for increment button.');
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

    // (Optional) If you have wishlist toggles or other code, keep them here...
    // function setupWishlistToggles() { ... }

    function initializeScripts() {
        setupQuantityButtons();
        // setupWishlistToggles();
        // ... any other init code
    }

    initializeScripts();
});
