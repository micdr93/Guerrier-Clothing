document.addEventListener('DOMContentLoaded', function() {
    setTimeout(function() {
      const cardElement = document.getElementById('card-element');
      if (cardElement) {
        // Apply direct styling to ensure visibility
        cardElement.style.border = '1px solid #ced4da';
        cardElement.style.borderRadius = '4px';
        cardElement.style.padding = '12px';
        cardElement.style.backgroundColor = 'white';
        cardElement.style.height = '40px';
        cardElement.style.display = 'flex';
        cardElement.style.alignItems = 'center';
        
        // Check for iframes inside the card element (Stripe creates these)
        const iframes = cardElement.querySelectorAll('iframe');
        if (iframes.length > 0) {
          console.log('Found Stripe iframe, applying styles');
          iframes.forEach(iframe => {
            iframe.style.opacity = '1';
            iframe.style.visibility = 'visible';
            iframe.style.display = 'block';
            iframe.style.width = '100%';
            iframe.style.height = '24px';
          });
        } else {
          console.log('No Stripe iframe found. The Stripe card element might not be properly initialized.');
          
          // If there's no iframe, try to recreate the Stripe element
          try {
            // Get Stripe publishable key
            const stripeKey = document.getElementById('id_stripe_public_key').textContent.trim().replace(/"/g, '');
            if (!stripeKey) {
              console.error('No Stripe public key found');
              return;
            }
            
            // Initialize Stripe again
            const stripe = Stripe(stripeKey);
            const elements = stripe.elements();
            
            // Clear the card element
            cardElement.innerHTML = '';
            
            // Create card with minimal styling
            const card = elements.create('card', {
              style: {
                base: {
                  color: '#32325d',
                  fontFamily: 'Arial, sans-serif',
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
              }
            });
            
            // Mount the card
            card.mount('#card-element');
            console.log('Card element recreated and mounted');
          } catch (e) {
            console.error('Error recreating Stripe card element:', e);
          }
        }
      } else {
        console.error('Card element not found in DOM');
      }
    }, 1000); // Give Stripe a second to initialize first
  });
</script>