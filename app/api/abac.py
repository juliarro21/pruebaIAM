from fastapi import APIRouter
from typing import Dict, Any
from app.services.abac_service import load_engine

router = APIRouter(prefix="/authz", tags=["ABAC"])
_engine = load_engine()

@router.post("/evaluate")
def evaluate(body: Dict[str, Any]):
    subject = body.get("subject", {})
    resource = body.get("resource", {})
    context = body.get("context", {})
    return _engine.evaluate(subject, resource, context)
