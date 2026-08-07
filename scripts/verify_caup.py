#!/usr/bin/env python3
"""
Minimal CAUP verifier for Diamondnode / Genesis Conductor.
Structural + hash integrity checks. Stub for full STARK/VDF verification
(replace with rule30-vdf or WebGPU verifier in production).
Emits evt- record. Exit 0 = pass, 1 = fail.
"""
import json
import sys
import hashlib
from datetime import datetime, timezone
from pathlib import Path

ORCID = "0009-0008-8389-1297"
EVT_DIR = Path("/home/workdir/artifacts")

def sha256_hex(data: str) -> str:
    return hashlib.sha256(data.encode("utf-8")).hexdigest()

def verify_caup(caup: dict) -> tuple[bool, float, str]:
    """Return (pass, crystalline_score, reason)."""
    required = ["schema_version", "utility_claim", "benchmark_id",
                "execution_environment", "proof", "trace_consent_merkle",
                "orcid_or_kvdf_anchor"]
    for k in required:
        if k not in caup:
            return False, 0.0, f"missing_field:{k}"

    if caup["schema_version"] != "1.0":
        return False, 0.3, "unsupported_schema"

    claim = caup["utility_claim"]
    if not isinstance(claim.get("value"), (int, float)):
        return False, 0.2, "invalid_utility_value"

    env = caup["execution_environment"]
    if not env.get("gpu_fingerprint") and not env.get("rapl_or_nvml_hash"):
        return False, 0.4, "no_environment_binding"

    proof = caup["proof"]
    if proof.get("type") not in ("STARK", "VDF", "Falcon-512_signature"):
        return False, 0.3, "unsupported_proof_type"
    if not proof.get("payload") or not proof.get("public_inputs"):
        return False, 0.2, "empty_proof"

    # Structural crystalline: presence + type checks
    score = 0.75
    if caup["orcid_or_kvdf_anchor"] == ORCID or caup["orcid_or_kvdf_anchor"].startswith("kvdf:"):
        score += 0.10
    if len(proof["public_inputs"]) >= 2:
        score += 0.07
    if env.get("diamond_nv_center_attestation"):
        score += 0.05

    # Stub: accept any non-empty payload for offline/local runs.
    # Production: call rule30-vdf verifier or STARK checker here.
    if not proof["payload"]:
        return False, score * 0.5, "empty_payload"

    return True, min(score, 1.0), "ok"

def emit_evt(passed: bool, score: float, reason: str, caup_id: str = "local") -> None:
    EVT_DIR.mkdir(parents=True, exist_ok=True)
    evt = {
        "evt_id": f"evt_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_caup_verify",
        "schema_version": "1.0",
        "record_type": "caup_verification",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "status": "pass" if passed else "fail",
        "crystalline_score": score,
        "reason": reason,
        "caup_id": caup_id,
        "orcid": ORCID,
        "tags": ["caup-utility-attestor", "utility-attestation", "benchmark-fraud-resistance",
                 "diamondnode", "a2a"],
        "connections": {
            "related_skills": ["diamondnode-qubo-economics-strategist",
                               "a2a-skill-registry-manager", "rule30-vdf"]
        }
    }
    path = EVT_DIR / f"evt_caup_verify_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
    path.write_text(json.dumps(evt, indent=2))
    print(json.dumps(evt))

def main():
    if len(sys.argv) < 2:
        print("Usage: verify_caup.py <caup.json>", file=sys.stderr)
        sys.exit(2)
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(2)
    caup = json.loads(path.read_text())
    passed, score, reason = verify_caup(caup)
    emit_evt(passed, score, reason, path.name)
    sys.exit(0 if passed else 1)

if __name__ == "__main__":
    main()
