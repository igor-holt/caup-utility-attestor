# CAUP Utility Attestor

**Cryptographically Attested Utility Primitive** for Genesis Conductor / Diamondnode.

Closes the gap between asserted utility (VPD, thermo yield, benchmark scores) and verifiable claims. Solves the parabolic authoritative proof and benchmark fraud problem by requiring every non-baseline skill to present a CAUP object (schema 1.0) before it can enter the QUBO selector or be instantiated by `a2a-skill-registry-manager`.

## Status
- Skill instantiated locally under `~/.grok/skills/caup-utility-attestor/`
- Registered via a2a-skill-registry-manager (mandatory CAUP inclusion added)
- QUBO optimizer patched for zeroing unattested claims
- Example run: objective 53.2, VPD/cost 3.325, CAUP-hardened portfolio selected
- Crystalline on sample verification: 0.92

## Quick Start
```bash
# Emit a CAUP skeleton
python scripts/emit_caup.py vpd 8.5 0.92 skill-benchmark-v1 gpu-fp-xxx rapl-hash-yyy

# Verify
python scripts/verify_caup.py artifacts/caup_....json

# Run hardened QUBO (zeros unattested)
python scripts/diamondnode_economics_qubo_optimizer.py
```

## Integration
- **a2a-skill-registry-manager**: Non-compliant skills stay outside Diamondnode surface.
- **diamondnode-qubo-economics-strategist**: Unattested VPD forced to 0.0 before objective.
- Proof backend: prefer `rule30-vdf` (STARK/VDF) + Falcon-512; Diamond NV-center attestation path reserved.
- ORCID anchor: 0009-0008-8389-1297

## Repo
https://github.com/igor-holt/caup-utility-attestor

Part of the high-VPD Diamondnode / Genesis Conductor portfolio. Baseline guards never cut.
