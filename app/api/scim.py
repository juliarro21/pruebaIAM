from fastapi import APIRouter, HTTPException, status, Request
from fastapi.responses import JSONResponse
from typing import Any, Dict
from app.models.scim import SCIMUserIn
from app.services.scim_service import store

router = APIRouter(prefix="/scim/v2", tags=["SCIM"])

@router.post("/Users", status_code=201)
def create_user(user: SCIMUserIn, request: Request):
    try:
        out = store.create(user)
        resp = JSONResponse(status_code=201, content=out.model_dump())
        resp.headers["Location"] = str(request.base_url).rstrip("/") + f"/scim/v2/Users/{out.id}"
        return resp
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.get("/Users/{uid}")
def get_user(uid: str):
    out = store.get(uid)
    if not out:
        raise HTTPException(status_code=404, detail="User not found")
    return out

@router.patch("/Users/{uid}")
def patch_user(uid: str, body: Dict[str, Any]):
    out = store.patch(uid, body)
    if not out:
        raise HTTPException(status_code=404, detail="User not found")
    return out

@router.get("/Users")
def search_users(filter: str | None = None):
    resources = []
    if filter:
        f = filter.strip()
        if f.lower().startswith("username eq"):
            q = f.split("eq",1)[1].strip()
            if q.startswith('"') and q.endswith('"'):
                username = q[1:-1]
                resources = [u.model_dump() for u in store.find_by_username(username)]
    return {
        "schemas": ["urn:ietf:params:scim:api:messages:2.0:ListResponse"],
        "totalResults": len(resources),
        "startIndex": 1,
        "itemsPerPage": len(resources),
        "Resources": resources,
    }
