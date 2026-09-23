from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..schemas import UserCreate, UserLogin, Token, UserResponse
from ..crud import create_user, authenticate_user
from ..security import create_access_token
from ..dependencies import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/")
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    return create_user(db=db, user=user)

@router.post("/login", response_model=Token)
def login_user(user: UserLogin, db: Session = Depends(get_db)):
    authenticated_user = authenticate_user(db=db, email=user.email, password=user.password)

    if not authenticated_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )

    access_token = create_access_token(authenticated_user.id)

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user = Depends(get_current_user)
):
    return current_user