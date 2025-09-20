from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class SCIMName(BaseModel):
    givenName: str
    familyName: str

class SCIMEmail(BaseModel):
    value: str
    primary: Optional[bool] = False

class SCIMUserIn(BaseModel):
    model_config = {"extra": "allow"}
    userName: str
    name: SCIMName
    active: bool = True
    emails: List[SCIMEmail]
    groups: Optional[List[str]] = Field(default_factory=list)

class SCIMUserOut(BaseModel):
    schemas: List[str] = ["urn:ietf:params:scim:schemas:core:2.0:User"]
    id: str
    userName: str
    name: Dict[str, Any]
    active: bool
    emails: List[Dict[str, Any]]
    groups: List[str] = Field(default_factory=list)
    meta: Dict[str, Any]
