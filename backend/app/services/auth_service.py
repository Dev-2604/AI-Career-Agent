
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.entities import User, CandidateProfile
from app.schemas.auth import UserRegister
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


def register_user(
    db: Session,
    user_data: UserRegister,
) -> tuple[User, CandidateProfile]:
    email = str(user_data.email).strip().lower()

    existing_user = db.scalar(
        select(User).where(User.email == email)
    )

    if existing_user:
        raise ValueError("An account with this email already exists.")

    user = User(
        email=email,
        password_hash=hash_password(user_data.password),
    )

    try:
        db.add(user)
        db.flush()

        profile = CandidateProfile(
            user_id=user.id,
            full_name=user_data.full_name.strip(),
        )

        db.add(profile)
        db.commit()

        db.refresh(user)
        db.refresh(profile)

        return user, profile

    except IntegrityError:
        db.rollback()
        raise ValueError(
            "An account with this email already exists."
        )


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> tuple[User, CandidateProfile] | None:
    normalized_email = email.strip().lower()

    user = db.scalar(
        select(User).where(User.email == normalized_email)
    )

    if user is None:
        return None

    if not verify_password(password, user.password_hash):
        return None

    if not user.is_active:
        return None

    profile = db.scalar(
        select(CandidateProfile).where(
            CandidateProfile.user_id == user.id
        )
    )

    if profile is None:
        return None

    return user, profile


def generate_user_token(user: User) -> str:
    return create_access_token(str(user.id))
