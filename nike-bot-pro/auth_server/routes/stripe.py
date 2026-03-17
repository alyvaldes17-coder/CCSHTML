from fastapi import APIRouter, Request, HTTPException
from services import handle_payment_success

router = APIRouter(prefix="/webhook", tags=["webhooks"])

@router.post("/stripe")
async def stripe_webhook(request: Request):
    """
    POST /webhook/stripe
    Handle Stripe payment events
    """
    
    try:
        payload = await request.json()
        event_type = payload.get("type")
        
        if event_type == "payment_intent.succeeded":
            result = await handle_payment_success(payload.get("data", {}).get("object", {}))
            if result:
                # TODO: Generar token para usuario
                return {"ok": True, "email": result["email"]}
        
        return {"ok": True}
    
    except Exception as e:
        print(f"ERROR in Stripe webhook: {e}")
        raise HTTPException(status_code=500, detail=str(e))
