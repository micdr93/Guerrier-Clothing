document.addEventListener('DOMContentLoaded', function() {
    // Get Stripe public key and client secret from JSON script elements
    var stripePublicKey = document.getElementById('id_stripe_public_key').textContent.trim();
    var clientSecret = document.getElementById('id_client_secret').textContent.trim();

    console.log("🔑 Stripe Public Key:", stripePublicKey);
    console.log("🔑 Client Secret:", clientSecret);

    // Create a Stripe client and Elements instance
    var stripe = Stripe(stripePublicKey);
    var elements = stripe.elements();

    // Custom styling for the card Element
    var style = {
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
            color: '#fa755a',
            iconColor: '#fa755a'
        }
    };

    // Create and mount the card Element
    var card = elements.create('card', { style: style });
    card.mount('#card-element');
    console.log("💳 Card element mounted");

    // Listen for real-time validation errors
    card.addEventListener('change', function(event) {
        var displayError = document.getElementById('card-errors');
        if (event.error) {
            displayError.textContent = event.error.message;
        } else {
            displayError.textContent = '';
        }
    });

    // Handle form submission
    var form = document.getElementById('payment-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();

        var submitButton = document.getElementById('submit-button');
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span> Processing...';

        var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        var postData = {
            'csrfmiddlewaretoken': csrfToken,
            'client_secret': clientSecret,
            'save_info': false // Adjust if you add a save-info checkbox later
        };

        // Cache checkout data before confirming payment
        fetch('/checkout/cache_checkout_data/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: new URLSearchParams(postData)
        }).then(function() {
            // Confirm the card payment
            return stripe.confirmCardPayment(clientSecret, {
                payment_method: {
                    card: card,
                    billing_details: {
                        name: document.getElementById('id_full_name').value,
                        email: document.getElementById('id_email').value,
                        phone: document.getElementById('id_phone_number').value,
                        address: {
                            line1: document.getElementById('id_street_address1').value,
                            line2: document.getElementById('id_street_address2').value,
                            city: document.getElementById('id_town_or_city').value,
                            postal_code: document.getElementById('id_postcode').value,
                            country: document.getElementById('id_country').value
                        }
                    }
                }
            });
        }).then(function(result) {
            if (result.error) {
                // Display error and re-enable submit button
                var errorElement = document.getElementById('card-errors');
                errorElement.textContent = result.error.message;
                submitButton.disabled = false;
                submitButton.innerHTML = 'Complete Order';
            } else {
                // Payment successful; submit the form
                if (result.paymentIntent.status === 'succeeded') {
                    console.log("✅ Payment succeeded, submitting form...");
                    form.submit();
                }
            }
        }).catch(function(error) {
            console.error("Error in payment process:", error);
            submitButton.disabled = false;
            submitButton.innerHTML = 'Complete Order';
        });
    });
});
