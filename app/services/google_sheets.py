import json
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
        result = (
            self.service.spreadsheets()
            .values()
            .get(spreadsheetId=self.settings.GOOGLE_SHEET_ID, range=self._range(a1_range))
            .execute()
        )
        return result.get("values", [])

    def _values_update(self, a1_range: str, values: list[list[Any]]) -> None:
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

    def _values_append(self, a1_range: str, values: list[list[Any]]) -> None:
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
        print(f"[DEBUG google_sheets] get_user - looking for: {username}")
        username_key = username.strip().lower()
        for row_number, user in self.list_users():
            if user.username.lower() == username_key:
                print(f"[DEBUG google_sheets] get_user - FOUND at row {row_number}")
                print(f"[DEBUG google_sheets] get_user - password_hash type: {type(user.password_hash)}, len: {len(user.password_hash)}")
                print(f"[DEBUG google_sheets] get_user - password_hash first 50 chars: {user.password_hash[:50]}")
                return row_number, user
        print(f"[DEBUG google_sheets] get_user - NOT FOUND")
        return None

    def append_user(self, user: UserRecord) -> None:
        print(f"[DEBUG google_sheets] append_user - username: {user.username}")
        row = user.to_sheet_row()
        print(f"[DEBUG google_sheets] append_user - row[0] (username): {row[0]}")
        print(f"[DEBUG google_sheets] append_user - row[1] (password_hash) type: {type(row[1])}, len: {len(row[1])}")
        print(f"[DEBUG google_sheets] append_user - row[1] first 50 chars: {row[1][:50]}")
        self.ensure_header()
        self._values_append("A:I", [row])
        print(f"[DEBUG google_sheets] append_user - SUCCESS")

    def update_user(self, user: UserRecord) -> None:
        found = self.get_user(user.username)
        if not found:
            raise GoogleSheetsError(f"No se encontro el usuario {user.username}.")
        row_number, _ = found
        self._values_update(f"A{row_number}:I{row_number}", [user.to_sheet_row()])
