from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    name = "checkout"

    def ready(self):
        # Import signals
        try:
            import checkout.signals

            print("✅ Checkout signals loaded successfully")
        except ModuleNotFoundError:
            print("⚠️ checkout.signals module not found - skipping")

        # Don't set Stripe API key here - it will be set in the views
        print("🔄 Checkout app initialized - Stripe key will be set in views")
