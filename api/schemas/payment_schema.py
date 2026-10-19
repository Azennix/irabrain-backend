from pydantic import BaseModel


class PaymentVerificationRequest(BaseModel):
    payment_id: int
    provider_payment_id: str
    signature: str