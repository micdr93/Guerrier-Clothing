// Retrieve the Stripe public key and client secret from the JSON script blocks
const stripePublicKeyElem = document.getElementById('id_stripe_public_key');
const clientSecretElem = document.getElementById('id_client_secret');

// Remove any surrounding quotes from the text content
let stripePublicKey = stripePublicKeyElem.textContent.replace(/"/g, '');
let clientSecret = clientSecretElem.textContent.replace(/"/g, '');

// Initialize Stripe with the public key
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

// Create the card element and mount it in the #card-element div
const card = elements.create('card', { style: style });
card.mount('#card-element');

// Handle real-time validation errors on the card element
card.on('change', function (event) {
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
const loadingOverlay = document.getElementById('loading-overlay');
const submitButton = document.getElementById('submit-button');

form.addEventListener('submit', function(ev) {
  ev.preventDefault();
  
  // Disable the card element and button to prevent duplicate submissions
  card.update({ disabled: true });
  submitButton.disabled = true;
  
  // (Optional) Fade out the form and show the loading overlay
  form.style.opacity = 0.5;
  loadingOverlay.style.display = 'block';
  
  // For test/demo, submit the form after a short delay
  setTimeout(function() {
    form.submit();
  }, 500);
});
