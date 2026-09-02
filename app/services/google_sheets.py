import json
import threading
from functools import cached_property
from typing import Any

from app.config import Settings
from app.models.user import UserRecord


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


class GoogleSheetsRepository:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._write_lock = threading.RLock()

    @cached_property
    def service(self) -> Any:
        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build
        except ImportError as exc:
            raise GoogleSheetsError(
                "Faltan dependencias de Google Sheets. Ejecuta `pip install -r requirements.txt`."
            ) from exc

        credentials_payload = self._credentials_payload()
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

        return build("sheets", "v4", credentials=credentials, cache_discovery=False)

    def _credentials_payload(self) -> dict[str, Any] | str:
        if self.settings.GOOGLE_SERVICE_ACCOUNT_INFO:
            try:
                return json.loads(self.settings.GOOGLE_SERVICE_ACCOUNT_INFO)
            except json.JSONDecodeError as exc:
                raise GoogleSheetsError("GOOGLE_SERVICE_ACCOUNT_INFO no contiene JSON valido.") from exc
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

    def _values_get(self, a1_range: str) -> list[list[Any]]:
        try:
            result = (
                self.service.spreadsheets()
                .values()
                .get(spreadsheetId=self.settings.GOOGLE_SHEET_ID, range=self._range(a1_range))
                .execute()
            )
        except Exception as exc:
            raise GoogleSheetsError("No se pudo consultar Google Sheets.") from exc
        return result.get("values", [])

    def _values_update(self, a1_range: str, values: list[list[Any]]) -> None:
        try:
            (
                self.service.spreadsheets()
                .values()
                .update(
                    spreadsheetId=self.settings.GOOGLE_SHEET_ID,
                    range=self._range(a1_range),
                    valueInputOption="RAW",
                    body={"values": values},
                )
                .execute()
            )
        except Exception as exc:
            raise GoogleSheetsError("No se pudo actualizar Google Sheets.") from exc

    def _values_append(self, a1_range: str, values: list[list[Any]]) -> None:
        try:
            (
                self.service.spreadsheets()
                .values()
                .append(
                    spreadsheetId=self.settings.GOOGLE_SHEET_ID,
                    range=self._range(a1_range),
                    valueInputOption="RAW",
                    insertDataOption="INSERT_ROWS",
                    body={"values": values},
                )
                .execute()
            )
        except Exception as exc:
            raise GoogleSheetsError("No se pudo agregar información a Google Sheets.") from exc

    def ensure_header(self) -> None:
        rows = self._values_get("A1:I1")
        if not rows or not rows[0]:
            self._values_update("A1:I1", [SHEET_HEADER])
            return

        first_cell = str(rows[0][0]).strip().lower()
        if first_cell in {"usuario", "user", "username"} and len(rows[0]) < len(SHEET_HEADER):
            self._values_update("A1:I1", [SHEET_HEADER])

    def list_users(self) -> list[tuple[int, UserRecord]]:
        self.ensure_header()
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
        with self._write_lock:
            self.ensure_header()
            self._values_append("A:I", [user.to_sheet_row()])

    def update_user(self, user: UserRecord) -> None:
        with self._write_lock:
            found = self.get_user(user.username)
            if not found:
                raise GoogleSheetsError(f"No se encontro el usuario {user.username}.")
            row_number, _ = found
            self._values_update(f"A{row_number}:I{row_number}", [user.to_sheet_row()])
