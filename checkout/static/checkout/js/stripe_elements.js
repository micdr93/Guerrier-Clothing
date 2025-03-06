document.addEventListener('DOMContentLoaded', function() {
    const stripePublicKey = document.getElementById('id_stripe_public_key').textContent.trim();
    const clientSecret = document.getElementById('id_client_secret').textContent.trim();
    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();
    const style = {
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
    const card = elements.create('card', { style: style });
    card.mount('#card-element');
    card.addEventListener('change', function(event) {
        const displayError = document.getElementById('card-errors');
        if (event.error) {
            displayError.textContent = event.error.message;
        } else {
            displayError.textContent = '';
        }
    });
    const form = document.getElementById('payment-form');
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        const submitButton = document.getElementById('submit-button');
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm mr-2" role="status" aria-hidden="true"></span> Processing...';
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const postData = {
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
                const errorElement = document.getElementById('card-errors');
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
