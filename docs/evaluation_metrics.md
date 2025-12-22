# Evaluation Metrics

This document describes how agent performance is evaluated in HumanStudyBench.

## Overview

Evaluation in HumanStudyBench follows a **unit test paradigm**: each study is a test, and passing requires matching the original study's outcomes within acceptable tolerances.

## Scoring Framework

### Three-Level Hierarchy

```
Overall Benchmark Score
    ├── Study-Level Scores
    │   ├── Test 1: Statistical Significance
    │   ├── Test 2: Effect Direction
    │   ├── Test 3: Effect Size Range
    │   └── Test 4: Descriptive Similarity
```

### Overall Score

**Formula**: Average of all study-level scores

```python
overall_score = sum(study_scores) / n_studies
```

**Interpretation**:
- 1.0 (100%): Perfect replication of all studies
- 0.75-1.0: Excellent performance
- 0.50-0.75: Good performance
- 0.25-0.50: Poor performance
- 0.0-0.25: Failure to replicate

### Study-Level Score

**Formula**: Weighted average of test scores

```python
study_score = sum(test_score_i * weight_i) / sum(weights)
```

**Pass Criteria**: Study score ≥ 0.75 (configurable)

## Test Types

### 1. Statistical Significance Test

**Purpose**: Check if the key statistical test is significant

**Implementation**:
```python
def test_statistical_significance(agent_results, ground_truth, alpha=0.05):
    agent_p = agent_results['inferential_statistics']['p_value']
    original_p = ground_truth['original_results']['inferential_statistics']['p_value']
    
    # Both should be significant or both non-significant
    agent_sig = agent_p < alpha
    original_sig = original_p < alpha
    
    if agent_sig == original_sig:
        return 1.0  # PASS
    else:
        return 0.0  # FAIL
```

**Example**:
- Original: p = 0.001 (significant)
- Agent: p = 0.003 (significant)
- Result: PASS ✓

**Weight**: 1.0 (critical test)

### 2. Effect Direction Test

**Purpose**: Check if the effect is in the correct direction

**Implementation**:
```python
def test_effect_direction(agent_results, ground_truth):
    agent_means = agent_results['descriptive_statistics']
    original_means = ground_truth['original_results']['descriptive_statistics']
    
    # Check if ranking matches
    agent_ranking = rank_conditions(agent_means)
    original_ranking = rank_conditions(original_means)
    
    if agent_ranking == original_ranking:
        return 1.0  # PASS
    else:
        return 0.0  # FAIL
```

**Example**:
- Original: M_incongruent (750ms) > M_congruent (550ms)
- Agent: M_incongruent (780ms) > M_congruent (520ms)
- Result: PASS ✓

**Weight**: 1.0 (critical test)

### 3. Effect Size Range Test

**Purpose**: Check if effect size is in expected range

**Implementation**:
```python
def test_effect_size_range(agent_results, ground_truth, tolerance=0.5):
    agent_d = agent_results['inferential_statistics']['cohens_d']
    original_d = ground_truth['original_results']['inferential_statistics']['cohens_d']
    
    min_d = original_d - tolerance
    max_d = original_d + tolerance
    
    if min_d <= agent_d <= max_d:
        return 1.0  # PASS
    else:
        # Partial credit for being close
        distance = min(abs(agent_d - min_d), abs(agent_d - max_d))
        return max(0, 1 - distance / tolerance)
```

**Example**:
- Original: d = 1.85, range = [1.35, 2.35]
- Agent: d = 1.92
- Result: PASS ✓ (within range)

**Weight**: 1.0

### 4. Descriptive Similarity Test

**Purpose**: Check if means and SDs are similar to original

**Implementation**:
```python
def test_descriptive_similarity(agent_results, ground_truth, tolerance=0.20):
    scores = []
    
    for condition in ground_truth['original_results']['descriptive_statistics']:
        original = ground_truth['original_results']['descriptive_statistics'][condition]
        agent = agent_results['descriptive_statistics'][condition]
        
        # Relative error for mean
        mean_error = abs(agent['mean'] - original['mean']) / original['mean']
        mean_score = max(0, 1 - mean_error / tolerance)
        
        # Relative error for SD
        sd_error = abs(agent['sd'] - original['sd']) / original['sd']
        sd_score = max(0, 1 - sd_error / tolerance)
        
        scores.append((mean_score + sd_score) / 2)
    
    return sum(scores) / len(scores)
```

**Example**:
- Original: M = 550, SD = 80
- Agent: M = 570, SD = 75
- Mean error: 3.6% → score = 0.82
- SD error: 6.25% → score = 0.69
- Result: 0.75 (partial credit)

**Weight**: 1.0

## Aggregation Methods

### Method 1: Weighted Average (Default)

```python
study_score = (
    w1 * significance_score +
    w2 * direction_score +
    w3 * effect_size_score +
    w4 * descriptive_score
) / (w1 + w2 + w3 + w4)
```

**Use when**: All tests are important

### Method 2: Conjunctive (All Must Pass)

```python
if all([test1_pass, test2_pass, test3_pass, test4_pass]):
    study_score = 1.0
else:
    study_score = 0.0
```

**Use when**: Strict replication required

### Method 3: Hierarchical (Critical Tests First)

```python
if not significance_pass or not direction_pass:
    study_score = 0.0
else:
    study_score = (effect_size_score + descriptive_score) / 2
```

**Use when**: Some tests are prerequisites

## Statistical Validation

### Handling Sampling Variability

Original studies have sampling variability. We account for this using:

#### 1. Tolerance Bands

```python
# Effect size tolerance based on sample size
def get_effect_size_tolerance(n):
    if n < 50:
        return 0.8  # Wide tolerance
    elif n < 100:
        return 0.5
    else:
        return 0.3  # Narrow tolerance
```

#### 2. Confidence Intervals

```python
# Check if agent CI overlaps with original CI
def test_ci_overlap(agent_ci, original_ci):
    return intervals_overlap(agent_ci, original_ci)
```

#### 3. Equivalence Testing

```python
# TOST (Two One-Sided Tests) for equivalence
def test_equivalence(agent_mean, original_mean, original_se, delta=0.5):
    # Test if difference is within [-delta*SD, +delta*SD]
    pass
```

### Multiple Comparisons

When studies have multiple hypotheses:

```python
# Bonferroni correction
adjusted_alpha = alpha / n_comparisons

# Or: Only require primary hypothesis to replicate
primary_test_pass and (secondary_tests_ratio > 0.5)
```

## Advanced Metrics

### Replication Bayes Factor

Quantify evidence for/against replication:

```python
def compute_replication_bf(agent_results, ground_truth):
    """
    Computes Bayes Factor comparing:
    H1: Agent results = original results
    H0: Agent results ≠ original results
    """
    # Using method from Verhagen & Wagenmakers (2014)
    pass
```

**Interpretation**:
- BF > 10: Strong evidence for replication
- BF 3-10: Moderate evidence for replication
- BF 1-3: Weak evidence
- BF < 1: Evidence against replication

### Small Telescopes Approach

Account for original study's precision:

```python
def small_telescopes_test(agent_d, original_d, original_n):
    """
    Test if failure to replicate is due to lower power in original.
    See Simonsohn (2015).
    """
    pass
```

### Kullback-Leibler Divergence

For distribution comparisons:

```python
def compute_kl_divergence(agent_dist, original_dist):
    """
    Measure divergence between agent and original data distributions.
    Lower is better.
    """
    return kl_div(original_dist, agent_dist)
```

## Reporting

### Study Report

```json
{
  "study_id": "study_001",
  "study_title": "Stroop Effect",
  "overall_score": 0.875,
  "status": "PASS",
  "tests": {
    "statistical_significance": {"score": 1.0, "status": "PASS"},
    "effect_direction": {"score": 1.0, "status": "PASS"},
    "effect_size_range": {"score": 0.8, "status": "PARTIAL"},
    "descriptive_similarity": {"score": 0.75, "status": "PARTIAL"}
  },
  "details": {
    "agent_p": 0.003,
    "original_p": 0.001,
    "agent_d": 1.72,
    "original_d": 1.85
  }
}
```

### Benchmark Report

```json
{
  "benchmark_version": "0.1.0",
  "agent_name": "MyAgent",
  "timestamp": "2025-10-27T12:00:00Z",
  "overall_score": 0.72,
  "studies_passed": 15,
  "studies_failed": 5,
  "total_studies": 20,
  "by_domain": {
    "cognitive_psychology": {"score": 0.85, "n": 10},
    "social_psychology": {"score": 0.58, "n": 10}
  },
  "by_difficulty": {
    "easy": {"score": 0.92, "n": 5},
    "medium": {"score": 0.70, "n": 10},
    "hard": {"score": 0.55, "n": 5}
  }
}
```

## Best Practices

### For Benchmark Developers

1. **Set reasonable tolerances**: Account for sampling variability
2. **Use multiple tests**: Don't rely on single metric
3. **Document decisions**: Explain why thresholds were chosen
4. **Validate with simulations**: Test scoring with synthetic data

### For Agent Developers

1. **Check test definitions**: Understand what's being evaluated
2. **Run multiple times**: Average over several runs if stochastic
3. **Analyze failures**: Don't just optimize for score
4. **Report honestly**: Include negative results

### For Researchers

1. **Use appropriate statistics**: Match analysis to original study
2. **Consider context**: Scores don't tell whole story
3. **Examine patterns**: Look for systematic failures
4. **Replicate carefully**: Some effects may not replicate even with humans

## Limitations

### Current Limitations

- **Binary/continuous hybrid**: Mix of pass/fail and graded scores
- **Weight selection**: Somewhat arbitrary
- **Missing uncertainty**: Don't model original study's uncertainty fully
- **No meta-analysis**: Don't aggregate across similar studies

### Future Improvements

- Bayesian scoring system
- Adaptive thresholds based on original study quality
- Meta-analytic benchmarks (aggregate similar studies)
- Uncertainty quantification for scores

## References

1. Simonsohn, U. (2015). Small telescopes: Detectability and the evaluation of replication results.
2. Verhagen, J., & Wagenmakers, E. J. (2014). Bayesian tests to quantify the result of a replication attempt.
3. LeBel, E. P., et al. (2019). A unified framework to quantify the credibility of scientific findings.
4. Open Science Collaboration (2015). Estimating the reproducibility of psychological science.

## Questions?

For clarification on metrics:
- Open an issue on GitHub
- See `run_full_benchmark.py` and `evaluate_results.py` for usage examples
- Email the maintainers
