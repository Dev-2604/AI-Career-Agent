
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_user
from app.models.entities import User, CandidateProfile
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse,
)
from app.services.auth_service import (
    register_user,
    authenticate_user,
    generate_user_token,
)

router = APIRouter()


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserRegister,
    db: Session = Depends(get_db),
):
    try:
        user, profile = register_user(db, user_data)

        return UserResponse(
            id=user.id,
            full_name=profile.full_name,
            email=user.email,
            is_active=user.is_active,
            is_verified=user.is_verified,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
):
    result = authenticate_user(
        db,
        login_data.email,
        login_data.password,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user, profile = result

    return TokenResponse(
        access_token=generate_user_token(user),
        user=UserResponse(
            id=user.id,
            full_name=profile.full_name,
            email=user.email,
            is_active=user.is_active,
            is_verified=user.is_verified,
        ),
    )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    profile = db.query(CandidateProfile).filter(
        CandidateProfile.user_id == current_user.id
    ).first()

    return UserResponse(
        id=current_user.id,
        full_name=profile.full_name if profile else None,
        email=current_user.email,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
    )
