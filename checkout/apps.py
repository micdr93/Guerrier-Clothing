from django.apps import AppConfig


class CheckoutConfig(AppConfig):
    name = "checkout"

    def ready(self):

        try:
            import checkout.signals

            print("✅ Checkout signals loaded successfully")
        except ModuleNotFoundError:
            print("⚠️ checkout.signals module not found - skipping")

        print("🔄 Checkout app initialized - Stripe key will be set in views")
