# Study 003 Implementation Complete

## Overview

Successfully implemented **study_003: The Framing of Decisions and the Psychology of Choice** by Tversky & Kahneman (1981).

## What Was Created

### 1. Core Study Files

✅ **metadata.json**
- Study identification and bibliographic information
- Domain: behavioral_economics, subdomain: choice_under_uncertainty
- Difficulty: easy, estimated time: 10 minutes

✅ **specification.json**
- Between-subjects design (positive_frame vs negative_frame)
- Single trial per participant (Asian Disease Problem)
- Dependent variable: choice between Program A (certain) and Program B (risky)
- Complete procedure specification

✅ **ground_truth.json**
- Original results: 72% risk-averse in positive frame, 78% risk-seeking in negative frame
- 5 validation tests with weights and pass criteria
- Statistical test specifications (χ² test, p < 0.001)
- Pass threshold: 70% weighted score

✅ **STUDY_INFO.md**
- Comprehensive documentation of the framing effect
- Theoretical significance (Prospect Theory, violation of invariance)
- Detailed results and implications
- LLM agent implementation considerations

### 2. Materials

✅ **materials/instructions.txt** - General instructions
✅ **materials/positive_frame.txt** - Gain framing (lives saved)
✅ **materials/negative_frame.txt** - Loss framing (lives lost)

### 3. Study Configuration

✅ **src/studies/study_003_config.py**
- `Study003Config` class registered with `@StudyConfigRegistry.register("study_003")`
- `create_trials()`: Generates single trial for Asian Disease Problem
- `aggregate_results()`: Computes choice proportions, framing effect size, statistical tests
- `get_custom_prompt_context()`: Provides frame-specific scenario text

### 4. Registry Update

✅ **data/registry.json** updated:
- total_studies: 2 → 3
- Added study_003 entry with all metadata
- Updated statistics: behavioral_economics: 0 → 1, easy: 1 → 2

## Study Design

### The Asian Disease Problem

**Scenario:** U.S. facing disease outbreak, 600 expected deaths, choose between two programs.

**Positive Frame (Gains):**
- Program A: 200 people will be saved (certain)
- Program B: 1/3 chance save all 600, 2/3 chance save none (risky)

**Negative Frame (Losses):**
- Program A: 400 people will die (certain)
- Program B: 1/3 chance nobody dies, 2/3 chance all 600 die (risky)

**Key Insight:** Options are objectively identical (expected value = 200 saved / 400 dead), but framing produces ~50 percentage point preference reversal.

## Validation Tests

1. **Framing Effect Direction** (Critical, 30%): Positive frame certain choice > negative frame + 30pp
2. **Positive Frame Risk Aversion** (Critical, 25%): 65-85% choose certain option
3. **Negative Frame Risk Seeking** (Critical, 25%): 70-90% choose risky option
4. **Statistical Significance** (15%): p < 0.05 for frame effect
5. **Effect Size** (5%): 40-65 percentage point difference

Pass threshold: 70% overall score, all critical tests must pass.

## Usage Example

```bash
# Run study_003 with caching
python run_full_benchmark.py \
  --real-llm \
  --model mistralai/mistral-nemo \
  --studies study_003 \
  --n-participants 76 \
  --use-cache

# Evaluate results
python evaluate_results.py --latest
```

## Expected Behavior

### Human Results (Original Study)
- **Positive frame:** 72% choose certain (Program A), 25% choose risky (Program B)
- **Negative frame:** 22% choose certain (Program A), 78% choose risky (Program B)
- **Framing effect:** ~50 percentage point difference

### LLM Agent Considerations

**Challenges:**
- LLMs may calculate expected values and make "rational" choices
- May recognize the framing manipulation from training data
- Could show reduced susceptibility compared to humans

**Research Questions:**
- Do LLM agents exhibit framing effects?
- How does prompt engineering affect susceptibility?
- Which models show more "human-like" vs "rational" patterns?

## Implementation Details

### Participant Assignment
- Between-subjects design: each participant assigned to one frame
- Frame assignment via participant profile: `framing_condition` field
- Random assignment recommended (50/50 split)

### Response Processing
- Accepts: "Program A", "Program B", "A", "B", "1", "2"
- Normalized to standard format in aggregation

### Statistical Analysis
- Chi-square test of independence (2x2 contingency table)
- Effect size: difference in proportion choosing certain option
- Includes risk attitude classification (risk-averse vs risk-seeking)

## Files Created Summary

```
data/studies/study_003/
├── metadata.json (467 bytes)
├── specification.json (4.2 KB)
├── ground_truth.json (6.8 KB)
├── STUDY_INFO.md (10.4 KB)
├── TverskyKahneman1981.pdf (existing)
└── materials/
    ├── instructions.txt (265 bytes)
    ├── positive_frame.txt (534 bytes)
    └── negative_frame.txt (516 bytes)

src/studies/
└── study_003_config.py (7.8 KB)

data/
└── registry.json (updated)
```

## Validation Status

✅ Study loads successfully  
✅ Trials generate correctly (1 trial)  
✅ Materials load properly (both frames)  
✅ Ground truth contains 5 validation tests  
✅ Config class registered and functional  
✅ Registry updated with correct statistics  

## Next Steps

1. **Test with LLM agents:**
   ```bash
   python run_full_benchmark.py --real-llm --studies study_003 --n-participants 152 --use-cache
   ```

2. **Evaluate results:**
   ```bash
   python evaluate_results.py --latest
   ```

3. **Compare to ground truth:**
   - Check if framing effect emerges
   - Measure effect size vs human data
   - Analyze which models show stronger effects

## Theoretical Significance

This study is one of the most replicated findings in behavioral economics:
- Demonstrates **Prospect Theory** in action
- Violates **rational choice theory's invariance principle**
- Shows systematic deviations from expected utility maximization
- Has major implications for policy, medicine, marketing, finance

---

**Study Type:** Between-subjects experiment  
**Difficulty:** Easy (simple design, large effect, single trial)  
**Domain:** Behavioral Economics / Decision Making  
**Status:** ✅ Complete and tested
