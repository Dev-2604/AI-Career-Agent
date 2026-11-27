
from datetime import datetime, timedelta, timezone
import secrets
from urllib.parse import urlencode

import httpx
import jwt

from app.core.config import settings


OAUTH_STATE_EXPIRE_MINUTES = 10
GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"


def create_github_oauth_state(user_id: str) -> str:
    now = datetime.now(timezone.utc)

    payload = {
        "sub": user_id,
        "purpose": "github_oauth",
        "nonce": secrets.token_urlsafe(32),
        "iat": now,
        "exp": now + timedelta(
            minutes=OAUTH_STATE_EXPIRE_MINUTES
        ),
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm="HS256",
    )


def get_github_oauth_state_user_id(state: str) -> str | None:
    """Extract the user ID from a valid GitHub OAuth state."""

    try:
        payload = jwt.decode(
            state,
            settings.SECRET_KEY,
            algorithms=["HS256"],
        )

        if (
            payload.get("purpose") != "github_oauth"
            or not payload.get("nonce")
        ):
            return None

        return payload.get("sub")

    except jwt.InvalidTokenError:
        return None


def verify_github_oauth_state(
    state: str,
    expected_user_id: str,
) -> bool:
    return (
        get_github_oauth_state_user_id(state)
        == expected_user_id
    )


def build_github_authorization_url(state: str) -> str:
    if not settings.GITHUB_CLIENT_ID:
        raise RuntimeError(
            "GitHub Client ID is not configured."
        )

    params = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
        "state": state,
    }

    return f"{GITHUB_AUTHORIZE_URL}?{urlencode(params)}"


async def exchange_github_code(
    code: str,
) -> str:
    if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
        raise RuntimeError(
            "GitHub OAuth credentials are not configured."
        )

    payload = {
        "client_id": settings.GITHUB_CLIENT_ID,
        "client_secret": settings.GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": settings.GITHUB_REDIRECT_URI,
    }

    headers = {
        "Accept": "application/json",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.post(
            GITHUB_TOKEN_URL,
            data=payload,
            headers=headers,
        )

    if response.status_code != 200:
        raise RuntimeError(
            "GitHub token exchange failed."
        )

    data = response.json()

    access_token = data.get("access_token")

    if not access_token:
        raise RuntimeError(
            "GitHub did not return an access token."
        )

    return access_token


async def get_github_user(
    access_token: str,
) -> dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            GITHUB_USER_URL,
            headers=headers,
        )

    if response.status_code != 200:
        raise RuntimeError(
            "Unable to retrieve GitHub user profile."
        )

    user_data = response.json()

    if not user_data.get("id") or not user_data.get("login"):
        raise RuntimeError(
            "GitHub returned an incomplete user profile."
        )

    return user_data
