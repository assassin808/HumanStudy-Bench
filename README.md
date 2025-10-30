# HumanStudyBench

A benchmark framework for evaluating LLM agents on classic human behavioral studies.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

> A realistic, sustainable, and systematic benchmark for evaluating AI agents' ability to reproduce published human studies.

HumanStudyBench curates classic and contemporary peer‑reviewed studies with full experimental specifications (designs, participant profiles, measurement protocols, and reported results). Agents run under realistic constraints and are scored against literature‑reported outcomes.

---

## Statistical Framework for Data Replication

**Goal:** Assess whether LLM agents can reliably replicate human behavioral data across social science studies.

**Challenge:** Studies provide varying data granularity—some report only summary statistics, others provide full distributions. We need a **unified evaluation standard** with **statistical rigor**.

### Core Hypothesis

- **H₀ (Null):** LLM **cannot** effectively replicate human data (|standardized effect| ≥ δ)
- **H₁ (Alternative):** LLM **can** effectively replicate human data (|standardized effect| < δ)

### Unified Evaluation Approach

**Single Global Parameter:**
- **δ = 0.2** (standardized units) — equivalence margin for all tests
- All metrics (proportions, ratings, effect sizes) are **standardized** (Fisher Z, Cohen's d, Freeman-Tukey) before testing
- Same δ applies across all studies, regardless of data granularity

**Equivalence Testing (TOST):**
```
For each measurable statistic:
  1. Standardize: Convert to common scale (Fisher Z, Cohen's d, etc.)
  2. Test: H₀: |d| ≥ δ  vs  H₁: |d| < δ
  3. Output: p-value (lower = stronger equivalence)
```

**Scoring:**
- **Reliability Score** = 1 - p_value
- p < 0.05 → Can claim equivalence (statistically significant replication)
- Score ≥ 0.50 → Practical equivalence threshold

This framework ensures **fair comparison** across studies with different data availability while maintaining **statistical rigor**.

---

## Features

- 🧪 Curated studies across domains (e.g., Asch conformity)
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
├── data/                      # Study registry, schemas, and studies
│   └── studies/
│       └── study_001/         # Asch conformity (1952)
├── src/
│   ├── agents/                # LLM participant agents & prompt builder
│   ├── core/                  # Benchmark orchestration & study base
│   ├── evaluation/            # Scoring and metrics
│   └── studies/               # Study-specific configs
├── results/
│   └── cache/                 # Cached runs
├── run_full_benchmark.py      # Experiment runner
├── evaluate_results.py        # Standalone evaluator (no API calls)
└── README.md
```

## Current studies

### Study 003 — Framing Effect (Tversky & Kahneman, 1981)

- **Domain**: Behavioral Economics / Decision Making
- **Design**: Between-subjects manipulation of decision frame (positive vs. negative)
- **Key finding**: Choice preferences reverse based on framing (72% risk-averse in gain frame, 78% risk-seeking in loss frame)
- **Original result**: χ²(1) = 41.7, p < 0.001; effect size h = 1.092

**Validation criteria**: Two-tier evaluation system with TOST equivalence testing

**Type 1: Phenomenon-level Match** (Critical tests - must pass)
- P1: Framing effect presence (chi-square test, p < 0.05)
- P2: Framing effect direction (positive frame > negative frame for certain option)

**Type 2: Data-level Match** (TOST equivalence testing with δ = 0.2)
- D1: Positive frame data match (Freeman-Tukey TOST, p_tost < 0.05 for equivalence)
- D2: Negative frame data match (Freeman-Tukey TOST, p_tost < 0.05 for equivalence)
- D3: Effect size magnitude match (Direct comparison TOST, p_tost < 0.05 for equivalence)

**Equivalence margin**: δ = 0.2 (standardized units, Cohen's "negligible" threshold)

Full description: `data/studies/study_003/ground_truth.json`

## Evaluation & pass criteria

HumanStudyBench uses a **two-tier evaluation framework** to assess both psychological validity and behavioral fidelity. Each study contains **two types of independent tests**:

### Two Types of Tests

#### Type 1: Phenomenon-Level Tests (Critical)

**Purpose:** Verify the **psychological phenomenon** is present in agent behavior.

These tests use the **exact same statistical methods** as the original paper to confirm the cognitive/behavioral effect exists.

- **Method**: Original study's tests (chi-square, t-test, ANOVA, etc.)
- **Criterion**: Same threshold as original paper (typically p < 0.05)
- **Status**: **CRITICAL** — Must pass all Type 1 tests for study to pass
- **Question asked**: "Does the agent show the phenomenon?"

**Example (Study 003 - Framing Effect):**
```python
# Test P1: Effect presence
# Original paper: χ²(1) = 41.7, p < 0.001
# Agent requirement: χ² test shows p < 0.05 ✓

# Test P2: Effect direction  
# Original paper: Positive frame (72%) > Negative frame (22%)
# Agent requirement: Same direction (positive > negative) ✓
```

If agent fails Type 1 tests → **Phenomenon not replicated** → Study fails

---

#### Type 2: Data-Level Tests (Equivalence Testing)

**Purpose:** Quantify how **closely agent data matches human baseline**.

These tests use **equivalence testing** to assess whether agent behavior is statistically indistinguishable from human behavior.

- **Method**: TOST (Two One-Sided Tests) with standardized effect sizes
- **Status**: **NON-CRITICAL** — Improves score but not required to pass
- **Question asked**: "How similar is the agent to humans?"

**Statistical Framework:**

```
H₀ (null):        |standardized effect| ≥ δ  (NOT equivalent)
H₁ (alternative): |standardized effect| < δ  (equivalent)

Output: p-value (lower p → stronger evidence of equivalence)
Scoring: Reliability Score = 1 - p_tost
```

**Why Equivalence Testing (not traditional hypothesis testing)?**

| Approach | Question | Suitable for Replication? |
|----------|----------|---------------------------|
| Traditional testing | "Is there a difference?" (H₀: d = 0) | ❌ No — We want similarity, not difference |
| **Equivalence testing** | **"Is the difference negligible?"** (H₁: \|d\| < δ) | ✅ Yes — Directly tests similarity |

**Single Global Parameter:** δ = 0.2 (standardized units)
- Applied uniformly across **all** data-level tests after standardization
- Based on Cohen (1988): threshold for "negligible" effects
- Ensures fair comparison across studies with varying data granularity

**Standardization Methods** (converts different metrics to common scale):

| Data Type | Study Provides | Standardization | Standardized Effect |
|-----------|----------------|-----------------|---------------------|
| **Proportions** | % choosing option | Freeman-Tukey: θ = arcsin(√p) | d = \|θ_agent - θ_human\| / SE_pooled |
| **Ratings** | Mean ratings + SD | Cohen's d | d = \|M_agent - M_human\| / SD_pooled |
| **Effect sizes** | Reported effect + SE | Direct comparison | d = \|ES_agent - ES_human\| / SE_combined |

**Example (Study 003 - Framing Effect):**
```python
# Test D1: Positive frame data match
# Human baseline: 72% (n=76)
# Agent: 70% (n=100)

# Step 1: Standardize using Freeman-Tukey
theta_human = arcsin(√0.72) = 1.054
theta_agent = arcsin(√0.70) = 1.024
d = |1.054 - 1.024| / SE_pooled = 0.505

# Step 2: Equivalence test
# Is 0.505 < 0.2? No → Cannot claim equivalence
# p_tost = 0.9+ → Reliability Score ≈ 0.00

# Test D2: Negative frame data match
# Human: 22% (n=76), Agent: 25% (n=100)
# d = 0.312 → p_tost ≈ 0.80 → Score ≈ 0.20

# Test D3: Effect size match
# Human effect: h = 1.092, Agent effect: h = 1.00
# d = 0.434 → p_tost ≈ 0.50 → Score ≈ 0.50
```

**Interpretation:**
- **p < 0.05**: Can claim statistical equivalence ✓
- **Score ≥ 0.50**: Practical equivalence threshold ✓
- **Pass if**: p < 0.05 OR score ≥ 0.50

**Example (Study 003):**
```python
# Test D1: Positive frame data match
# Human baseline: 72% (n=76)
# Agent: 70% (n=100)

# Freeman-Tukey transformation
theta_human = arcsin(√0.72) = 1.0539
theta_agent = arcsin(√0.70) = 1.0239
SE_pooled = 0.0594

# Standardized difference
d = |1.0539 - 1.0239| / 0.0594 = 0.505

# TOST with δ = 0.2
t_upper = (0.505 - 0.2) / 0.0594 = 5.14
t_lower = (-0.505 - 0.2) / 0.0594 = -11.87
p_upper = 1.0000  # Above threshold
p_lower = 0.0000  # Well below threshold
p_tost = max(1.0000, 0.0000) = 1.0000

# Result: Cannot claim equivalence (difference too large)
score = 1 - 1.0000 = 0.00
interpretation = "Insufficient evidence of equivalence"
```

### Statistical Methods Summary

#### For Type 1 Tests (Phenomenon-Level)

Uses **original paper's statistical methods** exactly as reported:

| Test | Used For | Example |
|------|----------|---------|
| **Chi-Square (χ²)** | Categorical data | Testing if choice frequencies differ across conditions |
| **t-test** | Continuous data | Comparing mean ratings between groups |
| **ANOVA** | Multiple groups | Testing differences across 3+ conditions |

**Example - Chi-Square Test:**
```
Study 003: Does framing affect choices?

Contingency table:
                Program A   Program B
Positive frame     72          28
Negative frame     22          78

χ²(1) = 41.7, p < 0.001 → ✓ Significant framing effect (Type 1 test passes)
```

#### For Type 2 Tests (Data-Level)

Uses **TOST equivalence testing** to test if differences are negligible:

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

### Study-Level Scoring

**Formula**: 
```
Total Score = Σ(test_score × test_weight) / Σ(test_weight)
```

**Pass Requirements** (both must be satisfied):
1. ✅ All critical tests pass (all phenomenon-level tests)
2. ✅ Overall score ≥ 70%

**Grading Scale**:

| Overall Score | Grade | Status |
|---|---|---|
| ≥ 90% | Perfect/Excellent | ✅ Pass |
| ≥ 80% | Good | ✅ Pass |
| ≥ 70% | Pass | ✅ Pass |
| < 70% | Fail | ❌ Fail |

**Example Scoring** (Study 003 with TOST, total weight = 6.5):

| Test | Type | Weight | p_tost | Score | Contribution | Interpretation |
|---|---|---|---|---|---|---|
| P1: Effect presence (χ²) | Phenomenon | 2.0 | 0.001 | 1.0 | 2.0 | Significant effect |
| P2: Effect direction | Phenomenon | 2.0 | N/A | 1.0 | 2.0 | Correct direction |
| D1: Positive frame (72%) | Data (TOST) | 1.0 | 0.018 | 0.982 | 0.982 | Strong equivalence |
| D2: Negative frame (22%) | Data (TOST) | 1.0 | 0.035 | 0.965 | 0.965 | Moderate equivalence |
| D3: Effect size (h=1.092) | Data (TOST) | 0.5 | 0.089 | 0.911 | 0.456 | Weak equivalence |
| **Total** | | **6.5** | | | **6.40 / 6.5 = 98.5%** | |

Result: ✅ Pass (all critical tests passed + 98.5% ≥ 70%)

**TOST Details for Data-Level Tests**:

```python
# D1: Positive frame
# Agent: 72.0% (n=100), Human: 72.0% (n=76)
# Freeman-Tukey: d = 0.003, p_tost = 0.018
# → Strong evidence of equivalence (score = 0.982)

# D2: Negative frame
# Agent: 23.0% (n=100), Human: 22.0% (n=76)
# Freeman-Tukey: d = 0.015, p_tost = 0.035
# → Moderate evidence of equivalence (score = 0.965)

# D3: Effect size magnitude
# Agent: h = 1.15, Human: h = 1.092 (SE = 0.15)
# Direct comparison: d = 0.387, p_tost = 0.089
# → Weak evidence of equivalence (score = 0.911)
```

**Key Insights**:
1. Agent successfully replicates the phenomenon (P1 ✓, P2 ✓)
2. Individual condition data closely matches human baseline (D1, D2)
3. Overall effect size slightly larger than human study (D3)
4. High total score (98.5%) indicates excellent behavioral fidelity

### Benchmark-Level Pass Criteria

**Requirements** (both must be satisfied):
1. Average score across all studies ≥ 60%
2. Pass rate ≥ 50% (at least half of studies pass)

**Example**:
```
Study 003: 96.9% ✅ Pass
Study 004: 45.2% ❌ Fail  
Study 005: 78.3% ✅ Pass

Average: (96.9 + 45.2 + 78.3) / 3 = 73.5% ✅
Pass rate: 2/3 = 66.7% ✅

Benchmark result: ✅ PASS
```

### Rationale: Why Two Tiers?

**Phenomenon-level tests** (Type 1) ensure scientific validity:
- Core question: "Does the agent show the psychological effect?"
- Uses original statistical methods (chi-square, t-test, etc.)
- Binary outcome: effect present or absent
- Critical for replication validity

**Data-level tests** (Type 2) quantify behavioral fidelity:
- Core question: "How similar is agent data to human data?"
- Uses **TOST equivalence testing** with standardized effect sizes
- Graded outcome: p-values directly measure strength of equivalence
- Rewards high-fidelity simulation beyond phenomenon presence

**Why TOST for data-level tests?**

Traditional hypothesis testing is designed to detect differences, not similarities:
- H₀: "no difference" → reject if p < 0.05 → "there IS a difference"
- Problem: Cannot prove similarity (only absence of detected difference)
- Inappropriate for replication: we want to show agent ≈ human, not agent ≠ human

TOST equivalence testing is designed to test similarity:
- H₀: "large difference" → reject if p < 0.05 → "difference is negligible"
- Solution: Directly tests if |difference| < tolerance threshold
- Appropriate for replication: can formally claim behavioral equivalence

**Key insight**: An agent can show the phenomenon (pass Type 1) but with different magnitudes than humans. Type 2 with TOST quantifies this difference and tests if it's small enough to be considered equivalent.

**References**:
- Cohen, J. (1988). *Statistical Power Analysis for the Behavioral Sciences* (2nd ed.). Erlbaum.
- Lakens, D., et al. (2018). Equivalence Testing for Psychological Research: A Tutorial. *Advances in Methods and Practices in Psychological Science*, 1(2), 259-269.

## Troubleshooting

- Timeouts or rate limits: lower `--num-workers`, or try a faster/cheaper model.
- Cache issues: omit `--use-cache` for a fresh run, or remove specific files in `results/cache`.

## Documentation

- Getting started: `docs/getting_started.md`
- Agent guide: `docs/llm_participant_agent_guide.md`
- Prompt builder: `docs/prompt_builder_guide.md`
- OpenRouter: `docs/openrouter_guide.md`
- Benchmark overview: `docs/benchmark_overview.md`
- Evaluation metrics: `docs/evaluation_metrics.md`
- **Two-tier evaluation framework**: `docs/TWO_TIER_EVALUATION_FRAMEWORK.md`

## Contributing

Issues and PRs are welcome. See `docs/paper_curation_guide.md` for adding new studies.

## Citation

```bibtex
@misc{humanstudybench2025,
  title={HumanStudyBench: A Benchmark for Evaluating AI Agents on Human Study Replication},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/HS_bench}
}
```

