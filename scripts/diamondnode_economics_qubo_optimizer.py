#!/usr/bin/env python3
"""
Diamondnode Economics QUBO Optimizer with CAUP zeroing.
Unattested utility claims are forced to VPD = 0 before selection.
"""
import json
import itertools
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

ORCID = "0009-0008-8389-1297"
ARTIFACTS = Path("/home/workdir/artifacts")
CAUP_VERIFY = Path("/home/workdir/.grok/skills/caup-utility-attestor/scripts/verify_caup.py")

# Baseline mandatory (never optimized away)
MANDATORY = [
    "mcp-llm-skill-api",
    "skill-creator",
    "genesis-conductor-ucp-integration",
    "maru",
    "trace-consent",
    "hermitian-audit",
    "rqa-rotation-quantization-auditor",
    "bash-process-substitution-zombie-guard",
]

# Example catalog subset for self-contained run (extend from xlsx in production)
DEFAULT_CATALOG = [
    {"name": "mcp-llm-skill-api", "vpd": 10, "cost": 3, "caup_path": None},
    {"name": "skill-creator", "vpd": 10, "cost": 3, "caup_path": None},
    {"name": "genesis-conductor-ucp-integration", "vpd": 9, "cost": 3, "caup_path": None},
    {"name": "maru", "vpd": 10, "cost": 1, "caup_path": None},
    {"name": "trace-consent", "vpd": 10, "cost": 1, "caup_path": None},
    {"name": "hermitian-audit", "vpd": 8, "cost": 1, "caup_path": None},
    {"name": "rqa-rotation-quantization-auditor", "vpd": 8, "cost": 1, "caup_path": None},
    {"name": "bash-process-substitution-zombie-guard", "vpd": 8, "cost": 1, "caup_path": None},
    {"name": "caup-utility-attestor", "vpd": 9, "cost": 2, "caup_path": "/home/workdir/artifacts/caup_vpd_20260807_151231.json"},
    {"name": "a2a-skill-registry-manager", "vpd": 9, "cost": 3, "caup_path": None},
    {"name": "unifying-thread", "vpd": 8, "cost": 2, "caup_path": None},
    {"name": "tunnel-through", "vpd": 8, "cost": 2, "caup_path": None},
    {"name": "yennefer-thermodynamic-daemon-deploy", "vpd": 7, "cost": 5, "caup_path": None},
    {"name": "x-radar-gov-fed", "vpd": 7, "cost": 3, "caup_path": None},
]

def has_valid_caup(caup_path: Optional[str]) -> bool:
    if not caup_path:
        return False
    p = Path(caup_path)
    if not p.exists():
        return False
    # Invoke the real verifier
    import subprocess
    r = subprocess.run(["python3", str(CAUP_VERIFY), str(p)], capture_output=True, text=True)
    return r.returncode == 0

def zero_unattested(catalog: List[Dict]) -> List[Dict]:
    """Force VPD=0 for any skill lacking a verified CAUP (except pure baseline guards)."""
    out = []
    for s in catalog:
        entry = dict(s)
        name = entry["name"]
        if name in MANDATORY:
            # Baseline always allowed; they are the guards themselves
            out.append(entry)
            continue
        if has_valid_caup(entry.get("caup_path")):
            out.append(entry)
        else:
            entry["vpd"] = 0.0
            entry["caup_status"] = "zeroed_unattested"
            out.append(entry)
    return out

def optimize(catalog: List[Dict], alpha: float = 1.8, budget: float = 38.0) -> Dict[str, Any]:
    catalog = zero_unattested(catalog)
    n = len(catalog)
    best_obj = float("-inf")
    best_x = None
    best_selected = []

    # Exact enumeration for small n (production: use QAOA / classical MIP)
    for mask in range(1 << n):
        selected = []
        total_cost = 0.0
        obj = 0.0
        valid_mandatory = True
        for i, s in enumerate(catalog):
            if (mask >> i) & 1:
                selected.append(s["name"])
                total_cost += s["cost"]
                obj += (s["vpd"] - alpha * s["cost"])
        # Enforce all mandatory present
        for m in MANDATORY:
            if m not in selected:
                valid_mandatory = False
                break
        if not valid_mandatory or total_cost > budget:
            continue
        if obj > best_obj:
            best_obj = obj
            best_x = mask
            best_selected = selected

    ratio = best_obj / max(sum(s["cost"] for s in catalog if s["name"] in best_selected), 1e-9)
    result = {
        "schema_version": "1.0",
        "record_type": "diamondnode_qubo_result",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parameters": {"alpha": alpha, "budget": budget},
        "objective": best_obj,
        "vpd_cost_ratio": ratio,
        "selected_skills": best_selected,
        "mandatory_enforced": True,
        "caup_zeroing_applied": True,
        "orcid": ORCID,
        "tags": ["qubo", "diamondnode-economics", "caup-hardened", "a2a"]
    }
    return result

def main():
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    result = optimize(DEFAULT_CATALOG)
    out = ARTIFACTS / "diamondnode_economics_qubo_result.json"
    out.write_text(json.dumps(result, indent=2))
    print(json.dumps(result, indent=2))
    print(f"Wrote {out}")

if __name__ == "__main__":
    main()
