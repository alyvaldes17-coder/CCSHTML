"""
User management service
"""
from auth_server.models import User, PlanType
from sqlmodel import Session, select
from auth_server.services.auth_service import hash_password, verify_password

class UserService:
    
    @staticmethod
    def create_user(session: Session, email: str, password: str, plan: PlanType = PlanType.STARTER) -> User:
        """Crear nuevo usuario"""
        user = User(
            email=email,
            hashed_password=hash_password(password),
            plan=plan,
            max_accounts=3  # Default
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_email(session: Session, email: str) -> User | None:
        """Obtener usuario por email"""
        statement = select(User).where(User.email == email)
        return session.exec(statement).first()
    
    @staticmethod
    def get_user_by_id(session: Session, user_id: int) -> User | None:
        """Obtener usuario por ID"""
        return session.get(User, user_id)
    
    @staticmethod
    def authenticate_user(session: Session, email: str, password: str) -> User | None:
        """Autenticar usuario"""
        user = UserService.get_user_by_email(session, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
    
    @staticmethod
    def update_plan(session: Session, user_id: int, new_plan: PlanType) -> User | None:
        """Actualizar plan de usuario"""
        user = UserService.get_user_by_id(session, user_id)
        if not user:
            return None
        
        user.plan = new_plan
        user.max_accounts = user.get_max_accounts()
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    
    @staticmethod
    def list_users(session: Session, skip: int = 0, limit: int = 100) -> list[User]:
        """Listar usuarios"""
        statement = select(User).offset(skip).limit(limit)
        return session.exec(statement).all()
