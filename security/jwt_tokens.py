import jwt
import os
from dotenv import load_dotenv
from datemtime import datetime, timedelta, timezone
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY") 
ALGORITHM = os.getenv("ALGO")

def issue_jwt_token(user_id: int, time_window: int = 30):
    expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    payload =  {
        "sub": str(user_id),
        "exp": expires,
    }

    return jwt.encode(payload, key = SECRET_KEY, algorithm = ALGORITHM)

def decode_verify_jwt_token():
    pass

