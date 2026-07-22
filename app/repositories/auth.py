import hashlib
import hmac
import secrets

from app.repositories.app_settings import get_setting, set_setting

DEFAULT_PASSWORD = "kolinet"
_SALT_KEY = "password_salt"
_HASH_KEY = "password_hash"
_ITERATIONS = 200_000


def ensure_default_password() -> None:
    if get_setting(_HASH_KEY) is None:
        set_password(DEFAULT_PASSWORD)


def set_password(new_password: str) -> None:
    salt = secrets.token_hex(16)
    set_setting(_SALT_KEY, salt)
    set_setting(_HASH_KEY, _hash_password(new_password, salt))


def verify_password(password: str) -> bool:
    salt = get_setting(_SALT_KEY)
    stored_hash = get_setting(_HASH_KEY)
    if salt is None or stored_hash is None:
        return False
    return hmac.compare_digest(_hash_password(password, salt), stored_hash)


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), bytes.fromhex(salt), _ITERATIONS
    ).hex()
