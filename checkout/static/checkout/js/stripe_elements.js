document.addEventListener('DOMContentLoaded', function() {
  // Get Stripe publishable key from the JSON script tag
  const rawPublicKey = document.getElementById('id_stripe_public_key').textContent.trim();
  let stripePublicKey;
  try {
      stripePublicKey = JSON.parse(rawPublicKey);
  } catch (e) {
      stripePublicKey = rawPublicKey;
  }

  // Get client secret from the JSON script tag
  const rawClientSecret = document.getElementById('id_client_secret').textContent.trim();
  let clientSecret;
  try {
      clientSecret = JSON.parse(rawClientSecret);
  } catch (e) {
      clientSecret = rawClientSecret;
  }
  // Ensure any extra surrounding quotes are removed
  if (clientSecret.startsWith('"') && clientSecret.endsWith('"')) {
      clientSecret = clientSecret.substring(1, clientSecret.length - 1);
  }
  
  // Validate that we have the required keys
  if (!stripePublicKey) {
      console.error('Missing Stripe public key');
      displayError('Configuration error with payment system. Please contact support.');
      return;
  }
  if (!clientSecret) {
      console.error('Missing client_secret');
      displayError('Configuration error with payment system. Please contact support.');
      return;
  }

  // Initialize Stripe with the public key
  const stripe = Stripe(stripePublicKey);
  const elements = stripe.elements();

  // Define styling for the card element
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
      hidePostalCode: true
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

      // Disable elements to prevent multiple submissions
      card.update({ disabled: true });
      submitButton.disabled = true;

      // Show loading state
      const loadingElement = document.getElementById('loading-overlay');
      if (loadingElement) {
          loadingElement.style.display = 'block';
      }

      // Get CSRF token
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

      // Build a URL-encoded string from postData
      const postBody = new URLSearchParams();
      Object.keys(postData).forEach(key => {
          postBody.append(key, postData[key]);
      });

      // Send data to the server
      fetch(url, {
          method: 'POST',
          headers: {
              'Content-Type': 'application/x-www-form-urlencoded'
          },
          body: postBody
      })
      .then(function(response) {
          if (!response.ok) {
              throw new Error('Network response was not ok');
          }
          return response;
      })
      .then(function() {
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
                  displayError(result.error.message);
                  enableForm();
              } else {
                  if (result.paymentIntent.status === 'succeeded') {
                      form.submit();
                  }
              }
          });
      })
      .catch(function(error) {
          console.error('Error:', error);
          displayError('Sorry, there was an error processing your payment. Please try again.');
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
      const loadingElement = document.getElementById('loading-overlay');
      if (loadingElement) {
          loadingElement.style.display = 'none';
      }
  }

  // Helper function to re-enable form elements
  function enableForm() {
      card.update({ disabled: false });
      submitButton.disabled = false;
      const loadingElement = document.getElementById('loading-overlay');
      if (loadingElement) {
          loadingElement.style.display = 'none';
      }
  }
});
