document.addEventListener('DOMContentLoaded', function() {
    console.log("stripe_elements.js loaded");

    // Read the public key and client secret from JSON script tags
    const stripePublicKey = JSON.parse(
        document.getElementById("id_stripe_public_key").textContent
    );
    const clientSecret = JSON.parse(
        document.getElementById("id_client_secret").textContent
    );

    const stripe = Stripe(stripePublicKey);
    const elements = stripe.elements();

    const style = {
        base: {
            color: '#32325d',
            fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
            fontSize: '16px',
            '::placeholder': { color: '#aab7c4' }
        },
        invalid: {
            color: '#fa755a'
        }
    };

    const card = elements.create('card', { style });
    card.mount('#card-element');

    card.addEventListener('change', function(event) {
        const errorDiv = document.getElementById('card-errors');
        if (event.error) {
            errorDiv.textContent = event.error.message;
        } else {
            errorDiv.textContent = '';
        }
    });

    const form = document.getElementById('payment-form');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const submitButton = document.getElementById('submit-button');
        submitButton.disabled = true;
        submitButton.innerHTML = 'Processing...';

        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        const saveInfo = document.getElementById('id-save-info').checked ? 'true' : 'false';

        // Step 1: Cache checkout data
        const postData = {
            csrfmiddlewaretoken: csrfToken,
            client_secret: clientSecret,
            save_info: saveInfo
        };

        fetch('/checkout/cache_checkout_data/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: new URLSearchParams(postData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Cache checkout data failed');
            }
            // Step 2: Confirm card payment
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
        })
        .then(result => {
            if (result.error) {
                const errorDiv = document.getElementById('card-errors');
                errorDiv.textContent = result.error.message;
                submitButton.disabled = false;
                submitButton.innerHTML = 'Complete Order';
            } else {
                if (result.paymentIntent.status === 'succeeded') {
                    form.submit();
                }
            }
        })
        .catch(error => {
            console.error("Error:", error);
            submitButton.disabled = false;
            submitButton.innerHTML = 'Complete Order';
        });
    });
});
