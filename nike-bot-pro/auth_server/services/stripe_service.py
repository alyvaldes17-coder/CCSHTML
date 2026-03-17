"""
Stripe payment service
Handles Stripe/MercadoPago webhook events
"""
import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET_KEY", "pk_test_xxx")

async def handle_payment_success(payload: dict) -> dict:
    """
    Handle successful payment from Stripe webhook
    payload: Stripe event object
    """
    try:
        # Extract metadata
        intent_id = payload.get("id")
        metadata = payload.get("metadata", {})
        email = metadata.get("email")
        plan = metadata.get("plan")
        amount = payload.get("amount")  # cents
        
        return {
            "email": email,
            "plan": plan,
            "amount": amount,
            "stripe_id": intent_id
        }
    except Exception as e:
        print(f"ERROR processing Stripe event: {e}")
        return None

async def create_payment_intent(email: str, plan: str, amount: int) -> str:
    """
    Create Stripe payment intent
    amount: in cents (e.g., 1500 = $15.00)
    """
    try:
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency="clp",
            metadata={
                "email": email,
                "plan": plan
            }
        )
        return intent["client_secret"]
    except Exception as e:
        print(f"ERROR creating payment intent: {e}")
        return None
