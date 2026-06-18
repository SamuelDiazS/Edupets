from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext


password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    # Truncate password to 72 bytes if necessary (bcrypt limit)
    print(f"[DEBUG hash_password] INPUT - type: {type(password)}, len: {len(password)}, len_bytes: {len(password.encode('utf-8'))}")
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password = password_bytes[:72].decode('utf-8', errors='ignore')
        print(f"[DEBUG hash_password] TRUNCATED - len: {len(password)}, len_bytes: {len(password.encode('utf-8'))}")
    try:
        hashed = password_context.hash(password)
        print(f"[DEBUG hash_password] SUCCESS - hash_len: {len(hashed)}")
        return hashed
    except Exception as e:
        print(f"[DEBUG hash_password] ERROR - {type(e).__name__}: {str(e)}")
        raise


def verify_password(plain_password: str, password_hash: str) -> bool:
    # Truncate password to 72 bytes if necessary (bcrypt limit)
    print(f"[DEBUG verify_password] INPUT - password_type: {type(plain_password)}, password_len: {len(plain_password)}, password_bytes: {len(plain_password.encode('utf-8'))}")
    print(f"[DEBUG verify_password] INPUT - hash_type: {type(password_hash)}, hash_len: {len(password_hash)}")
    password_bytes = plain_password.encode('utf-8')
    if len(password_bytes) > 72:
        plain_password = password_bytes[:72].decode('utf-8', errors='ignore')
        print(f"[DEBUG verify_password] TRUNCATED - password_len: {len(plain_password)}, password_bytes: {len(plain_password.encode('utf-8'))}")
    try:
        result = password_context.verify(plain_password, password_hash)
        print(f"[DEBUG verify_password] SUCCESS - result: {result}")
        return result
    except Exception as e:
        print(f"[DEBUG verify_password] ERROR - {type(e).__name__}: {str(e)}")
        raise


def create_access_token(
    subject: str,
    secret_key: str,
    algorithm: str,
    expires_minutes: int,
) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=expires_minutes)
    payload = {"sub": subject, "exp": expires_at}
    return jwt.encode(payload, secret_key, algorithm=algorithm)


def decode_access_token(token: str, secret_key: str, algorithm: str) -> dict[str, Any] | None:
    try:
        return jwt.decode(token, secret_key, algorithms=[algorithm])
    except JWTError:
        return None
