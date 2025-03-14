window.addEventListener('load', function() {
    console.log("Stripe elements script loaded");
    var keyElem = document.getElementById('id_stripe_public_key');
    var clientSecretElem = document.getElementById('id_client_secret');
    if (!keyElem) { console.error("Stripe key element not found"); return; }
    if (!clientSecretElem) { console.error("Client secret element not found"); return; }
    var stripePublicKey = keyElem.textContent.trim().replace(/"/g, '');
    var clientSecret = clientSecretElem.textContent.trim().replace(/"/g, '');
    console.log("Stripe public key:", stripePublicKey);
    console.log("Client secret:", clientSecret);
    if (!stripePublicKey || !clientSecret) { console.error('Missing Stripe key or client secret'); return; }
    var stripe = Stripe(stripePublicKey);
    var elements = stripe.elements();
    var card = elements.create('card', {
      style: {
        base: {
          color: '#333',
          fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
          fontSmoothing: 'antialiased',
          fontSize: '16px',
          '::placeholder': { color: '#aab7c4' },
          iconColor: '#666'
        },
        invalid: { color: '#dc3545', iconColor: '#dc3545' }
      },
      hidePostalCode: true
    });
    card.mount('#card-element');
    console.log("Card element mounted");
    card.addEventListener('change', function(e) {
      var errorDiv = document.getElementById('card-errors');
      if (e.error) {
        errorDiv.innerHTML = '<span class="icon" role="alert"><i class="fas fa-times"></i></span><span>' + e.error.message + '</span>';
      } else {
        errorDiv.innerHTML = '';
      }
    });
    var form = document.getElementById('payment-form');
    form.addEventListener('submit', function(e) {
      e.preventDefault();
      card.update({ disabled: true });
      document.getElementById('submit-button').disabled = true;
      document.getElementById('loading-overlay').style.display = 'block';
      stripe.confirmCardPayment(clientSecret, {
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
              country: document.getElementById('id_country').value,
              state: document.getElementById('id_county').value,
              postal_code: document.getElementById('id_postcode').value
            }
          }
        },
        shipping: {
          name: document.getElementById('id_full_name').value,
          phone: document.getElementById('id_phone_number').value,
          address: {
            line1: document.getElementById('id_street_address1').value,
            line2: document.getElementById('id_street_address2').value,
            city: document.getElementById('id_town_or_city').value,
            country: document.getElementById('id_country').value,
            state: document.getElementById('id_county').value,
            postal_code: document.getElementById('id_postcode').value
          }
        }
      }).then(function(result) {
        if (result.error) {
          var errorDiv = document.getElementById('card-errors');
          errorDiv.innerHTML = '<span class="icon" role="alert"><i class="fas fa-times"></i></span><span>' + result.error.message + '</span>';
          card.update({ disabled: false });
          document.getElementById('submit-button').disabled = false;
          document.getElementById('loading-overlay').style.display = 'none';
        } else {
          if (result.paymentIntent.status === 'succeeded') {
            form.submit();
          }
        }
      });
    });
  });
  