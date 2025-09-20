import json, os, uuid, time
from typing import Dict, List, Optional, Any
from app.models.scim import SCIMUserIn, SCIMUserOut

class SCIMStore:
    def __init__(self):
        self.by_id: Dict[str, Dict[str, Any]] = {}
        self.by_username: Dict[str, str] = {}

    def _now(self) -> str:
        return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    def _to_out(self, rec: Dict[str, Any]) -> SCIMUserOut:
        return SCIMUserOut(
            id=rec["id"],
            userName=rec["userName"],
            name=rec["name"],
            active=rec["active"],
            emails=rec["emails"],
            groups=rec.get("groups", []),
            meta={
                "resourceType": "User",
                "created": rec["created"],
                "lastModified": rec["lastModified"],
                "location": f"/scim/v2/Users/{rec['id']}",
            },
        )

    def seed_from_file(self, path: str):
        if not path or not os.path.exists(path):
            return
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for item in data:
            u = SCIMUserIn.model_validate(item)
            self.create(u, extras={k:v for k,v in item.items() if k not in u.model_dump()})

    def create(self, user_in: SCIMUserIn, extras: Optional[Dict[str, Any]]=None) -> SCIMUserOut:
        if user_in.userName in self.by_username:
            raise ValueError("userName already exists")
        uid = str(uuid.uuid4())
        now = self._now()
        rec: Dict[str, Any] = {
            "id": uid,
            "userName": user_in.userName,
            "name": user_in.name.model_dump(),
            "active": user_in.active,
            "emails": [e.model_dump() for e in user_in.emails],
            "groups": user_in.groups or [],
            "created": now,
            "lastModified": now,
        }
        if extras:
            rec.update(extras)
        self.by_id[uid] = rec
        self.by_username[user_in.userName] = uid
        return self._to_out(rec)

    def get(self, uid: str) -> Optional[SCIMUserOut]:
        rec = self.by_id.get(uid)
        return self._to_out(rec) if rec else None

    def patch(self, uid: str, patch: dict) -> Optional[SCIMUserOut]:
        rec = self.by_id.get(uid)
        if not rec:
            return None
        if "Operations" in patch:
            for op in patch["Operations"]:
                if op.get("op","").lower() == "replace":
                    path = op.get("path")
                    val = op.get("value")
                    if path == "active":
                        rec["active"] = bool(val)
                    elif path and path.startswith("name."):
                        _, key = path.split(".",1)
                        rec["name"][key] = val
                    elif path == "emails":
                        rec["emails"] = val
                    elif path == "groups":
                        rec["groups"] = val
        else:
            for k in ("active","name","emails","groups"):
                if k in patch:
                    rec[k] = patch[k]
        rec["lastModified"] = self._now()
        return self._to_out(rec)

    def find_by_username(self, username: str) -> List[SCIMUserOut]:
        uid = self.by_username.get(username)
        return [self._to_out(self.by_id[uid])] if uid else []

    def get_raw_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        uid = self.by_username.get(username)
        return self.by_id.get(uid) if uid else None

store = SCIMStore()

def init_seed():
    seed_path = os.getenv("SEED_USERS_PATH")
    store.seed_from_file(seed_path)
