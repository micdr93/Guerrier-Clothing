// Get Stripe public key and client secret
var stripePublicKey = document.getElementById('id_stripe_public_key').textContent.trim();
var clientSecret = document.getElementById('id_client_secret').textContent.trim();

console.log("🔑 Stripe Public Key:", stripePublicKey);
console.log("🔑 Client Secret:", clientSecret);

// Create a Stripe client
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

// Create an instance of the card Element
var card = elements.create('card', {style: style});

// Add an instance of the card Element into the `card-element` div
card.mount('#card-element');
console.log("💳 Card element mounted");

// Handle real-time validation errors from the card Element
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
    
    // Disable the submit button to prevent repeated clicks
    document.getElementById('submit-button').disabled = true;
    
    // Cache checkout data before confirming payment
    var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    var postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': false, // No save-info checkbox in your form
    };
    
    // Optional caching of checkout data
    fetch('/checkout/cache_checkout_data/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: new URLSearchParams(postData)
    }).then(function() {
        // Confirm card payment
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
            // Show error to customer
            var errorElement = document.getElementById('card-errors');
            errorElement.textContent = result.error.message;
            document.getElementById('submit-button').disabled = false;
        } else {
            // The payment processed successfully
            if (result.paymentIntent.status === 'succeeded') {
                console.log("✅ Payment succeeded, submitting form...");
                form.submit();
            }
        }
    }).catch(function(error) {
        console.error("Error in payment process:", error);
        document.getElementById('submit-button').disabled = false;
    });
});