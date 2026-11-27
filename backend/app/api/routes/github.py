
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_current_user
from app.db.session import get_db
from app.models.entities import User
from app.schemas.github import (
    GitHubConnectResponse,
    GitHubConnectionStatus,
)
from app.services.github_account_service import (
    save_github_account,
    get_github_account,
    disconnect_github_account,
)
from app.services.github_oauth_service import (
    create_github_oauth_state,
    get_github_oauth_state_user_id,
    build_github_authorization_url,
    exchange_github_code,
    get_github_user,
)


router = APIRouter()


@router.get(
    "/connect",
    response_model=GitHubConnectResponse,
)
def connect_github(
    current_user: User = Depends(get_current_user),
):
    state = create_github_oauth_state(str(current_user.id))

    authorization_url = build_github_authorization_url(state)

    return GitHubConnectResponse(
        authorization_url=authorization_url
    )


@router.get("/callback")
async def github_callback(
    code: str | None = Query(default=None),
    state: str | None = Query(default=None),
    error: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="GitHub authorization was denied.",
        )

    if not code or not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing GitHub authorization code or state.",
        )

    user_id = get_github_oauth_state_user_id(state)

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired GitHub OAuth state.",
        )

    try:
        parsed_user_id = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OAuth user reference.",
        )

    current_user = db.scalar(
        select(User).where(
            User.id == parsed_user_id,
            User.is_active.is_(True),
        )
    )

    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="The account associated with this authorization is unavailable.",
        )

    try:
        access_token = await exchange_github_code(code)
        github_user = await get_github_user(access_token)

        save_github_account(
            db=db,
            user_id=current_user.id,
            github_username=github_user["login"],
            access_token=access_token,
        )

    except (RuntimeError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to complete GitHub account connection.",
        )

    return RedirectResponse(
        url=f"{settings.FRONTEND_URL}/settings/integrations?github=connected",
        status_code=status.HTTP_303_SEE_OTHER,
    )


@router.get(
    "/status",
    response_model=GitHubConnectionStatus,
)
def github_connection_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    account = get_github_account(db, current_user.id)

    if account is None:
        return GitHubConnectionStatus(connected=False)

    return GitHubConnectionStatus(
        connected=True,
        github_username=account.github_username,
    )


@router.delete(
    "/disconnect",
    status_code=status.HTTP_204_NO_CONTENT,
)
def disconnect_github(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    disconnect_github_account(db, current_user.id)
