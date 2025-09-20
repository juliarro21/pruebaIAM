import json, os
from typing import Any, Dict, List, Tuple

def _get(path: str, data: Dict[str, Any]):
    cur: Any = data
    for p in path.split("."):
        if isinstance(cur, dict) and p in cur:
            cur = cur[p]
        else:
            return None
    return cur

def _cmp(key: str, expect: Any, inp: Dict[str, Any]) -> Tuple[bool, Tuple[str,str,Any]]:
    if key.endswith(">="):
        path = key[:-2]
        val = _get(path, inp)
        try:
            return (float(val) >= float(expect)), (path, ">=", expect)
        except Exception:
            return False, (path, ">=", expect)
    if key.endswith("!="):
        path = key[:-2]
        val = _get(path, inp)
        return (val != expect), (path, "!=", expect)
    if key.endswith("~"):
        path = key[:-1]
        val = _get(path, inp)
        if isinstance(val, list):
            return (expect in val), (path, "~", expect)
        return False, (path, "~", expect)
    if key.endswith("NotIn"):
        path = key[:-5]
        val = _get(path, inp)
        return (val not in expect), (path, "NotIn", expect)
    path = key
    val = _get(path, inp)
    return (val == expect), (path, "==", expect)

def _match_all(conds: Dict[str, Any], inp: Dict[str, Any]) -> bool:
    for k, v in conds.items():
        ok, _ = _cmp(k, v, inp)
        if not ok:
            return False
    return True

def _match_else_for_neq(conds: Dict[str, Any], inp: Dict[str, Any]) -> bool:
    base: Dict[str, Any] = {}
    flip: Dict[str, Any] = {}
    for k, v in conds.items():
        if k.endswith("!="):
            flip[k[:-2]] = v
        else:
            base[k] = v
    if not flip:
        return False
    if not _match_all(base, inp):
        return False
    for path, v in flip.items():
        val = _get(path, inp)
        if val != v:
            return False
    return True

class ABACEngine:
    def __init__(self, policies: List[Dict[str, Any]]):
        self.policies = policies

    def evaluate(self, subject: Dict[str, Any], resource: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        inp = {"subject": subject or {}, "resource": resource or {}, "context": context or {}}
        matched: List[Tuple[str,str]] = []
        for r in self.policies:
            rid = r.get("id","unknown")
            eff = r.get("effect","Deny")
            when = r.get("when", {})
            when_any = r.get("whenAny", [])
            hit = False
            if when and _match_all(when, inp):
                hit = True
            elif when_any and any(_match_all(conds, inp) for conds in when_any):
                hit = True
            elif r.get("else") and when and _match_else_for_neq(when, inp):
                eff = r["else"].get("effect", eff)
                hit = True
            if hit:
                matched.append((rid, eff))
        decision = "Deny"
        if any(eff == "Challenge" for _, eff in matched):
            decision = "Challenge"
        elif any(eff == "Permit" for _, eff in matched):
            decision = "Permit"
        reasons = [f"ruleId: {rid}" for rid, _ in matched] or ["ruleId: none"]
        return {"decision": decision, "reasons": reasons}

def load_engine() -> ABACEngine:
    path = os.getenv("POLICIES_PATH")
    with open(path, "r", encoding="utf-8") as f:
        pol = json.load(f)
    return ABACEngine(pol)
