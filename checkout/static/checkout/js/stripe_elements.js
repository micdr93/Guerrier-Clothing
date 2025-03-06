document.addEventListener('DOMContentLoaded', function() {
    var stripePublicKey = stripePublicKey || document.getElementById("stripe-public-key").textContent.trim();
    var clientSecret = clientSecret || document.getElementById("client-secret-data").textContent.trim();
    var stripe = Stripe(stripePublicKey);
    var elements = stripe.elements();
    var style = {
        base: {
            color: '#32325d',
            fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
            fontSmoothing: 'antialiased',
            fontSize: '16px',
            '::placeholder': { color: '#aab7c4' }
        },
        invalid: {
            color: '#fa755a',
            iconColor: '#fa755a'
        }
    };
    var card = elements.create('card', { style: style });
    card.mount('#card-element');
    card.addEventListener('change', function(event) {
        var displayError = document.getElementById('card-errors');
        if (event.error) {
            displayError.textContent = event.error.message;
        } else {
            displayError.textContent = '';
        }
    });
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
            'save_info': document.getElementById('id-save-info').checked ? 'true' : 'false'
        };
        fetch('/checkout/cache_checkout_data/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: new URLSearchParams(postData)
        }).then(function() {
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
                var errorElement = document.getElementById('card-errors');
                errorElement.textContent = result.error.message;
                submitButton.disabled = false;
                submitButton.innerHTML = 'Complete Order';
            } else {
                if (result.paymentIntent.status === 'succeeded') {
                    form.submit();
                }
            }
        }).catch(function(error) {
            submitButton.disabled = false;
            submitButton.innerHTML = 'Complete Order';
        });
    });
});
