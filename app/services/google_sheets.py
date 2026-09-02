import json
import logging
import threading
import time
from contextvars import ContextVar
from typing import Any

from app.config import Settings
from app.models.user import UserRecord


logger = logging.getLogger(__name__)
request_endpoint: ContextVar[str] = ContextVar("google_sheets_endpoint", default="unknown")


SHEET_HEADER = [
    "Usuario",
    "Contraseña",
    "Monedas",
    "Felicidad",
    "Comida",
    "Sueño",
    "Nombre",
    "Progreso",
    "Tareas",
]


class GoogleSheetsError(RuntimeError):
    """Raised when Google Sheets cannot be reached or configured."""

    def __init__(self, message: str, *, transient: bool = False, status: int | None = None):
        super().__init__(message)
        self.transient = transient
        self.status = status


class GoogleSheetsRepository:
    _MAX_ATTEMPTS = 3
    _RETRYABLE_STATUSES = {429, 500, 502, 503, 504}

    def __init__(self, settings: Settings):
        self.settings = settings
        self._service: Any | None = None
        self._service_lock = threading.RLock()

    @property
    def service(self) -> Any:
        with self._service_lock:
            if self._service is None:
                if not self.settings.GOOGLE_SHEET_ID.strip() or not self.settings.GOOGLE_SHEET_NAME.strip():
                    raise GoogleSheetsError("GOOGLE_SHEET_ID y GOOGLE_SHEET_NAME son obligatorios.")
                try:
                    from google.oauth2 import service_account
                    from googleapiclient.discovery import build
                except ImportError as exc:
                    raise GoogleSheetsError(
                        "Faltan dependencias de Google Sheets. Ejecuta `pip install -r requirements.txt`."
                    ) from exc

                credentials_payload = self._credentials_payload()
                try:
                    if isinstance(credentials_payload, dict):
                        credentials = service_account.Credentials.from_service_account_info(
                            credentials_payload,
                            scopes=self.settings.google_scopes,
                        )
                    else:
                        credentials = service_account.Credentials.from_service_account_file(
                            credentials_payload,
                            scopes=self.settings.google_scopes,
                        )
                    self._service = build("sheets", "v4", credentials=credentials, cache_discovery=False)
                except (ValueError, OSError, TypeError) as exc:
                    logger.error("Google Sheets permanent configuration error type=%s", type(exc).__name__)
                    raise GoogleSheetsError(
                        "La configuración de credenciales de Google Sheets no es válida."
                    ) from exc
                logger.info("Cliente de Google Sheets inicializado para la hoja configurada")
            return self._service

    def _credentials_payload(self) -> dict[str, Any] | str:
        if self.settings.GOOGLE_SERVICE_ACCOUNT_INFO:
            try:
                payload = json.loads(self.settings.GOOGLE_SERVICE_ACCOUNT_INFO)
            except json.JSONDecodeError as exc:
                logger.error("Google Sheets permanent configuration error type=JSONDecodeError")
                raise GoogleSheetsError("GOOGLE_SERVICE_ACCOUNT_INFO no contiene JSON valido.") from exc
            if not isinstance(payload, dict):
                raise GoogleSheetsError("GOOGLE_SERVICE_ACCOUNT_INFO debe contener un objeto JSON.")
            return payload
        if self.settings.GOOGLE_SERVICE_ACCOUNT_FILE:
            return self.settings.GOOGLE_SERVICE_ACCOUNT_FILE
        raise GoogleSheetsError(
            "Configura GOOGLE_SERVICE_ACCOUNT_FILE o GOOGLE_SERVICE_ACCOUNT_INFO para usar Google Sheets."
        )

    @property
    def sheet_name(self) -> str:
        return self.settings.GOOGLE_SHEET_NAME.replace("'", "''")

    def _range(self, a1_range: str) -> str:
        return f"'{self.sheet_name}'!{a1_range}"

    @staticmethod
    def _error_details(exc: Exception) -> tuple[int | None, str]:
        response = getattr(exc, "resp", None)
        status = getattr(response, "status", None)
        reason = ""
        content = getattr(exc, "content", b"")
        if content:
            try:
                payload = json.loads(content.decode("utf-8") if isinstance(content, bytes) else content)
                errors = payload.get("error", {}).get("errors", [])
                reason = errors[0].get("reason", "") if errors else payload.get("error", {}).get("status", "")
            except (AttributeError, IndexError, TypeError, ValueError):
                reason = ""
        return status if isinstance(status, int) else None, reason or type(exc).__name__

    @classmethod
    def _is_transient(cls, exc: Exception, status: int | None) -> bool:
        if status in cls._RETRYABLE_STATUSES:
            return True
        return isinstance(exc, (TimeoutError, ConnectionError, OSError))

    def _execute(self, operation: str, a1_range: str, request: Any) -> Any:
        with self._service_lock:
            for attempt in range(1, self._MAX_ATTEMPTS + 1):
                logger.info(
                    "Google Sheets %s attempt=%s range=%s endpoint=%s",
                    operation,
                    attempt,
                    a1_range,
                    request_endpoint.get(),
                )
                try:
                    result = request().execute()
                    logger.info(
                        "Google Sheets %s successful attempt=%s range=%s endpoint=%s",
                        operation,
                        attempt,
                        a1_range,
                        request_endpoint.get(),
                    )
                    return result
                except Exception as exc:
                    status, reason = self._error_details(exc)
                    if not self._is_transient(exc, status):
                        logger.error(
                            "Google Sheets permanent error operation=%s status=%s reason=%s range=%s endpoint=%s",
                            operation,
                            status or "unknown",
                            reason,
                            a1_range,
                            request_endpoint.get(),
                        )
                        raise GoogleSheetsError(
                            f"Error permanente de Google Sheets ({status or 'desconocido'}): {reason}.",
                            status=status,
                        ) from exc
                    logger.warning(
                        "Google Sheets temporary error operation=%s status=%s reason=%s attempt=%s range=%s endpoint=%s",
                        operation,
                        status or "network",
                        reason,
                        attempt,
                        a1_range,
                        request_endpoint.get(),
                    )
                    if attempt == self._MAX_ATTEMPTS:
                        raise GoogleSheetsError(
                            f"Google Sheets no está disponible temporalmente ({status or 'red'}).",
                            transient=True,
                            status=status,
                        ) from exc
                    delay = 0.25 * (2 ** (attempt - 1))
                    logger.info(
                        "Google Sheets retrying attempt=%s operation=%s range=%s endpoint=%s",
                        attempt + 1,
                        operation,
                        a1_range,
                        request_endpoint.get(),
                    )
                    time.sleep(delay)

    def _values_get(self, a1_range: str) -> list[list[Any]]:
        result = self._execute(
            "read",
            a1_range,
            lambda: self.service.spreadsheets().values().get(
                spreadsheetId=self.settings.GOOGLE_SHEET_ID, range=self._range(a1_range)
            ),
        )
        return result.get("values", [])

    def _values_update(self, a1_range: str, values: list[list[Any]]) -> None:
        self._execute(
            "update",
            a1_range,
            lambda: self.service.spreadsheets().values().update(
                spreadsheetId=self.settings.GOOGLE_SHEET_ID,
                range=self._range(a1_range),
                valueInputOption="RAW",
                body={"values": values},
            ),
        )

    def _values_append(self, a1_range: str, values: list[list[Any]]) -> None:
        self._execute(
            "append",
            a1_range,
            lambda: self.service.spreadsheets().values().append(
                spreadsheetId=self.settings.GOOGLE_SHEET_ID,
                range=self._range(a1_range),
                valueInputOption="RAW",
                insertDataOption="INSERT_ROWS",
                body={"values": values},
            ),
        )

    def ensure_header(self) -> None:
        rows = self._values_get("A1:I1")
        if not rows or not rows[0]:
            self._values_update("A1:I1", [SHEET_HEADER])
            return

        first_cell = str(rows[0][0]).strip().lower()
        if first_cell in {"usuario", "user", "username"} and len(rows[0]) < len(SHEET_HEADER):
            self._values_update("A1:I1", [SHEET_HEADER])

    def list_users(self) -> list[tuple[int, UserRecord]]:
        rows = self._values_get("A2:I")
        users: list[tuple[int, UserRecord]] = []
        for index, row in enumerate(rows, start=2):
            if row and str(row[0]).strip():
                users.append((index, UserRecord.from_sheet_row(row)))
        return users

    def get_user(self, username: str) -> tuple[int, UserRecord] | None:
        username_key = username.strip().lower()
        for row_number, user in self.list_users():
            if user.username.lower() == username_key:
                return row_number, user
        return None

    def append_user(self, user: UserRecord) -> None:
        self.ensure_header()
        self._values_append("A:I", [user.to_sheet_row()])

    def update_user(self, user: UserRecord) -> None:
        found = self.get_user(user.username)
        if not found:
            raise GoogleSheetsError(f"No se encontro el usuario {user.username}.")
        row_number, _ = found
        self._values_update(f"A{row_number}:I{row_number}", [user.to_sheet_row()])

    def check_connection(self) -> None:
        self._values_get("A1:I1")
