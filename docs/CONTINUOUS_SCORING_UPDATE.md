# Continuous Scoring Update for Data-Level Tests

**Date**: October 29, 2024  
**Version**: 2.1  
**Status**: ✅ Implemented

## 🎯 Problem Addressed

### Previous System (v2.0)
Data-level tests used **discrete scoring tiers**:
- h < 0.20 → score = 1.0 (excellent)
- h < 0.50 → score = 0.9 (good)
- h < 0.80 → score = 0.8 (acceptable)
- h ≥ 0.80 → score = 0.7 (poor)

**Issues**:
1. ❌ Agent with h=0.79 gets 0.8, but h=0.81 gets 0.7 (cliff effect)
2. ❌ Agent with h=1.5 still gets 0.7 (no penalty for very large differences)
3. ❌ Doesn't reflect the continuous nature of Cohen's h

### New System (v2.1)
Data-level tests use **continuous linear scoring**:
```python
score = max(0, 1 - h / 0.8)
```

**Benefits**:
- ✅ Score decreases smoothly with increasing h
- ✅ h=0.8 → score=0.0 (true fail for large differences)
- ✅ Rewards similarity proportionally

---

## 📐 Scoring Function

### Formula
```python
# For Cohen's h
score = max(0.0, 1.0 - cohens_h / max_h)

# For absolute difference
score = max(0.0, 1.0 - abs_diff / max_diff)
```

### Parameters
- `max_h = 0.80` - Maximum acceptable Cohen's h (beyond this = 0 score)
- `max_diff = 0.30` - Maximum acceptable absolute difference

### Examples

| Cohen's h | Calculation | Score | Interpretation |
|---|---|---|---|
| 0.00 | max(0, 1 - 0.00/0.80) | **1.000** | Perfect match |
| 0.10 | max(0, 1 - 0.10/0.80) | **0.875** | Excellent |
| 0.20 | max(0, 1 - 0.20/0.80) | **0.750** | Good |
| 0.40 | max(0, 1 - 0.40/0.80) | **0.500** | Moderate |
| 0.60 | max(0, 1 - 0.60/0.80) | **0.250** | Poor |
| 0.80 | max(0, 1 - 0.80/0.80) | **0.000** | Fail |
| 1.00 | max(0, 1 - 1.00/0.80) | **0.000** | Fail |

---

## 📊 Visual Comparison

### Old Scoring (Discrete)
```
Score
1.0 |████████████████████████  h < 0.20
0.9 |           █████████████  0.20 ≤ h < 0.50
0.8 |                  ██████  0.50 ≤ h < 0.80
0.7 |                      ██  h ≥ 0.80
    +-------------------------
    0    0.2   0.4   0.6   0.8   1.0   Cohen's h
```

### New Scoring (Continuous)
```
Score
1.0 |██
    |  ██
    |    ██
0.8 |      ██
    |        ██
    |          ██
0.6 |            ██
    |              ██
    |                ██
0.4 |                  ██
    |                    ██
    |                      ██
0.2 |                        ██
    |                          ██
0.0 |                            ██████████
    +------------------------------------
    0    0.2   0.4   0.6   0.8   1.0   Cohen's h
```

---

## 🔄 Code Changes

### 1. `src/evaluation/scorer.py` - Cohen's h Test

**Before**:
```python
if cohens_h < excellent:
    score = 1.0
elif cohens_h < good:
    score = 0.9
elif cohens_h < acceptable:
    score = 0.8
else:
    score = 0.7
```

**After**:
```python
# Continuous scoring: score decreases linearly with Cohen's h
max_h = thresholds.get("acceptable", 0.80)
score = max(0.0, 1.0 - cohens_h / max_h)
```

### 2. `src/evaluation/scorer.py` - Absolute Difference Test

**Before**:
```python
if abs_diff < excellent:
    score = 1.0
elif abs_diff < good:
    score = 0.9
elif abs_diff < acceptable:
    score = 0.8
else:
    score = 0.7
```

**After**:
```python
# Continuous scoring: score decreases linearly with absolute difference
max_diff = thresholds.get("acceptable", 0.30)
score = max(0.0, 1.0 - abs_diff / max_diff)
```

### 3. `src/evaluation/scorer.py` - Separate Test Results

**Added**:
```python
# Separate phenomenon and data results
phenomenon_tests = {}  # P tests only
data_tests = {}        # D tests only

# ... in loop ...
if test_type == "phenomenon_level":
    phenomenon_tests[test_id] = test_result
    phenomenon_score += score * weight
    phenomenon_weight += weight
elif test_type == "data_level":
    data_tests[test_id] = test_result
    data_score += score * weight
    data_weight += weight

# Return includes:
return {
    ...
    "phenomenon_tests": phenomenon_tests,
    "data_tests": data_tests,
    "phenomenon_score": phenomenon_avg,
    "data_score": data_avg,
}
```

---

## 📈 Impact on Scoring

### Example Study 003 Results

#### Scenario A: Good Match
- Human: 72% positive, 22% negative
- Agent: 70% positive, 25% negative

| Test | h/diff | Old Score | New Score | Change |
|---|---|---|---|---|
| D1 (pos) | h=0.044 | 1.0 | 0.945 | -0.055 |
| D2 (neg) | h=0.071 | 1.0 | 0.912 | -0.088 |
| D3 (eff) | d=0.050 | 1.0 | 0.833 | -0.167 |
| **Weighted** | | **1.00** | **0.909** | **-0.091** |

**Impact**: Slightly lower but still excellent

---

#### Scenario B: Moderate Match
- Human: 72% positive, 22% negative
- Agent: 62% positive, 32% negative

| Test | h/diff | Old Score | New Score | Change |
|---|---|---|---|---|
| D1 (pos) | h=0.211 | 0.9 | 0.736 | -0.164 |
| D2 (neg) | h=0.220 | 0.9 | 0.725 | -0.175 |
| D3 (eff) | d=0.200 | 0.9 | 0.333 | -0.567 |
| **Weighted** | | **0.90** | **0.644** | **-0.256** |

**Impact**: Much lower, reflects true distance

---

#### Scenario C: Poor Match
- Human: 72% positive, 22% negative
- Agent: 55% positive, 60% negative

| Test | h/diff | Old Score | New Score | Change |
|---|---|---|---|---|
| D1 (pos) | h=0.355 | 0.9 | 0.556 | -0.344 |
| D2 (neg) | h=0.796 | 0.8 | 0.005 | -0.795 |
| D3 (eff) | d=0.550 | 0.7 | 0.000 | -0.700 |
| **Weighted** | | **0.82** | **0.224** | **-0.596** |

**Impact**: Dramatically lower, penalizes large differences

---

#### Scenario D: Very Poor Match (h≥0.8)
- Human: 72% positive, 22% negative
- Agent: 30% positive, 80% negative

| Test | h/diff | Old Score | New Score | Change |
|---|---|---|---|---|
| D1 (pos) | h=0.894 | 0.7 | 0.000 | -0.700 |
| D2 (neg) | h=1.264 | 0.7 | 0.000 | -0.700 |
| D3 (eff) | d=0.600 | 0.7 | 0.000 | -0.700 |
| **Weighted** | | **0.70** | **0.000** | **-0.700** |

**Impact**: Zero score for very large differences ✅

---

## ✅ Validation Results

```bash
$ python test_two_tier_evaluation.py

============================================================
TEST 3: Data-Level Tests (Continuous Scoring)
============================================================

Good match
  D1: h=0.044 → Score=0.945 (was 1.0)
  D2: h=0.071 → Score=0.912 (was 1.0)
  D3: diff=0.050 → Score=0.833 (was 1.0)
  Data-level score: 90.9%

Phenomenon but poor match
  D1: h=0.355 → Score=0.556 (was 0.9)
  D2: h=0.796 → Score=0.005 (was 0.8)
  D3: diff=0.550 → Score=0.000 (was 0.7)
  Data-level score: 22.4%

✅ Continuous scoring verified
```

---

## 🎯 Key Advantages

### 1. True Zero for Large Differences
**Old**: h=1.5 still gets 0.7 score  
**New**: h≥0.8 gets 0.0 score ✅

### 2. Proportional Rewards
**Old**: h=0.19 and h=0.01 both get 1.0  
**New**: h=0.19 gets 0.76, h=0.01 gets 0.99 ✅

### 3. No Cliff Effects
**Old**: h=0.49 gets 0.9, h=0.51 gets 0.8  
**New**: h=0.49 gets 0.39, h=0.51 gets 0.36 ✅

### 4. Separable Results
**New**: Returns separate `phenomenon_tests` and `data_tests` dicts ✅

---

## 📋 Pass Criteria (Unchanged)

Study still passes if:
1. ✅ All critical (phenomenon-level) tests pass
2. ✅ Overall weighted score ≥ 70%

**Note**: With continuous scoring, agents need better data matches to achieve 70% overall.

---

## 🔮 Example Total Scores

| Phenomenon | Data Quality | P Score | D Score (new) | Total | Pass? |
|---|---|---|---|---|---|
| ✅ Yes (P=1.0) | Excellent (h~0.05) | 4.0/4.0 | 2.3/2.5 | 97% | ✅ |
| ✅ Yes (P=1.0) | Good (h~0.20) | 4.0/4.0 | 1.9/2.5 | 91% | ✅ |
| ✅ Yes (P=1.0) | Moderate (h~0.40) | 4.0/4.0 | 1.2/2.5 | 80% | ✅ |
| ✅ Yes (P=1.0) | Poor (h~0.60) | 4.0/4.0 | 0.6/2.5 | 71% | ✅ |
| ✅ Yes (P=1.0) | Very poor (h~0.70) | 4.0/4.0 | 0.3/2.5 | 66% | ❌ |
| ✅ Yes (P=1.0) | Fail (h≥0.80) | 4.0/4.0 | 0.0/2.5 | 62% | ❌ |
| ❌ No (P=0.0) | Perfect (h=0.0) | 0.0/4.0 | 2.5/2.5 | 38% | ❌ |

**Insight**: Now requires h < 0.65 on average to pass (stricter than before)

---

## 🚀 Migration Notes

### For Users
- Scores may be **lower** than before for agents with h > 0.2
- **More discriminating**: Better separates good from mediocre agents
- **Same pass criteria**: Still need 70% overall + all critical tests

### For Developers
- `test_results` now includes `phenomenon_tests` and `data_tests` separately
- Returned scores include `phenomenon_score` and `data_score` averages
- Details include `score_formula` showing calculation

---

## 📚 Mathematical Justification

### Why Linear?

Cohen's h is already on an **interpretable scale**:
- h=0.2 is "small"
- h=0.5 is "medium"
- h=0.8 is "large"

Linear mapping preserves this:
```
score = 1 - h/0.8
```

Maps directly:
- Small difference (h=0.2) → 75% score
- Medium difference (h=0.5) → 37.5% score
- Large difference (h=0.8) → 0% score

### Alternative Considered: Exponential

```python
score = exp(-2 * cohens_h)
```

**Rejected** because:
- Less interpretable
- Doesn't reach true zero
- Over-penalizes small differences

---

## ✅ Status

- ✅ Implemented in `scorer.py`
- ✅ Updated tests pass
- ✅ Documentation complete
- ✅ Backward compatible (phenomenon tests unchanged)

---

**Version**: 2.1  
**Date**: October 29, 2024  
**Status**: Ready for production 🚀
