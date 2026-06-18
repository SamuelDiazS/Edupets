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
    username, password = validate_credentials(username, password)
    if repo.get_user(username):
        raise AuthServiceError("Ese usuario ya existe.")

    user = UserRecord(
        username=username,
        password_hash=hash_password(password),
        coins=0,
        happiness=100,
        food=100,
        sleep=100,
        pet_name="Mi Mascota",
    )
    repo.append_user(user)
    return user


def authenticate_user(repo: GoogleSheetsRepository, username: str, password: str) -> UserRecord:
    username = normalize_username(username)
    found = repo.get_user(username)
    if not found:
        raise AuthServiceError("Usuario o contraseña incorrectos.")
    _, user = found
    if not verify_password(password, user.password_hash):
        raise AuthServiceError("Usuario o contraseña incorrectos.")
    return user
