
from pydantic import BaseModel, HttpUrl


class GitHubConnectResponse(BaseModel):
    authorization_url: HttpUrl


class GitHubConnectionStatus(BaseModel):
    connected: bool
    github_username: str | None = None
    github_user_id: int | None = None
