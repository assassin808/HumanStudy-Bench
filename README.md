# HumanStudyBench

A benchmark framework for evaluating LLM agents on classic human behavioral studies.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

Evaluating whether LLM agents can faithfully reproduce human behavior requires answering two distinct questions: **Do agents exhibit the psychological phenomena?** and **How closely do agent behaviors match human data distributions?** HumanStudyBench addresses both through a dual-validation framework.

### Two Classes of Validation

**Phenomena Validation** tests whether agents exhibit the core psychological effects reported in original studies. These tests replicate the exact statistical analyses from published papers (e.g., chi-square tests, t-tests, ANOVA) with identical significance thresholds. An agent passes phenomena validation if it demonstrates the same cognitive or behavioral patterns that defined the original findings—proving the phenomenon exists in agent behavior.

**Data Replication** quantifies the fidelity of agent behavior to human baselines. Unlike phenomena validation, which asks "Is the effect present?", data replication asks "How similar are the magnitudes?" This requires a unified statistical framework that can compare agents to humans across studies with vastly different data granularities—from complete response distributions to summary statistics alone.

### Statistical Framework for Data Replication

**Challenge:** Social science papers report varying levels of detail. Some provide full datasets, others only means and standard errors. Fair comparison across studies requires standardization.

**Solution:** Equivalence testing with a single global tolerance parameter.

**Core Hypothesis:**
- H₀: |standardized effect| ≥ δ (agent behavior differs from human baseline)
- H₁: |standardized effect| < δ (agent behavior equivalent to human baseline)

**Unified Approach:**
1. **Standardize all metrics** to a common scale (Freeman-Tukey for proportions, Cohen's d for means, direct comparison for effect sizes)
2. **Apply single tolerance threshold** δ = 0.2 (Cohen's "negligible" effect size) uniformly across all studies
3. **Test equivalence via TOST** (Two One-Sided Tests): reject H₀ if p < 0.05 → can claim behavioral equivalence
4. **Score continuously**: Reliability Score = 1 - p_TOST (lower p-values indicate stronger evidence of human-like behavior)

This framework ensures fair comparison across studies regardless of reported data granularity, while maintaining statistical rigor for claims of behavioral replication.

---

## Features

- 🧪 Curated studies across domains 
- 👤 LLM‑as‑Participant: agents act as human participants
- 📊 Built‑in validation against ground truth results
- 💾 Caching: run once, re‑evaluate for free
- 🔧 Extensible study/config system and metrics
- 📚 Documentation and examples included

## Quick start

Run an experiment with caching, then evaluate cached results without new API calls.

```bash
# Run Asch (study_001) with caching
python run_full_benchmark.py \
  --real-llm \
  --model mistralai/mistral-nemo \
  --studies study_001 \
  --n-participants 5 \
  --num-workers 3 \
  --use-cache

# Evaluate latest cached result (no API calls)
python evaluate_results.py --latest

# Or evaluate all cached runs
python evaluate_results.py --all
```

## Usage

```bash
python run_full_benchmark.py [OPTIONS]
```

Key options:

| Option | Description | Default |
|---|---|---|
| `--real-llm` | Use real LLM (vs. mock agent) | Off |
| `--model MODEL` | LLM model id (OpenRouter supported) | mistralai/mistral-nemo |
| `--studies STUDY [STUDY...]` | Studies to run | All |
| `--n-participants N` | Number of participants | Study default |
| `--num-workers N` | Parallel workers | 5 |
| `--use-cache` | Enable caching | Off |
| `--cache-dir DIR` | Cache directory | results/cache |
| `--random-seed SEED` | Seed for reproducibility | 42 |

## Cache system

- On `--use-cache`, results are saved and reused by signature (study, model, participants, seed).
- Re‑evaluate cached data with `evaluate_results.py` without making new API calls.

Filename format:

```
{study_id}__{model_slug}__n{participants}__seed{seed}.json
```

Example: `study_001__mistralai_mistral-nemo__n123__seed42.json`

## OpenRouter support

HumanStudyBench supports [OpenRouter](https://openrouter.ai/) with `mistralai/mistral-nemo` as a sensible default. Switch models by changing `--model`.

Examples:

```bash
python run_full_benchmark.py --real-llm --model anthropic/claude-3-sonnet --use-cache
python run_full_benchmark.py --real-llm --model meta-llama/llama-3-70b-instruct --use-cache
```

See `docs/openrouter_guide.md` for details.

## Project structure

```
HS_bench/
├── data/
│   ├── registry.json          # Study registry
│   ├── schemas/               # JSON schemas for studies
│   └── studies/
│       └── study_003/         # Framing Effect (Tversky & Kahneman, 1981)
├── src/
│   ├── agents/                # LLM participant agents & prompt builder
│   ├── core/                  # Benchmark orchestration & study base
│   ├── evaluation/            # Scoring, metrics, TOST framework
│   │   ├── scorer.py          # Main evaluation logic
│   │   ├── standardizers.py  # Data standardization (Freeman-Tukey, Cohen's d)
│   │   ├── tost.py            # TOST equivalence testing
│   │   └── metrics.py         # Statistical metrics
│   └── studies/               # Study-specific configs
├── docs/                      # Documentation
├── examples/                  # Example scripts
├── tests/                     # Test suite
├── results/cache/             # Cached experiment runs
├── run_full_benchmark.py      # Experiment runner
├── evaluate_results.py        # Standalone evaluator (no API calls)
└── test_tost_framework.py     # TOST framework validation
```

## Current studies

### Study 003 — Framing Effect (Tversky & Kahneman, 1981)

**Domain:** Behavioral Economics | **Design:** Between-subjects (positive vs. negative frame) | **N:** 152 (76 per condition)

**Original Finding:** Choice preferences reverse based on framing—72% risk-averse in gain frame, 78% risk-seeking in loss frame (χ²(1) = 41.7, p < 0.001; Cohen's h = 1.092).

**Validation:**

**Phenomena Tests (Critical):**
- P1: Effect presence — χ² test, p < 0.05 required
- P2: Effect direction — Positive frame > Negative frame for certain option

**Data Replication Tests (TOST, δ = 0.2):**
- D1: Positive frame proportion (Freeman-Tukey standardization)
- D2: Negative frame proportion (Freeman-Tukey standardization)
- D3: Effect size magnitude (Direct comparison)

Full specification: `data/studies/study_003/ground_truth.json`

## Evaluation Framework

### Phenomena Validation (Critical Tests)

**Purpose:** Verify psychological phenomena exist in agent behavior using original paper's statistical methods.

- **Method:** Replicate exact tests from published studies (χ², t-test, ANOVA, etc.)
- **Criterion:** Same significance thresholds (typically p < 0.05)
- **Status:** CRITICAL — All phenomena tests must pass for study to pass
- **Question:** "Does the agent exhibit the phenomenon?"

**Example (Study 003):**
```python
# P1: Effect presence
# Original: χ²(1) = 41.7, p < 0.001
# Agent must show: p < 0.05 ✓

# Test P2: Effect direction  
# P2: Effect direction
# Original: Positive (72%) > Negative (22%)
# Agent must show: Same direction ✓
```

**Outcome:** Phenomena test failure → Study fails (phenomenon not replicated)

---

### Data Replication (TOST Equivalence Testing)

**Purpose:** Quantify behavioral fidelity to human baselines.

- **Method:** TOST (Two One-Sided Tests) with standardized effect sizes
- **Status:** NON-CRITICAL — Improves score, not required for study pass
- **Question:** "How similar are agent data to human data?"

**Framework:**
```
H₀: |standardized effect| ≥ δ  (NOT equivalent)
H₁: |standardized effect| < δ  (equivalent)

Test via TOST → p-value
Scoring: Reliability Score = 1 - p_TOST
```

**Why equivalence testing?** Traditional testing asks "Is there a difference?" (wrong question for replication). Equivalence testing asks "Is the difference negligible?" (correct question).

**Parameters:**
- **δ = 0.2** (Cohen's "negligible" threshold) — applied uniformly after standardization
- **Standardization:** Freeman-Tukey (proportions), Cohen's d (means), direct comparison (effect sizes)

| Data Type | Study Provides | Standardization | Standardized Effect |
|-----------|----------------|-----------------|---------------------|
| **Proportions** | % choosing option | Freeman-Tukey: θ = arcsin(√p) | d = \|θ_agent - θ_human\| / SE_pooled |
| **Ratings** | Mean ratings + SD | Cohen's d | d = \|M_agent - M_human\| / SD_pooled |
| **Effect sizes** | Reported effect + SE | Direct comparison | d = \|ES_agent - ES_human\| / SE_combined |

**Example (Study 003):**
```python
# D1: Positive frame — Human 72%, Agent 70%
# Freeman-Tukey: θ_human = 1.054, θ_agent = 1.024
# d = 0.505 → p_TOST = 1.00 → Score = 0.00 (difference too large)

# D2: Negative frame — Human 22%, Agent 25%  
# d = 0.312 → p_TOST = 0.80 → Score = 0.20 (moderate difference)

# D3: Effect size — Human h=1.092, Agent h=1.00
# d = 0.434 → p_TOST = 0.50 → Score = 0.50 (borderline)
```

**Interpretation:** p < 0.05 (or Score ≥ 0.50) → Can claim equivalence

---

### Statistical Methods

**Phenomena Tests:** Use original paper's methods (χ², t-test, ANOVA, etc.) with same thresholds.

**Data Replication:** TOST equivalence testing

**Formula**: 
```
t_upper = (d - δ) / SE
t_lower = (-d - δ) / SE

p_upper = CDF_t(t_upper, df)
p_lower = CDF_t(t_lower, df)

p_tost = max(p_upper, p_lower)
```

**Interpretation Guidelines**:
- **p < 0.001**: Very strong evidence of equivalence
- **p < 0.01**: Strong evidence of equivalence
- **p < 0.05**: Moderate evidence (statistically significant equivalence)
- **p < 0.10**: Weak evidence
- **p ≥ 0.10**: Insufficient evidence of equivalence

**Example**: Testing proportion equivalence
```python
from src.evaluation.tost import tost_from_proportions

# Agent: 70% (n=100), Human: 72% (n=76)
result = tost_from_proportions(
    p1=0.70, n1=100,
    p2=0.72, n2=76,
    delta=0.2
)

print(f"p_tost = {result['p_tost']:.4f}")
print(f"Interpretation: {result['interpretation']}")
print(f"Score: {1 - result['p_tost']:.3f}")

# Output:
# p_tost = 1.0000
# Interpretation: Insufficient evidence of equivalence
# Score: 0.000
```

### Scoring & Pass Criteria

**Study-Level:**
```
Score = Σ(test_score × weight) / Σ(weight)
Pass if: (1) All phenomena tests pass AND (2) Score ≥ 70%
```

**Example (Study 003, total weight = 6.5):**

| Test | Type | Weight | Score | Weighted |
|------|------|--------|-------|----------|
| P1: Effect presence | Phenomena | 2.0 | 1.0 | 2.0 |
| P2: Effect direction | Phenomena | 2.0 | 1.0 | 2.0 |
| D1: Positive frame | Data | 1.0 | 0.98 | 0.98 |
| D2: Negative frame | Data | 1.0 | 0.97 | 0.97 |
| D3: Effect size | Data | 0.5 | 0.91 | 0.46 |
| **Total** | | **6.5** | | **6.41 → 98.5%** |

**Outcome:** ✅ Pass (phenomena validated + high fidelity score)

**Benchmark-Level:**
```
Pass if: (1) Average score ≥ 60% AND (2) Pass rate ≥ 50%
```

**Key Insight:** Phenomena validation ensures scientific validity (effect exists). Data replication quantifies behavioral fidelity (how human-like). An agent can show the phenomenon but with different magnitudes—TOST quantifies this difference.

---

### Rationale

**Why distinguish phenomena validation from data replication?**

Traditional hypothesis testing asks "Is there a difference?" This is wrong for replication—we want to prove similarity, not difference. Equivalence testing (TOST) asks "Is the difference negligible?" and can formally claim behavioral equivalence when p < 0.05.

**Why two validation tiers?** An agent may exhibit a phenomenon (e.g., framing effect exists) but with different magnitudes than humans (e.g., 60% vs 72% choosing safe option). Phenomena validation ensures scientific validity (binary: effect present or absent). Data replication quantifies fidelity (continuous: how human-like). Both matter for faithful replication.

**References:**
- Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.). Erlbaum.
- Lakens, D., et al. (2018). Equivalence Testing for Psychological Research. *Advances in Methods and Practices in Psychological Science*, 1(2), 259-269.

## Troubleshooting

- Timeouts or rate limits: lower `--num-workers`, or try a faster/cheaper model.
- Cache issues: omit `--use-cache` for a fresh run, or remove specific files in `results/cache`.

## Documentation

- Quick Start: `docs/QUICKSTART.md`
- API Reference: `docs/api_reference.md`

## Contributing

Issues and PRs are welcome. See `docs/QUICKSTART.md` for adding new studies.

## Citation

```bibtex
@misc{humanstudybench2025,
  title={HumanStudyBench: A Benchmark for Evaluating AI Agents on Human Study Replication},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/HS_bench}
}
```

