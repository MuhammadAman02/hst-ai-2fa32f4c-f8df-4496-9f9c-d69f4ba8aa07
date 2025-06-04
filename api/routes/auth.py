from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from core.database import get_db
from services.auth import authenticate_user, create_user, login_for_access_token
from models.schemas import UserCreate, UserResponse, Token

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Login endpoint"""
    return login_for_access_token(db, form_data.username, form_data.password)

@router.post("/register", response_model=UserResponse)
async def register(
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    full_name: str = Form(None),
    db: Session = Depends(get_db)
):
    """Registration endpoint"""
    user_data = UserCreate(
        email=email,
        username=username,
        password=password,
        full_name=full_name
    )
    return create_user(db, user_data)