from app.models.user import UserRecord
from app.services.google_sheets import GoogleSheetsRepository
from app.utils.security import hash_password, verify_password


class AuthServiceError(ValueError):
    pass


def normalize_username(username: str) -> str:
    return username.strip().lower()


def validate_credentials(username: str, password: str) -> tuple[str, str]:
    username = normalize_username(username)
    password = password.strip()
    if len(username) < 3:
        raise AuthServiceError("El usuario debe tener al menos 3 caracteres.")
    if len(username) > 30:
        raise AuthServiceError("El usuario no puede superar 30 caracteres.")
    if len(password) < 6:
        raise AuthServiceError("La contraseña debe tener al menos 6 caracteres.")
    return username, password


def register_user(repo: GoogleSheetsRepository, username: str, password: str) -> UserRecord:
    print(f"[DEBUG register_user] START - username: {username}, password_type: {type(password)}, password_len: {len(str(password))}")
    username, password = validate_credentials(username, password)
    print(f"[DEBUG register_user] AFTER VALIDATE - username: {username}, password_len: {len(password)}")
    if repo.get_user(username):
        raise AuthServiceError("Ese usuario ya existe.")

    print(f"[DEBUG register_user] CALLING hash_password with password_len: {len(password)}")
    password_hash = hash_password(password)
    print(f"[DEBUG register_user] GOT hash: {password_hash[:20]}... (len: {len(password_hash)})")
    
    user = UserRecord(
        username=username,
        password_hash=password_hash,
        coins=0,
        happiness=100,
        food=100,
        sleep=100,
        pet_name="Mi Mascota",
    )
    repo.append_user(user)
    print(f"[DEBUG register_user] SUCCESS")
    return user


def authenticate_user(repo: GoogleSheetsRepository, username: str, password: str) -> UserRecord:
    print(f"[DEBUG authenticate_user] START - username: {username}, password_type: {type(password)}, password_len: {len(str(password))}")
    username = normalize_username(username)
    found = repo.get_user(username)
    if not found:
        raise AuthServiceError("Usuario o contraseña incorrectos.")
    _, user = found
    print(f"[DEBUG authenticate_user] FOUND USER - password_hash_type: {type(user.password_hash)}, hash_len: {len(user.password_hash)}")
    print(f"[DEBUG authenticate_user] CALLING verify_password")
    if not verify_password(password, user.password_hash):
        raise AuthServiceError("Usuario o contraseña incorrectos.")
    print(f"[DEBUG authenticate_user] SUCCESS")
    return user
