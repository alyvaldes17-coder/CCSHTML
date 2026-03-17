from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum
from sqlalchemy.orm import declarative_base
from sqlmodel import SQLModel, Field
from datetime import datetime
import enum

Base = declarative_base()

class PlanType(str, enum.Enum):
    STARTER = "starter"
    PRO = "pro"
    ELITE = "elite"

class User(SQLModel, table=True):
    """Usuario del sistema"""
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    plan: PlanType = Field(default=PlanType.STARTER)
    max_accounts: int = Field(default=3)  # Según plan
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    def get_max_accounts(self) -> int:
        """Retorna máximas cuentas según plan"""
        plan_limits = {
            PlanType.STARTER: 3,
            PlanType.PRO: 6,
            PlanType.ELITE: 10
        }
        return plan_limits.get(self.plan, 3)

class Subscription(SQLModel, table=True):
    """Suscripción activa"""
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    plan: PlanType
    token: str = Field(unique=True, index=True)  # JWT token
    hwid: str  # Hardware ID del cliente
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
class StripePayment(SQLModel, table=True):
    """Registro de pagos Stripe"""
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    stripe_id: str = Field(unique=True)
    amount: int  # en centavos
    currency: str
    status: str  # pending, completed, failed
    created_at: datetime = Field(default_factory=datetime.utcnow)
