// Wait for the document to be fully loaded before executing code
document.addEventListener('DOMContentLoaded', function() {
    console.log('Stripe Elements script loaded');
    
    // Get Stripe keys from hidden elements in the page
    const stripePublicKey = document.getElementById('id_stripe_public_key').textContent.trim();
    const clientSecret = document.getElementById('id_client_secret').textContent.trim();
    
    // Log for debugging
    console.log('Public key loaded:', stripePublicKey ? 'Yes' : 'No');
    console.log('Client secret loaded:', clientSecret ? 'Yes' : 'No');
    
    // Exit if required keys aren't available
    if (!stripePublicKey) {
        console.error('Stripe public key is missing!');
        displayError('Configuration error with payment system. Please contact support.');
        return;
    }
    
    if (!clientSecret) {
        console.error('Client secret is missing!');
        displayError('Configuration error with payment system. Please contact support.');
        return;
    }
    
    // Initialize Stripe with the public key
    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();
    
    // Style the card element
    const style = {
        base: {
            color: '#32325d',
            fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
            fontSmoothing: 'antialiased',
            fontSize: '16px',
            '::placeholder': {
                color: '#aab7c4'
            }
        },
        invalid: {
            color: '#dc3545',
            iconColor: '#dc3545'
        }
    };
    
    // Create the card element
    const card = elements.create('card', {
        style: style,
        hidePostalCode: true
    });
    
    // Mount the card element to the DOM
    console.log('Mounting card element');
    card.mount('#card-element');
    
    // Handle validation errors on the card element
    card.addEventListener('change', function(event) {
        const errorElement = document.getElementById('card-errors');
        if (event.error) {
            errorElement.innerHTML = `
                <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                </span>
                <span>${event.error.message}</span>
            `;
        } else {
            errorElement.textContent = '';
        }
    });
    
    // Handle form submission
    const form = document.getElementById('payment-form');
    const submitButton = document.getElementById('submit-button');
    
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Disable the card element and submit button to prevent multiple submissions
        card.update({ disabled: true });
        submitButton.disabled = true;
        
        // Show the loading overlay
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'block';
        }
        
        // Get CSRF token for secure request
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Check if save-info checkbox is checked
        let saveInfo = false;
        const saveInfoElement = document.getElementById('id-save-info');
        if (saveInfoElement) {
            saveInfo = saveInfoElement.checked;
        }
        
        // Create the data to post to the cache_checkout_data view
        const postData = new URLSearchParams({
            'csrfmiddlewaretoken': csrfToken,
            'client_secret': clientSecret,
            'save_info': saveInfo
        });
        
        // Post data to the cache_checkout_data endpoint
        fetch('/checkout/cache_checkout_data/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: postData
        })
        .then(function(response) {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response;
        })
        .then(function() {
            // Confirm card payment with Stripe
            stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: card,
                    billing_details: {
                        name: document.getElementById('id_full_name').value.trim(),
                        email: document.getElementById('id_email').value.trim(),
                        phone: document.getElementById('id_phone_number').value.trim(),
                        address: {
                            line1: document.getElementById('id_street_address1').value.trim(),
                            line2: document.getElementById('id_street_address2').value.trim() || '',
                            city: document.getElementById('id_town_or_city').value.trim(),
                            country: document.getElementById('id_country').value.trim(),
                            state: document.getElementById('id_county').value.trim() || ''
                        }
                    }
                },
                shipping: {
                    name: document.getElementById('id_full_name').value.trim(),
                    phone: document.getElementById('id_phone_number').value.trim(),
                    address: {
                        line1: document.getElementById('id_street_address1').value.trim(),
                        line2: document.getElementById('id_street_address2').value.trim() || '',
                        city: document.getElementById('id_town_or_city').value.trim(),
                        country: document.getElementById('id_country').value.trim(),
                        postal_code: document.getElementById('id_postcode').value.trim() || '',
                        state: document.getElementById('id_county').value.trim() || ''
                    }
                }
            }).then(function(result) {
                if (result.error) {
                    // Show error to customer
                    console.error('Payment error:', result.error.message);
                    displayError(result.error.message);
                    enableForm();
                } else {
                    if (result.paymentIntent.status === 'succeeded') {
                        // Submit the form if payment succeeded
                        console.log('Payment succeeded!');
                        form.submit();
                    }
                }
            });
        })
        .catch(function(error) {
            console.error('Error:', error);
            displayError('Sorry, there was an error processing your payment. Please try again.');
            enableForm();
        });
    });
    
    // Helper function to display error messages
    function displayError(message) {
        const errorDiv = document.getElementById('card-errors');
        errorDiv.innerHTML = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${message}</span>
        `;
        
        // Hide loading overlay
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }
    
    // Helper function to re-enable form elements
    function enableForm() {
        card.update({ disabled: false });
        submitButton.disabled = false;
        
        // Hide loading overlay
        const loadingOverlay = document.getElementById('loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.style.display = 'none';
        }
    }
});