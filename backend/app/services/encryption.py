from cryptography.fernet import Fernet
from app.config import get_settings


def _get_fernet() -> Fernet:
    settings = get_settings()
    if not settings.ENCRYPTION_KEY:
        raise ValueError(
            "ENCRYPTION_KEY is not configured. Set a persistent Fernet key in the backend environment."
        )
    key = settings.ENCRYPTION_KEY.encode()
    return Fernet(key)


def encrypt_password(plain_password: str) -> str:
    """Encrypt a plaintext password using Fernet (AES-128-CBC)."""
    f = _get_fernet()
    return f.encrypt(plain_password.encode()).decode()


def decrypt_password(encrypted_password: str) -> str:
    """Decrypt a Fernet-encrypted password back to plaintext."""
    f = _get_fernet()
    return f.decrypt(encrypted_password.encode()).decode()
