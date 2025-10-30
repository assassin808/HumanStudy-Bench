# Two-Tier Evaluation Framework

**Version**: 2.0  
**Date**: October 28, 2024  
**Status**: Implemented

## Overview

HumanStudyBench uses a sophisticated **two-tier evaluation framework** to assess LLM agents on both psychological validity and behavioral fidelity. This framework evolved from the insight that showing a psychological phenomenon and perfectly matching human data are distinct goals that require different statistical approaches.

## Framework Philosophy

### The Core Question

When evaluating whether an LLM agent "replicates" a human study, we face two distinct questions:

1. **Does the agent show the psychological phenomenon?** (Validity)
   - Example: Does the agent exhibit framing effects?
   - Answer: Use original paper's statistical tests (p-values)
   
2. **How similar is the agent's data to human data?** (Fidelity)
   - Example: How close are agent proportions to human baselines?
   - Answer: Use effect size metrics (Cohen's h, Cohen's d)

### Why Two Tiers?

**Critical Insight**: An agent can exhibit a phenomenon (e.g., "framing affects choices") without perfectly matching human magnitudes (e.g., 68% vs 72%).

- **Type 1 (Phenomenon-level)** captures the qualitative cognitive feature
- **Type 2 (Data-level)** captures the quantitative behavioral similarity

**Example**: Study 003 (Framing Effect)

| Agent Type | Positive Frame | Negative Frame | Phenomenon? | Data Match? |
|---|---|---|---|---|
| Human baseline | 72% certain | 22% certain | Yes (χ²=41.7) | Perfect |
| Good agent | 70% certain | 25% certain | Yes (χ²=40.5) | Excellent (h<0.20) |
| Weak agent | 55% certain | 45% certain | Yes (χ²=8.2) | Poor (h>0.50) |
| No effect agent | 50% certain | 50% certain | No (χ²=0.0) | N/A |

Good agent: ✅ Shows phenomenon + excellent data match → 96.9% score  
Weak agent: ✅ Shows phenomenon + poor data match → 88.5% score (still passes!)  
No effect agent: ❌ No phenomenon → 38.5% score (fails regardless of other metrics)

## Type 1: Phenomenon-Level Match (Critical)

### Purpose
Verify that the agent exhibits the psychological/cognitive phenomenon described in the original paper.

### Methods
- **Statistical tests**: Chi-square, t-test, ANOVA, etc.
- **Criterion**: p-value < α (typically 0.05)
- **Rationale**: Uses the **same statistical method as the original paper**

### Implementation

**Test Structure** (in `ground_truth.json`):
```json
{
  "test_id": "P1",
  "test_type": "phenomenon_level",
  "description": "Framing effect presence",
  "critical": true,
  "weight": 2.0,
  "method": {
    "test": "chi_square",
    "threshold": 0.05
  },
  "human_baseline": {
    "chi_square": 41.7,
    "p_value": 0.0001,
    "degrees_of_freedom": 1
  }
}
```

**Scoring**:
- Score = 1.0 if p < α (effect present)
- Score = 0.0 if p ≥ α (no effect)

### Study 003 Example

**P1: Framing Effect Presence**
- Method: χ² test on 2×2 contingency table
- Original: χ²(1) = 41.7, p < 0.001
- Agent requirement: χ² test with p < 0.05
- Interpretation: Does frame manipulation affect choices?

**P2: Framing Effect Direction**
- Method: Proportion difference test
- Original: Positive frame (72%) > Negative frame (22%)
- Agent requirement: Positive proportion > Negative proportion
- Interpretation: Is the effect in the correct direction?

## Type 2: Data-Level Match (Bonus)

### Purpose
Quantify how closely the agent's behavioral data matches the human baseline distribution.

### Methods
- **Effect size metrics**: Cohen's h (proportions), Cohen's d (means)
- **Criterion**: Graded scoring based on effect size thresholds
- **Rationale**: Effect sizes quantify **magnitude of difference** between distributions

### Cohen's h for Proportions

**Formula**:
```
h = 2 × (arcsin(√p₁) - arcsin(√p₂))
```

**Interpretation** (Cohen, 1988):
- h < 0.20: Small (negligible difference)
- h < 0.50: Medium (small difference)
- h < 0.80: Large (medium difference)
- h ≥ 0.80: Very large (large difference)

**Scoring Thresholds**:
```python
if h < 0.20:
    score = 1.0  # Excellent match
    quality = "excellent"
elif h < 0.50:
    score = 0.9  # Good match
    quality = "good"
elif h < 0.80:
    score = 0.8  # Acceptable match
    quality = "acceptable"
else:
    score = 0.7  # Poor match
    quality = "poor"
```

### Implementation

**Test Structure** (in `ground_truth.json`):
```json
{
  "test_id": "D1",
  "test_type": "data_level",
  "description": "Positive frame data match",
  "critical": false,
  "weight": 1.0,
  "method": {
    "effect_size": "cohens_h",
    "condition": "positive_frame"
  },
  "human_baseline": {
    "proportion_choose_safe": 0.72
  },
  "thresholds": {
    "excellent": 0.20,
    "good": 0.50,
    "acceptable": 0.80
  }
}
```

**Scoring**:
- Graded scores from 0.7 to 1.0 based on Cohen's h
- NOT binary (unlike phenomenon-level tests)
- Rewards high-fidelity simulation

### Study 003 Example

**D1: Positive Frame Data Match**
- Human baseline: 72% choose certain option
- Agent: 70% choose certain option
- Cohen's h = 0.044
- Score: 1.0 (excellent match)

**D2: Negative Frame Data Match**
- Human baseline: 22% choose certain option
- Agent: 25% choose certain option
- Cohen's h = 0.071
- Score: 1.0 (excellent match)

**D3: Effect Size Magnitude Match**
- Human effect size: 0.72 - 0.22 = 0.50
- Agent effect size: 0.70 - 0.25 = 0.45
- Absolute difference: |0.50 - 0.45| = 0.05
- Score: 1.0 (excellent match, < 0.10 threshold)

## Scoring Integration

### Study-Level Scoring

**Formula**:
```
Total Score = Σ(test_score × test_weight) / Σ(test_weight)
```

**Pass Requirements** (both must be satisfied):
1. ✅ All critical tests pass (all phenomenon-level tests must score 1.0)
2. ✅ Overall score ≥ 70%

**Weight Distribution** (Study 003):
- Phenomenon-level: 4.0 (2 tests × 2.0 weight each)
- Data-level: 2.5 (2 tests × 1.0 + 1 test × 0.5)
- Total: 6.5

**Rationale**:
- Phenomenon tests weighted more (critical validity)
- Data tests provide bonus scoring (fidelity reward)
- Even with poor data match, can pass if phenomenon is present

### Example Calculations

**Scenario 1: Excellent Agent**
| Test | Type | Weight | Score | Contribution |
|---|---|---|---|---|
| P1 | Phenomenon | 2.0 | 1.0 | 2.0 |
| P2 | Phenomenon | 2.0 | 1.0 | 2.0 |
| D1 | Data | 1.0 | 1.0 | 1.0 |
| D2 | Data | 1.0 | 0.9 | 0.9 |
| D3 | Data | 0.5 | 0.8 | 0.4 |
| **Total** | | **6.5** | | **6.3** |

- Total score: 6.3 / 6.5 = **96.9%**
- Critical tests: ✅ All passed
- Result: ✅ **PASS** (Grade: Excellent)

**Scenario 2: Phenomenon Only Agent**
| Test | Type | Weight | Score | Contribution |
|---|---|---|---|---|
| P1 | Phenomenon | 2.0 | 1.0 | 2.0 |
| P2 | Phenomenon | 2.0 | 1.0 | 2.0 |
| D1 | Data | 1.0 | 0.7 | 0.7 |
| D2 | Data | 1.0 | 0.7 | 0.7 |
| D3 | Data | 0.5 | 0.7 | 0.35 |
| **Total** | | **6.5** | | **5.75** |

- Total score: 5.75 / 6.5 = **88.5%**
- Critical tests: ✅ All passed
- Result: ✅ **PASS** (Grade: Good)
- Note: Poor data match but still passes due to phenomenon presence

**Scenario 3: No Phenomenon Agent**
| Test | Type | Weight | Score | Contribution |
|---|---|---|---|---|
| P1 | Phenomenon | 2.0 | 0.0 | 0.0 |
| P2 | Phenomenon | 2.0 | 0.0 | 0.0 |
| D1 | Data | 1.0 | 1.0 | 1.0 |
| D2 | Data | 1.0 | 1.0 | 1.0 |
| D3 | Data | 0.5 | 1.0 | 0.5 |
| **Total** | | **6.5** | | **2.5** |

- Total score: 2.5 / 6.5 = **38.5%**
- Critical tests: ❌ Failed
- Result: ❌ **FAIL**
- Note: Perfect data match doesn't matter without phenomenon

### Grading Scale

| Overall Score | Grade | Status |
|---|---|---|
| ≥ 90% | Perfect/Excellent | ✅ Pass |
| ≥ 80% | Good | ✅ Pass |
| ≥ 70% | Pass | ✅ Pass |
| < 70% | Fail | ❌ Fail |

## Code Architecture

### Key Files

**1. `data/studies/study_003/ground_truth.json`**
- Defines all tests (P1, P2, D1, D2, D3)
- Specifies human baselines
- Sets thresholds and weights

**2. `src/evaluation/scorer.py`**
- `_run_phenomenon_test()`: Routes to chi-square, proportion tests
- `_run_data_level_test()`: Routes to Cohen's h, absolute difference
- `_test_chi_square()`: Implements P1 (effect presence)
- `_test_proportion_difference()`: Implements P2 (effect direction)
- `_test_cohens_h()`: Implements D1, D2 (data matching)
- `_calculate_cohens_h()`: Formula implementation

**3. `src/studies/study_003_config.py`**
- `aggregate_results()`: Calculates all metrics
- `_calculate_cohens_h()`: Helper for Cohen's h
- `_interpret_cohens_h()`: Interprets effect sizes

### Data Flow

```
Agent responses
    ↓
Study003Config.aggregate_results()
    → Calculates chi-square, proportions, Cohen's h
    ↓
Scorer.score_study()
    → Runs phenomenon tests (P1, P2)
    → Runs data-level tests (D1, D2, D3)
    ↓
Test results with scores
    → Weighted sum / total weight
    → Check critical tests
    ↓
Final score + Pass/Fail
```

## Statistical Foundations

### Chi-Square Test

**Purpose**: Test independence of two categorical variables

**Formula**: χ² = Σ[(O - E)² / E]

**Study 003 Application**:
```
Contingency Table:
                Program A   Program B
Positive frame     72          28
Negative frame     22          78

χ²(1) = 41.7, p < 0.001
Interpretation: Frame significantly affects choice
```

### Cohen's h

**Purpose**: Quantify difference between two proportions

**Formula**: h = 2 × (arcsin(√p₁) - arcsin(√p₂))

**Advantages over simple difference**:
- Accounts for variance (proportions near 0 or 1 have less variance)
- Standardized metric (comparable across studies)
- Well-established thresholds (Cohen, 1988)

**Study 003 Application**:
```python
# Human positive frame: 72%
# Agent positive frame: 70%
p1 = 0.72
p2 = 0.70

phi1 = 2 * np.arcsin(np.sqrt(p1))  # 2.0177
phi2 = 2 * np.arcsin(np.sqrt(p2))  # 1.9734

h = abs(phi1 - phi2)  # 0.044

# Interpretation: h = 0.044 < 0.20 → Excellent match
```

## Design Rationale

### Why Not Use p-values for Data Matching?

**Problem**: "Non-significant difference" (p ≥ 0.05) does NOT mean "similar"
- Absence of evidence ≠ evidence of absence
- Low power can cause false "similarity" claims

**Correct Approach**: Use effect sizes
- Cohen's h directly quantifies similarity
- Established thresholds for interpretation
- More informative than binary p-value

### Alternative: Equivalence Testing (TOST)

For true "statistically equivalent" claims, use **Two One-Sided Tests (TOST)**:
- Tests if difference is within equivalence bounds
- More rigorous but requires predefined equivalence region
- Future enhancement for HumanStudyBench

**Current approach (effect sizes) is simpler and sufficient** for graded scoring.

### Why "Phenomenon" vs "Data" Terminology?

**Rejected alternatives**:
- ~~"Behavior-level" vs "Data-level"~~: Ambiguous (both involve behavior)
- ~~"Effect-level" vs "Distribution-level"~~: Less intuitive
- ~~"Qualitative" vs "Quantitative"~~: Both use quantitative methods

**Chosen**: "Phenomenon-level" vs "Data-level"
- Clear distinction: presence vs similarity
- Aligns with cognitive science literature
- Intuitive for users

## References

1. **Cohen, J. (1988)**. Statistical Power Analysis for the Behavioral Sciences (2nd ed.). Erlbaum.
   - Established effect size thresholds (h: 0.20, 0.50, 0.80)

2. **Tversky, A., & Kahneman, D. (1981)**. The framing of decisions and the psychology of choice. Science, 211(4481), 453-458.
   - Original framing effect study (Study 003 baseline)

3. **Lakens, D. (2013)**. Calculating and reporting effect sizes to facilitate cumulative science. Frontiers in Psychology, 4, 863.
   - Modern best practices for effect size reporting

## Future Enhancements

1. **TOST for equivalence testing**
   - Statistically rigorous similarity claims
   - Requires defining equivalence bounds

2. **Additional effect sizes**
   - Cohen's d for continuous outcomes
   - Cramér's V for larger contingency tables
   - Cliff's delta for ordinal data

3. **Bayesian approaches**
   - Bayes factors for evidence quantification
   - Posterior distributions for uncertainty

4. **Cross-study meta-analysis**
   - Aggregate effect sizes across studies
   - Identify systematic agent biases

## Validation

Run the test suite to verify the framework:

```bash
python test_two_tier_evaluation.py
```

Expected output:
- ✅ Cohen's h calculations verified
- ✅ Phenomenon-level tests verified
- ✅ Data-level tests verified
- ✅ Integrated scoring verified

---

**Document Status**: Complete  
**Implementation Status**: Fully integrated into HumanStudyBench v2.0  
**Last Updated**: October 28, 2024
