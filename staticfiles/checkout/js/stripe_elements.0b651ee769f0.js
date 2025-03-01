var stripePublicKey = document.getElementById('id_stripe_public_key').textContent.trim();
var clientSecret = document.getElementById('id_client_secret').textContent.trim();
console.log("🔑 Stripe Public Key:", stripePublicKey);
console.log("🔑 Client Secret:", clientSecret);

var stripe = Stripe(stripePublicKey);
var elements = stripe.elements();

var style = {
    base: {
        color: '#000',
        fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
        fontSmoothing: 'antialiased',
        fontSize: '16px',
        '::placeholder': { color: '#aab7c4' }
    },
    invalid: { color: '#dc3545', iconColor: '#dc3545' }
};

var card = elements.create('card', {style: style});
card.mount('#card-element');

card.addEventListener('change', function (event) {
    var errorDiv = document.getElementById('card-errors');
    errorDiv.innerHTML = event.error ? `<span class="icon"><i class="fas fa-times"></i></span> <span>${event.error.message}</span>` : '';
});

var form = document.getElementById('payment-form');
form.addEventListener('submit', function(ev) {
    ev.preventDefault();
    card.update({ 'disabled': true });
    document.getElementById('submit-button').disabled = true;

    var saveInfo = Boolean(document.getElementById('id-save-info').checked);
    var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    var postData = {
        'csrfmiddlewaretoken': csrfToken,
        'client_secret': clientSecret,
        'save_info': saveInfo,
    };

    fetch('/checkout/cache_checkout_data/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: new URLSearchParams(postData),
    }).then(function(response) {
        return response.json();
    }).then(function(data) {
        console.log("✅ Checkout Data Cached Successfully:", data);
        
        return stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: form.full_name.value,
                    phone: form.phone_number.value,
                    email: form.email.value,
                    address: {
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
        });
    }).then(function(result) {
        if (result.error) {
            var errorDiv = document.getElementById('card-errors');
            errorDiv.innerHTML = `<span class="icon"><i class="fas fa-times"></i></span> <span>${result.error.message}</span>`;
            card.update({ 'disabled': false });
            document.getElementById('submit-button').disabled = false;
        } else if (result.paymentIntent && result.paymentIntent.status === 'succeeded') {
            console.log("✅ Payment succeeded, submitting form...");
            form.submit();
        }
    }).catch(function(error) {
        console.error("❌ Error Processing Payment:", error);
    });
});
