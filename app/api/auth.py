from fastapi import APIRouter, HTTPException, Header, Depends, Request
from typing import Optional, Dict, Any
from app.services.auth_service import issue_password, issue_client_credentials, parse

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/token")
def token(body: Dict[str, Any]):
    gt = body.get("grant_type") or ("password" if body.get("username") else "client_credentials")
    try:
        if gt == "password":
            return issue_password(body.get("username",""), body.get("password",""), body.get("scope"))
        return issue_client_credentials(body.get("client_id",""), body.get("client_secret",""), body.get("scope"))
    except ValueError as e:
        if str(e) == "invalid_user":
            raise HTTPException(status_code=401, detail="invalid_user")
        if str(e) == "invalid_client":
            raise HTTPException(status_code=401, detail="invalid_client")
        raise

@router.get("/me")
def me(authorization: Optional[str] = Header(None)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing_bearer_token")
    token = authorization.split(" ",1)[1]
    try:
        return parse(token)
    except Exception:
        raise HTTPException(status_code=401, detail="invalid_token")
