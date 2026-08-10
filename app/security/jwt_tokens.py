import os
from datetime import datetime, timedelta, timezone
from typing import Dict

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") 
ALGORITHM = os.getenv("ALGO")

def issue_jwt_token(user_id: int, time_window: int = 30) -> str:
    expires = datetime.now(timezone.utc) + timedelta(minutes=time_window)
    payload =  {
        "sub": str(user_id),
        "exp": expires,
    }

    return jwt.encode(payload, key = SECRET_KEY, algorithm = ALGORITHM)

def decode_jwt_token(token: str) -> Dict[str, str]:
    try:
        return jwt.decode(token, SECRET_KEY, ALGORITHM)

    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=401, detail = "Token is invalid")

    except jwt.exceptions.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail = "Token is expired")
    
    
