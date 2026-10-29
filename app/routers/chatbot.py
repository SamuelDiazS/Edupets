import asyncio
import json
import time
from collections import defaultdict, deque

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from app.config import get_settings
from app.dependencies import verify_csrf
from app.services.chatbot_service import (
    CLARIFICATION_REPLY,
    OUT_OF_SCOPE_REPLY,
    GeminiQuotaError,
    GeminiRequestError,
    GeminiUnavailableError,
    classify_message,
    generate_tutor_reply,
)


router = APIRouter()

MAX_BODY_BYTES = 12_000
MAX_MESSAGES_PER_MINUTE = 8
MAX_TRACKED_CLIENTS = 4096
RATE_WINDOW_SECONDS = 60
_request_times: dict[str, deque[float]] = defaultdict(deque)
_rate_lock = asyncio.Lock()
_model_slots = asyncio.Semaphore(2)


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=500)
    history: list[str] = Field(default_factory=list, max_length=4)

    @field_validator("history")
    @classmethod
    def limit_history_message_length(cls, history: list[str]) -> list[str]:
        if any(len(message) > 500 for message in history):
            raise ValueError("El historial contiene un mensaje demasiado largo.")
        return history


async def _check_rate_limit(client_key: str) -> None:
    now = time.monotonic()
    async with _rate_lock:
        for key in list(_request_times):
            if not _request_times[key] or now - _request_times[key][-1] >= RATE_WINDOW_SECONDS:
                del _request_times[key]
        recent = _request_times[client_key]
        while recent and now - recent[0] >= RATE_WINDOW_SECONDS:
            recent.popleft()
        if len(recent) >= MAX_MESSAGES_PER_MINUTE:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Has enviado muchos mensajes. Espera un minuto y vuelve a intentarlo.",
            )
        if len(_request_times) > MAX_TRACKED_CLIENTS:
            oldest_key = min(_request_times, key=lambda key: _request_times[key][-1])
            if oldest_key != client_key:
                del _request_times[oldest_key]
        recent.append(now)


@router.post("/api/chat")
async def chat(request: Request):
    if not request.headers.get("x-csrf-token"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No se pudo validar la solicitud.")
    await verify_csrf(request)

    declared_length = request.headers.get("content-length")
    if declared_length:
        try:
            if int(declared_length) > MAX_BODY_BYTES:
                raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="El mensaje es demasiado largo.")
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La solicitud no es válida.") from exc

    body = bytearray()
    async for chunk in request.stream():
        body.extend(chunk)
        if len(body) > MAX_BODY_BYTES:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="El mensaje es demasiado largo.")

    try:
        payload = json.loads(body)
        chat_request = ChatRequest.model_validate(payload)
    except (json.JSONDecodeError, UnicodeDecodeError, ValidationError, TypeError):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Escribe un mensaje corto para el tutor.") from None

    await _check_rate_limit(request.client.host if request.client else "unknown")

    math_history: list[str] = []
    has_math_context = False
    for previous_message in chat_request.history:
        if classify_message(previous_message, has_math_context) == "math":
            math_history.append(previous_message)
            has_math_context = True

    classification = classify_message(chat_request.message, has_math_context)
    if classification == "reject":
        return {"reply": OUT_OF_SCOPE_REPLY, "math_allowed": False}
    if classification == "clarify":
        return {"reply": CLARIFICATION_REPLY, "math_allowed": False}

    api_key = get_settings().GEMINI_API_KEY
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El tutor no está disponible por ahora. Inténtalo más tarde.",
        )

    try:
        await asyncio.wait_for(_model_slots.acquire(), timeout=1)
    except TimeoutError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="El tutor está atendiendo a otros estudiantes. Inténtalo en un momento.",
        ) from exc

    try:
        reply = await generate_tutor_reply(chat_request.message, math_history, api_key)
    except GeminiQuotaError as exc:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="El tutor alcanzó su límite temporal. Espera un momento y vuelve a intentarlo.",
        ) from exc
    except GeminiUnavailableError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar con el tutor. Inténtalo más tarde.",
        ) from exc
    except GeminiRequestError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No pude preparar una respuesta. Prueba con otra pregunta de matemáticas.",
        ) from exc
    finally:
        _model_slots.release()

    return {"reply": reply, "math_allowed": True}