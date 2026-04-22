from fastapi import Header, HTTPException, status

from app.core.config import get_settings


async def require_api_key(
    x_api_key: str | None = Header(default=None, alias="X-API-Key"),
    authorization: str | None = Header(default=None),
) -> str:
    """Accept either `X-API-Key: <key>` or `Authorization: Bearer <key>`.

    Raises 401 if the provided key isn't in the allowed set.
    """
    settings = get_settings()
    candidate: str | None = None
    if x_api_key:
        candidate = x_api_key.strip()
    elif authorization and authorization.lower().startswith("bearer "):
        candidate = authorization.split(" ", 1)[1].strip()

    if not candidate or candidate not in settings.api_key_set:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return candidate
