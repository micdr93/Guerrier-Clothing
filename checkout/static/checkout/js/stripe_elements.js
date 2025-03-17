document.addEventListener("DOMContentLoaded", function () {
    // Retrieve and parse the JSON data for the public key and client secret.
    var stripePublicKey = JSON.parse(document.getElementById("id_stripe_public_key").textContent);
    var clientSecret = JSON.parse(document.getElementById("id_client_secret").textContent);

    var stripe = Stripe(stripePublicKey);
    var elements = stripe.elements();

    var card = elements.create("card", {
        style: {
            base: {
                color: "#000",
                fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
                fontSmoothing: "antialiased",
                fontSize: "16px",
                "::placeholder": {
                    color: "#aab7c4",
                },
            },
            invalid: {
                color: "#dc3545",
                iconColor: "#dc3545",
            },
        },
    });

    card.mount("#card-element");

    card.addEventListener("change", function (event) {
        var errorDiv = document.getElementById("card-errors");
        if (event.error) {
            errorDiv.innerHTML = `<span class="icon" role="alert">
                <i class="fas fa-times"></i>
            </span>
            <span>${event.error.message}</span>`;
        } else {
            errorDiv.textContent = "";
        }
    });

    var form = document.getElementById("payment-form");
    form.addEventListener("submit", function (ev) {
        ev.preventDefault();

        card.update({ disabled: true });
        document.getElementById("submit-button").disabled = true;
        document.getElementById("payment-form").style.opacity = "0.5";

        stripe.confirmCardPayment(clientSecret, {
            payment_method: {
                card: card,
                billing_details: {
                    name: form.full_name.value.trim(),
                    email: form.email.value.trim(),
                    phone: form.phone_number.value.trim(),
                    address: {
                        line1: form.street_address1.value.trim(),
                        line2: form.street_address2.value.trim(),
                        city: form.town_or_city.value.trim(),
                        country: form.country.value.trim(),
                        postal_code: form.postcode.value.trim(),
                        state: form.county.value.trim(),
                    },
                },
            },
        })
        .then(function (result) {
            if (result.error) {
                var errorDiv = document.getElementById("card-errors");
                errorDiv.innerHTML = `<span class="icon" role="alert">
                    <i class="fas fa-times"></i>
                </span>
                <span>${result.error.message}</span>`;
                card.update({ disabled: false });
                document.getElementById("submit-button").disabled = false;
                document.getElementById("payment-form").style.opacity = "1";
            } else {
                if (result.paymentIntent.status === "succeeded") {
                    form.submit();
                }
            }
        });
    });
});
