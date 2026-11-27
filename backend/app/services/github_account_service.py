
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.entities import GitHubAccount
from app.services.github_token_service import encrypt_github_token


def save_github_account(
    db: Session,
    user_id,
    github_username: str,
    access_token: str,
) -> GitHubAccount:
    """Create or update the GitHub account for a user."""

    account = db.scalar(
        select(GitHubAccount).where(
            GitHubAccount.user_id == user_id
        )
    )

    encrypted_token = encrypt_github_token(access_token)

    if account is None:
        account = GitHubAccount(
            user_id=user_id,
            github_username=github_username,
            access_token_encrypted=encrypted_token,
        )
        db.add(account)
    else:
        account.github_username = github_username
        account.access_token_encrypted = encrypted_token

    try:
        db.commit()
        db.refresh(account)
        return account

    except IntegrityError:
        db.rollback()
        raise ValueError(
            "Unable to save GitHub account connection."
        )


def get_github_account(
    db: Session,
    user_id,
) -> GitHubAccount | None:
    return db.scalar(
        select(GitHubAccount).where(
            GitHubAccount.user_id == user_id
        )
    )


def disconnect_github_account(
    db: Session,
    user_id,
) -> bool:
    account = get_github_account(db, user_id)

    if account is None:
        return False

    db.delete(account)
    db.commit()

    return True
