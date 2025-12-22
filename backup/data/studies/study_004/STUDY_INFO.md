# Study 004: Subjective Probability - A Judgment of Representativeness

## Citation

Kahneman, D., & Tversky, A. (1972). Subjective probability: A judgment of representativeness. *Cognitive Psychology*, 3(3), 430-454.

## Overview

This foundational study in judgment and decision making demonstrates the **representativeness heuristic**: people judge the probability of events based on how representative (similar) they are to their parent population, systematically ignoring key statistical principles like sample size and variance.

## Key Phenomenon

The representativeness heuristic leads to systematic errors in probability judgment:

1. **Insensitivity to sample size**: People ignore sample size when judging likelihood
2. **Misconceptions of chance**: Sequences that "look random" are judged more probable
3. **Neglect of base rates**: Similarity to a category overrides statistical base rates
4. **Neglect of variance**: People focus on central tendency and ignore variance

## Experimental Design

**Design Type**: Between-subjects  
**Original Sample**: ~1500 participants across multiple studies (high school students, ages 15-18)
- Birth sequence problem: 92 participants
- Program choice problem: 89 participants  
**Recommended Sample**: 100+ participants (50 per problem)  
**Trials**: 1 problem per participant (from questionnaire of ~24 items)

### Problems Implemented

#### 1. Birth Sequence Problem

**Scenario**: Families with 6 children, comparing two birth sequences:
- Reference: G B G B B G (72 families)
- Target: B G B B B B (estimate frequency)

**Objective Probability**: Both sequences are equally likely (each has probability 1/64)

**Representativeness**: GBGBBG is more representative (balanced sex ratio, appears random)

**Original Finding**: 75 of 92 participants (81.5%) judged BGBBBB as less likely, with median estimate of 30 families vs. 72 (p < .01)

**Key Insight**: Participants ignore equal objective probability and judge based on representativeness

#### 2. Program Choice Problem

**Scenario**: 
- Program A: 65% boys (majority)
- Program B: 45% boys (minority)
- Observed class: 55% boys
- Question: Which program does the class likely belong to?

**Correct Answer**: Program B (higher variance at p=0.45 makes 55% more likely)

**Representative Answer**: Program A (55% is closer to 65%, preserves majority)

**Original Finding**: 67 of 89 participants (75.3%) chose Program A (p < .01)

**Key Insight**: Participants choose based on representativeness (majority preservation) rather than statistical reasoning (variance consideration)

## Theoretical Significance

1. **Challenges Normative Models**: Demonstrates systematic deviation from Bayesian probability judgment
2. **Predictable Errors**: Errors are not random but follow consistent patterns
3. **Robust Effect**: Replicates across populations, cultures, and even expert statisticians
4. **Heuristics and Biases Program**: Foundational paper in the heuristics and biases research program

## Implementation Notes

### Critical Features

1. **Clear Scenario Presentation**: Ensure agents understand the statistical structure
2. **Between-Subjects Design**: Each agent sees ONE problem (randomly assigned)
3. **Response Parsing**: Handle both numerical estimates and categorical choices
4. **Questionnaire Format**: Original study presented ~24 questions per participant in quiz format

### Expected Agent Behavior

**If representativeness heuristic is present:**
- Birth sequence: Judge BGBBBB as less likely, estimate < 72 (~81.5% of humans show this bias)
- Program choice: Choose Program A (representative over correct) (~75.3% of humans choose this)

**If statistical reasoning dominates:**
- Birth sequence: Recognize equal probability or estimate ≈72
- Program choice: Choose Program B (correct based on variance)

### Validation Strategy

**Phenomena Tests (Critical):**
- P1: Birth sequence bias present (proportion > 50%, p < .05)
- P2: Program choice bias present (proportion > 50%, p < .05)

**Data Replication Tests (Non-Critical):**
- D1: Birth sequence bias magnitude matches human baseline (TOST with δ=0.2)
- D2: Program choice bias magnitude matches human baseline (TOST with δ=0.2)

**Pass Criteria:**
- All phenomenon tests must pass (bias detected)
- Overall score ≥ 70% (weighted average including data replication)

## Connection to Other Studies

- **Study 003 (Framing Effect)**: Also by Kahneman & Tversky, demonstrates another systematic bias
- **Heuristics and Biases Tradition**: Part of broader research program on cognitive shortcuts
- **Dual Process Theory**: Representativeness is System 1 (fast, intuitive), statistical reasoning is System 2 (slow, analytical)

## References

### Original Paper
Kahneman, D., & Tversky, A. (1972). Subjective probability: A judgment of representativeness. *Cognitive Psychology*, 3(3), 430-454.

### Related Work
- Tversky, A., & Kahneman, D. (1974). Judgment under uncertainty: Heuristics and biases. *Science*, 185(4157), 1124-1131.
- Kahneman, D., Slovic, P., & Tversky, A. (1982). *Judgment under uncertainty: Heuristics and biases*. Cambridge University Press.

### Methodological References
- Cohen, J. (1988). *Statistical power analysis for the behavioral sciences* (2nd ed.). Erlbaum.
- Lakens, D., et al. (2018). Equivalence testing for psychological research. *Advances in Methods and Practices in Psychological Science*, 1(2), 259-269.
