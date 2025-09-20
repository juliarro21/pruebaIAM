from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from app.core.config import settings
from app.core.jwt_utils import sign, verify
from app.services.scim_service import store

def _exp():
    return int((datetime.now(timezone.utc) + timedelta(seconds=settings.JWT_EXP_SECONDS)).timestamp())

def issue_password(username: str, password: str, scope: Optional[str]) -> Dict[str, Any]:
    rec = store.get_raw_by_username(username)
    if not rec or not rec.get("active", False):
        raise ValueError("invalid_user")
    claims = {
        "sub": username,
        "scope": scope or "basic",
        "groups": rec.get("groups", []),
        "dept": rec.get("dept", None),
        "riskScore": rec.get("riskScore", 0),
        "exp": _exp(),
    }
    token = sign(claims)
    return {"access_token": token, "token_type": "Bearer", "expires_in": settings.JWT_EXP_SECONDS}

def issue_client_credentials(client_id: str, client_secret: str, scope: Optional[str]) -> Dict[str, Any]:
    if client_id != settings.CLIENT_ID or client_secret != settings.CLIENT_SECRET:
        raise ValueError("invalid_client")
    claims = {
        "sub": f"client:{client_id}",
        "scope": scope or "system",
        "groups": [],
        "dept": "system",
        "riskScore": 0,
        "exp": _exp(),
    }
    token = sign(claims)
    return {"access_token": token, "token_type": "Bearer", "expires_in": settings.JWT_EXP_SECONDS}

def parse(token: str) -> Dict[str, Any]:
    return verify(token)
