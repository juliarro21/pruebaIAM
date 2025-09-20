from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from app.core.config import settings

def _keys():
    if settings.JWT_ALG.upper() == "HS256":
        return settings.JWT_SECRET, settings.JWT_SECRET
    with open(settings.JWT_PRIVATE_KEY_PATH,"rb") as f:
        priv = f.read()
    with open(settings.JWT_PUBLIC_KEY_PATH,"rb") as f:
        pub = f.read()
    return priv, pub

def sign(claims: dict) -> str:
    priv, _ = _keys()
    return jwt.encode(claims, priv, algorithm=settings.JWT_ALG)

def verify(token: str) -> dict:
    _, pub = _keys()
    return jwt.decode(token, pub, algorithms=[settings.JWT_ALG])
