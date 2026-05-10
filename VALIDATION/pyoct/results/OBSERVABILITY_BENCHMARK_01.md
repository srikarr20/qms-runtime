# Observability Benchmark 01

## Objective

Evaluate how acquisition degradation affects:

- visibility,
- observability,
- coherence transfer,
- and reconstruction fidelity.

Goal:
compare QMS observability semantics
against coherence-sensitive acquisition behavior
inspired by PyOCT.

---

# Test Conditions

## Synthetic Field

- coherent interference pattern
- ideal upstream visibility ≈ 0.98

## Acquisition Degradation Parameters

### High Fidelity
- low blur
- low noise
- no binning

### Medium Fidelity
- moderate blur
- moderate noise
- 4× binning

### Coarse Acquisition
- strong blur
- strong noise
- 8× binning

---

# Validation Questions

1. Does observability degrade progressively?
2. Does visibility collapse under coarse acquisition?
3. Is lost observability recoverable downstream?
4. Does degradation arise from acquisition alone?
5. Does the trend align with PyOCT-style coherence sensitivity?

---

# Expected QMS-Relevant Outcomes

- detector-conditioned visibility collapse
- acquisition-limited observability
- irreversible reconstruction loss
- coherence-sensitive observability degradation

---

# Planned Metrics

- visibility
- observability index
- visibility loss
- acquisition degradation severity
- recoverability assessment
