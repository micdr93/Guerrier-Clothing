/*
    Core logic/payment flow for this comes from here:
    https://stripe.com/docs/payments/accept-a-payment

    CSS from here: 
    https://stripe.com/docs/stripe-js
*/

// Get the Stripe public key and client secret
const stripePublicKey = document.getElementById('id_stripe_public_key').textContent.slice(1, -1);
const clientSecret = document.getElementById('id_client_secret').textContent.slice(1, -1);

// Set up Stripe
const stripe = Stripe(stripePublicKey);
const elements = stripe.elements();

// Custom styling for the card element
const style = {
    base: {
        color: '#000',
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

// Create card element
const card = elements.create('card', {style: style});
card.mount('#card-element');

// Handle validation errors on the card element
card.addEventListener('change', function (event) {
    const errorDiv = document.getElementById('card-errors');
    if (event.error) {
        const html = `
            <span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>
        `;
        errorDiv.innerHTML = html;
    } else {
        errorDiv.textContent = '';
    }
});

// Handle form submission
const form = document.getElementById('payment-form');
form.addEventListener('submit', function(ev) {
    ev.preventDefault();
    // Disable card input and submit button to prevent multiple submissions
    card.update({ 'disabled': true });
    document.getElementById('submit-button').disabled = true;
    
    // Get the save info checkbox value
    const saveInfo = Boolean(document.getElementById('id-save-info')?.checked);
    
    // Create a token for the CSRF
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Create metadata for the payment
    const postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
    };
    
    const url = '/checkout/cache_checkout_data/';
    
    // Post the metadata first, then handle the card payment
    fetch(url, {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: new URLSearchParams(postData)
    }).then(function() {
        // Use Stripe to confirm card payment
        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: form.full_name.value,
                    phone: form.phone_number.value,
                    email: form.email.value,
                    address:{
                        line1: form.street_address1.value,
                        line2: form.street_address2.value,
                        city: form.town_or_city.value,
                        country: form.country.value,
                        state: form.county.value,
                    }
                }
            },
            shipping: {
                name: form.full_name.value,
                phone: form.phone_number.value,
                address: {
                    line1: form.street_address1.value,
                    line2: form.street_address2.value,
                    city: form.town_or_city.value,
                    country: form.country.value,
                    postal_code: form.postcode.value,
                    state: form.county.value,
                }
            },
        }).then(function(result) {
            if (result.error) {
                // Show error and re-enable form
                const errorDiv = document.getElementById('card-errors');
                const html = `
                    <span class="icon" role="alert">
                        <i class="fas fa-times"></i>
                    </span>
                    <span>${result.error.message}</span>
                `;
                errorDiv.innerHTML = html;
                card.update({ 'disabled': false });
                document.getElementById('submit-button').disabled = false;
            } else {
                // Submit the form if payment succeeded
                if (result.paymentIntent.status === 'succeeded') {
                    form.submit();
                }
            }
        });
    }).catch(function() {
        // Reload the page if there's an error
        location.reload();
    });
});§