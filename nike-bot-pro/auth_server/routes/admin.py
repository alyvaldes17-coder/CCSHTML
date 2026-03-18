from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from models import User, PlanType
from schemas import UserResponse, UpdatePlanRequest
from services import UserService
from database import get_session

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users", response_model=list[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    session: Session = Depends(get_session)
):
    """
    GET /admin/users
    Listar todos los usuarios
    """
    users = UserService.list_users(session, skip=skip, limit=limit)
    return users

@router.put("/plan/{user_id}", response_model=UserResponse)
async def update_plan(
    user_id: int,
    request: UpdatePlanRequest,
    session: Session = Depends(get_session)
):
    """
    PUT /admin/plan/{user_id}
    {"plan": "pro"}
    Actualizar plan de usuario
    """
    
    # Validar plan
    try:
        plan = PlanType(request.plan.lower())
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid plan")
    
    # Actualizar
    user = UserService.update_plan(session, user_id, plan)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserResponse(
        id=user.id,
        email=user.email,
        plan=user.plan.value,
        max_accounts=user.max_accounts,
        is_active=user.is_active,
        created_at=user.created_at
    )
