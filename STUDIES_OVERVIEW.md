# Study Overview: Studies 001-004

## Summary Table

| Study ID | Title | Authors | Year | Domain | Phenomenon | Difficulty | Original N | Conditions |
|----------|-------|---------|------|--------|------------|------------|------------|------------|
| **study_001** | The False Consensus Effect | Ross, Greene, House | 1977 | Social Psychology | False consensus bias | Medium | ~250 | 5 scenarios × 2 choices |
| **study_002** | Measures of Anchoring in Estimation Tasks | Jacowitz & Kahneman | 1995 | Cognitive Psychology | Anchoring effect | Easy | 145 | 15 questions × 2 anchors |
| **study_003** | The Framing of Decisions and Psychology of Choice | Tversky & Kahneman | 1981 | Behavioral Economics | Framing effect | Easy | ~600 | 10 problems × 2 frames |
| **study_004** | Subjective Probability: Judgment of Representativeness | Kahneman & Tversky | 1972 | Cognitive Psychology | Representativeness heuristic | Medium | ~1500 | 9 problem types |

---

## Detailed Breakdown

### Study 001: The False Consensus Effect

**Core Phenomenon**: People overestimate how common their own choices and opinions are in the general population.

**Design**:
- **Type**: Between-subjects
- **Conditions**: 5 scenarios (supermarket, term paper, traffic ticket, space program, sign)
- **Dependent Variable**: Estimated prevalence of own choice vs. alternative choice
- **Key Metric**: FCE Magnitude = |Own estimate - Other estimate|

**Key Findings**:
- Average FCE magnitude: ~15 percentage points
- Effect persists across all scenarios
- Stronger for more personally involving decisions

**Validation Tests**:
- **P1**: Presence of FCE (magnitude > 5%)
- **D1**: Magnitude match (~15% ± 10%)

---

### Study 002: Measures of Anchoring in Estimation Tasks

**Core Phenomenon**: Initial values (anchors) influence subsequent numerical estimates, even when anchors are random.

**Design**:
- **Type**: Between-subjects
- **Conditions**: 15 diverse estimation questions × 2 anchor conditions (high/low)
- **Procedure**: 
  1. Comparative judgment ("Is X greater or less than [anchor]?")
  2. Absolute estimate ("What is your best estimate?")
- **Key Metric**: Anchoring Index (AI) = (High - Low) / (High_anchor - Low_anchor)

**Key Findings**:
- Mean AI: 0.47 (range: 0.00-0.93)
- Effect varies by question type
- Negative correlation with confidence

**Validation Tests**:
- **P1**: Overall AI significantly > 0
- **P2**: High vs Low asymmetry (AI_high ≠ AI_low)
- **P3**: Negative correlation with confidence
- **D1-D2**: AI and confidence match human baseline

---

### Study 003: The Framing of Decisions

**Core Phenomenon**: Logically equivalent choices elicit different preferences when framed as gains vs. losses.

**Design**:
- **Type**: Between-subjects
- **Conditions**: 10 decision problems × 2 frames (positive/negative or gains/losses)
- **Dependent Variable**: Choice proportions (risk-averse vs. risk-seeking)
- **Classic Example**: Asian Disease Problem
  - Positive frame → 72% choose certain option (risk averse)
  - Negative frame → 78% choose risky option (risk seeking)

**Key Findings**:
- Systematic preference reversal based on framing
- Positive frame → risk aversion
- Negative frame → risk seeking
- Effect violates rational choice theory's invariance principle

**Validation Tests**:
- **P1-P10**: Direction tests for each problem pair
- **D1-D10**: Magnitude matching with human baseline proportions

---

### Study 004: Subjective Probability - Representativeness

**Core Phenomenon**: People judge probability based on representativeness (similarity to stereotypes) rather than statistical principles, systematically ignoring sample size and base rates.

**Design**:
- **Type**: Between-subjects
- **Conditions**: 9 problem types testing different aspects of representativeness:
  1. **Birth Sequence**: Judging likelihood of birth orders
  2. **Program Choice**: Class assignment based on gender composition
  3. **Marbles Distribution**: Randomness perception
  4. **Hospital Problem**: Sample size neglect (small vs. large hospital)
  5. **Word Length**: Sample size (page vs. line)
  6. **Height Check**: Sample size (3 vs. 1 person)
  7. **Posterior Chips**: Base rate neglect in Bayesian inference
  8. **Posterior Height (N=1)**: Single case representativeness
  9. **Posterior Height (N=6)**: Sample representativeness

**Key Findings**:
- Birth Sequence: 81.5% judge less representative sequence as less likely
- Program Choice: 75.3% choose based on representativeness over statistical correctness
- Hospital Problem: Most ignore sample size effects on variance
- Posterior probability: Systematic underweighting of base rates and sample size

**Validation Tests**:
- **P1-P8**: Presence of representativeness bias in each problem type
- **D1-D2**: Magnitude matching for Birth Sequence and Program Choice

---

## Evaluation Framework

All studies use a **two-tier evaluation system**:

### Tier 1: Phenomenon-Level Tests
- **Goal**: Verify the psychological phenomenon is present
- **Method**: Statistical significance tests from original papers
- **Criterion**: Pass if agent exhibits the cognitive bias/effect
- **Weight**: Critical (must pass for study validation)

### Tier 2: Data-Level Tests
- **Goal**: Measure quantitative similarity to human baseline
- **Method**: TOST (Two One-Sided Tests) equivalence testing
- **Criterion**: Pass if agent data is statistically equivalent to human data (within δ = 0.2)
- **Weight**: Non-critical (provides additional validation)

---

## Implementation Status

| Study | Materials | Configuration | Ground Truth | Evaluation | Status |
|-------|-----------|---------------|--------------|------------|--------|
| study_001 | ✅ Complete | ✅ Complete | ✅ Complete | ✅ Complete | 🟢 Active |
| study_002 | ✅ Complete | ✅ Complete | ✅ Complete | ✅ Complete | 🟢 Active |
| study_003 | ✅ Complete | ✅ Complete | ✅ Complete | ✅ Complete | 🟢 Active |
| study_004 | ✅ Complete | ✅ Complete | ✅ Complete | ✅ Complete | 🟢 Active |

---

## Running the Studies

### Quick Start

```bash
# Run all studies
python run_full_benchmark.py --real-llm --model mistralai/mistral-nemo

# Run specific study
python run_full_benchmark.py --real-llm --model mistralai/mistral-nemo --studies study_004

# Run with custom sample size
python run_full_benchmark.py --real-llm --model mistralai/mistral-nemo --studies study_001 --n-participants 100
```

### Individual Study Scripts

```bash
# Study-specific runners (if available)
python run_study_001.py  # False Consensus Effect
python run_study_006.py  # (if implemented)
```

---

## Expected Results

### Typical LLM Performance Patterns

Based on initial testing with **mistralai/mistral-nemo**:

| Study | Phenomenon Detection Rate | Notes |
|-------|---------------------------|-------|
| study_001 | Medium | Exhibits false consensus in some scenarios |
| study_002 | High | Strong anchoring effects observed |
| study_003 | High | Clear framing effects across problems |
| study_004 | Mixed | Shows representativeness in simple problems (Birth Sequence, Program Choice), but often applies correct statistical reasoning in complex problems |

**Key Insight**: LLMs tend to exhibit some human-like cognitive biases, but their manifestation patterns differ from humans:
- Stronger in simple heuristic tasks
- Weaker in complex statistical reasoning tasks (where they often outperform humans)
- Model-dependent (different LLMs show different bias profiles)

---

## References

1. Ross, L., Greene, D., & House, P. (1977). The "false consensus effect": An egocentric bias in social perception and attribution processes. *Journal of Experimental Social Psychology*, 13(3), 279-301.

2. Jacowitz, K. E., & Kahneman, D. (1995). Measures of anchoring in estimation tasks. *Personality and Social Psychology Bulletin*, 21(11), 1161-1166.

3. Tversky, A., & Kahneman, D. (1981). The framing of decisions and the psychology of choice. *Science*, 211(4481), 453-458.

4. Kahneman, D., & Tversky, A. (1972). Subjective probability: A judgment of representativeness. *Cognitive Psychology*, 3(3), 430-454.

