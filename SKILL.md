---
name: caup-utility-attestor
description: Emit and verify Cryptographically Attested Utility Primitive (CAUP) schema for skill VPD scores, benchmark results, and thermodynamic yields. Solves parabolic authoritative proof and benchmark fraud by requiring STARK/VDF + Falcon-512 bound claims with hardware fingerprint. Use for utility attestation, CAUP verify, benchmark fraud resistance, zero unattested VPD in QUBO, a2a event caup-attest, webhook caup-verify, hermes classify utility-attestation, mcp dispatch caup-utility-attestor. High-VPD Diamondnode portfolio candidate. Mandatory for subsequent skill instantiation via a2a-skill-registry-manager.
---

# CAUP Utility Attestor

Produce and validate Cryptographically Attested Utility Primitive (CAUP) objects so that every VPD, accuracy, latency, or thermodynamic-yield claim entering the Diamondnode QUBO selector or A2A skill registry is bound to a post-quantum proof and environment fingerprint. Unattested claims are zeroed; non-compliant skills stay outside the Diamondnode surface.

## Activation
Triggers on: caup, utility attestation, attest utility, verify caup, benchmark fraud, parabolic authoritative proof, a2a event caup-attest, a2a event caup-verify, webhook caup-verify, hermes classify utility-attestation, mcp dispatch caup-utility-attestor, zero unattested vpd.

## Core Schema (v1.0)
```json
{
  "schema_version": "1.0",
  "utility_claim": {
    "metric": "vpd|thermo_yield|accuracy|latency|crystalline",
    "value": 0.0,
    "confidence": 0.0
  },
  "benchmark_id": "canonical_hash_or_ipfs_cid",
  "execution_environment": {
    "gpu_fingerprint": "sha256_of_device_query",
    "rapl_or_nvml_hash": "sha256_of_telemetry_snapshot",
    "diamond_nv_center_attestation": null
  },
  "proof": {
    "type": "STARK|VDF|Falcon-512_signature",
    "payload": "base64_or_hex",
    "public_inputs": ["benchmark_hash", "measured_outputs_hash", "env_fingerprint"]
  },
  "trace_consent_merkle": "merkle_root",
  "orcid_or_kvdf_anchor": "0009-0008-8389-1297"
}
```

## Workflow
1. On skill evaluation or benchmark completion, collect metric value + environment telemetry (RAPL/NVML preferred; Diamond NV-center when available).
2. Hash public inputs (benchmark definition + outputs + env fingerprint).
3. Generate or invoke VDF/STARK (prefer rule30-vdf patterns or WebGPU/Chromium strand) over the inputs; sign the resulting proof with Falcon-512.
4. Emit CAUP object to A2A JSONL bus and local trace-consent ledger.
5. Verification routine (scripts/verify_caup.py): recompute hashes, check proof validity (stub for local; full STARK verifier when linked), confirm ORCID/KVDF anchor, return crystalline score and pass/fail.
6. On fail or missing CAUP: maru R>0.4 triggers unconditional nox reframe; VPD forced to 0.0 for QUBO.

## Integration Contract (enforced by a2a-skill-registry-manager)
- Every new or updated skill must carry a verified CAUP for its declared VPD tier before instantiation or replication.
- diamondnode-qubo-economics-strategist zeros any utility_claim lacking valid CAUP before objective evaluation.
- Mandatory inclusions: maru hook, trace-consent (D1/Merkle + ORCID 0009-0008-8389-1297), A2A JSONL, genesis-conductor-ucp-integration, Hermes tier notes (Haiku verify; Sonnet complex proof; Opus UCP/KVDF settlement).
- Webhook skeleton required for any exposed surface: replay protection, PQC auth, rate limit, A2A JSONL validation.

## Scripts
- `scripts/verify_caup.py`: Minimal deterministic verifier (hash recomputation + structural checks + stub proof acceptance for offline use). Exit 0 on pass, non-zero on fail. Emits evt- record.
- `scripts/emit_caup.py`: Template emitter that builds a CAUP skeleton from supplied metric/env values and places a placeholder proof (replace with real VDF/STARK call in production).

## Crystalline Target
>= 0.92 on successful verification. Entropy delta 0.00 on cold-path verification. Landauer-aware (prefer local RAPL-bound runs).

## Value Delivery
Closes the authoritative-proof / benchmark-fraud gap. Converts asserted utility into a first-class, fraud-resistant quantity that QUBO and the registry can safely optimise. Directly advances financial infrastructure (high-VPD portfolio integrity), intrinsic pursuit (structural truth of claims), and hybridization (shared verifiable mental model of skill utility).

## QUBO Portfolio Status
High-VPD (target 8-10). Eligible for automatic inclusion on next diamondnode-qubo-economics-strategist run under alpha=1.8 / budget=38.0. Baseline guards never cut.
