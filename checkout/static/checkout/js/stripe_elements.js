/**
 * Stripe Elements Integration
 * A clean, maintainable implementation for handling Stripe payments
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get Stripe publishable key and client secret from the DOM
    const stripePublicKey = document.getElementById('id_stripe_public_key').textContent.trim().replace(/"/g, '');
    const clientSecret = document.getElementById('id_client_secret').textContent.trim().replace(/"/g, '');
    
    // Validate that we have the required keys
    if (!stripePublicKey) {
        console.error('Missing Stripe public key');
        displayError('Configuration error with payment system. Please contact support.');
        return;
    }
    
    // Initialize Stripe with the public key
    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();
    
    // Define clean, simple styling for the card element
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
    
    // Create and mount the card element
    const card = elements.create('card', {
        style: style,
        hidePostalCode: true // We collect this separately in the form
    });
    
    card.mount('#card-element');
    
    // Handle validation errors on the card element
    card.addEventListener('change', function(event) {
        const errorElement = document.getElementById('card-errors');
        
        if (event.error) {
            const errorMessage = `
                <span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                </span>
                <span>${event.error.message}</span>
            `;
            errorElement.innerHTML = errorMessage;
        } else {
            errorElement.textContent = '';
        }
    });
    
    // Handle form submission
    const form = document.getElementById('payment-form');
    const submitButton = document.getElementById('submit-button');
    
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Disable the submit button and card element to prevent multiple submissions
        card.update({ disabled: true });
        submitButton.disabled = true;
        
        // Show loading state
        const loadingElement = document.getElementById('loading-overlay');
        if (loadingElement) {
            loadingElement.style.display = 'block';
        }
        
        // Get CSRF token for Django
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        
        // Get save-info value if the checkbox exists
        let saveInfo = false;
        const saveInfoElement = document.getElementById('id-save-info');
        if (saveInfoElement) {
            saveInfo = saveInfoElement.checked;
        }
        
        // Post data to the cache_checkout_data view
        const url = '/checkout/cache_checkout_data/';
        const postData = {
            'csrfmiddlewaretoken': csrfToken,
            'client_secret': clientSecret,
            'save_info': saveInfo
        };
        
        // Create a URL-encoded string from the post data
        const postBody = new URLSearchParams();
        Object.keys(postData).forEach(key => {
            postBody.append(key, postData[key]);
        });
        
        // Send the data to the server
        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: postBody
        }).then(function(response) {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response;
        }).then(function() {
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
                            line2: document.getElementById('id_street_address2').value.trim(),
                            city: document.getElementById('id_town_or_city').value.trim(),
                            country: document.getElementById('id_country').value.trim(),
                            state: document.getElementById('id_county').value.trim(),
                        }
                    }
                },
                shipping: {
                    name: document.getElementById('id_full_name').value.trim(),
                    phone: document.getElementById('id_phone_number').value.trim(),
                    address: {
                        line1: document.getElementById('id_street_address1').value.trim(),
                        line2: document.getElementById('id_street_address2').value.trim(),
                        city: document.getElementById('id_town_or_city').value.trim(),
                        country: document.getElementById('id_country').value.trim(),
                        postal_code: document.getElementById('id_postcode').value.trim(),
                        state: document.getElementById('id_county').value.trim(),
                    }
                }
            }).then(function(result) {
                if (result.error) {
                    // Show error in the card-errors div
                    displayError(result.error.message);
                    
                    // Re-enable the form elements
                    enableForm();
                } else {
                    // Payment succeeded, submit the form
                    if (result.paymentIntent.status === 'succeeded') {
                        form.submit();
                    }
                }
            });
        }).catch(function(error) {
            // Log the error and display a generic error message
            console.error('Error:', error);
            displayError('Sorry, there was an error processing your payment. Please try again.');
            
            // Re-enable the form elements
            enableForm();
        });
    });
    
    // Helper function to display error messages
    function displayError(message) {
        const errorElement = document.getElementById('card-errors');
        const errorMessage = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${message}</span>
        `;
        errorElement.innerHTML = errorMessage;
        
        // Hide loading overlay if it exists
        const loadingElement = document.getElementById('loading-overlay');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }
    
    // Helper function to re-enable form elements
    function enableForm() {
        card.update({ disabled: false });
        submitButton.disabled = false;
        
        // Hide loading overlay if it exists
        const loadingElement = document.getElementById('loading-overlay');
        if (loadingElement) {
            loadingElement.style.display = 'none';
        }
    }
});