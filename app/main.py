from fastapi import FastAPI
from app.api import scim, auth, abac
from app.services.scim_service import init_seed

app = FastAPI(title="IAM Microservice", version="0.1.0")
app.include_router(scim.router)
app.include_router(auth.router)
app.include_router(abac.router)

@app.get("/health")
def health():
    return {"status":"ok"}

@app.on_event("startup")
def _startup():
    init_seed()
