
from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


def get_fernet() -> Fernet:
    key = settings.GITHUB_TOKEN_ENCRYPTION_KEY

    if not key:
        raise RuntimeError(
            "GitHub token encryption key is not configured."
        )

    return Fernet(key.encode())


def encrypt_github_token(access_token: str) -> str:
    if not access_token:
        raise ValueError("Access token cannot be empty.")

    encrypted_token = get_fernet().encrypt(
        access_token.encode()
    )

    return encrypted_token.decode()


def decrypt_github_token(encrypted_token: str) -> str:
    if not encrypted_token:
        raise ValueError("Encrypted token cannot be empty.")

    try:
        decrypted_token = get_fernet().decrypt(
            encrypted_token.encode()
        )
        return decrypted_token.decode()

    except InvalidToken as exc:
        raise ValueError(
            "Unable to decrypt GitHub access token."
        ) from exc
