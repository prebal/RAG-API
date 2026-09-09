import uuid
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException

from app.settings import get_settings

settings = get_settings()

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algo


def issue_jwt_token(user_id: int, time_window: int = 30) -> str:
    expires = datetime.now(UTC) + timedelta(minutes=time_window)
    payload = {"sub": str(user_id), "exp": expires, "type": "access"}

    return jwt.encode(payload, key=SECRET_KEY, algorithm=ALGORITHM)


def decode_jwt_token(token: str) -> dict[str, str]:
    try:
        return jwt.decode(token, SECRET_KEY, ALGORITHM)
    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token is expired")

    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token is invalid")


def issue_refresh_token(user_id: int, time_window_days: int = 14) -> str:
    expires = datetime.now(UTC) + timedelta(days=time_window_days)
    payload = {
        "sub": str(user_id),
        "exp": expires,
        "type": "refresh",
        "jti": str(uuid.uuid4()),
    }

    return jwt.encode(payload, key=SECRET_KEY, algorithm=ALGORITHM)
