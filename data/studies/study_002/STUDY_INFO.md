# Study 002: Measures of Anchoring in Estimation Tasks

## Citation
Jacowitz, K. E., & Kahneman, D. (1995). Measures of anchoring in estimation tasks. *Personality and Social Psychology Bulletin*, 21(11), 1161-1166.

## Overview
This study demonstrates the anchoring effect, where people's numerical estimates are systematically influenced by arbitrary anchor values presented before the estimation task.

## Phenomenon
**Anchoring Effect**: The tendency for people's estimates to be biased toward an initially presented anchor value, even when the anchor is randomly generated and obviously uninformative.

## Original Study Design

### Participants
- N = 156 undergraduate students
- University of California, Berkeley
- Participated for course credit in introductory psychology class

### Design
- Between-subjects design
- Two conditions per question:
  - **High anchor group**: Receives high anchor value
  - **Low anchor group**: Receives low anchor value
- Multiple estimation questions (e.g., "Length of the Mississippi River")

### Procedure
1. Participants receive an anchor value (presented as randomly generated)
2. They first answer: "Is the true value higher or lower than [anchor]?" (comparative judgment)
3. Then provide their numerical estimate (absolute judgment)
4. The difference between high and low anchor groups measures anchoring effect

### Key Measures
- **Anchoring Index**: (Mean_high - Mean_low) / (Anchor_high - Anchor_low)
- Values range from 0 (no anchoring) to 1 (complete anchoring)
- Typical values: 0.3-0.5 for factual questions

## Example Questions

### Question 1: Height of Mount Everest
- **High anchor**: 45,500 ft
- **Low anchor**: 2,000 ft
- **Correct answer**: 29,029 ft (approx)
- **Human anchoring index**: 0.79

### Question 2: Population of Chicago
- **High anchor**: 5,000,000
- **Low anchor**: 200,000
- **Correct answer**: ~2,700,000 (1990s)
- **Human anchoring index**: 0.93

### Question 3: Number of United Nations members
- **High anchor**: 127
- **Low anchor**: 14
- **Correct answer**: ~185 (at time of study)
- **Human anchoring index**: 0.65

## Expected Pattern
- Estimates in high-anchor condition significantly > estimates in low-anchor condition
- Effect persists even when people know anchor is random
- Effect size typically medium to large (d > 0.5)

## Replication Criteria
1. **P1 (Overall Anchoring Effect)**: Significant difference between estimates under high vs. low anchor conditions (One-sample t-test on Anchoring Index > 0).
2. **P2 (High vs Low Asymmetry)**: Tests if High Anchors produce stronger effects than Low Anchors (AI_high > AI_low) using Paired t-test.
3. **P3 (Confidence-Anchoring Correlation)**: Tests if Anchoring Index is negatively correlated with Confidence (Pearson correlation).
4. **D1 (Anchoring Index Equivalence)**: Tests if agent's Anchoring Index matches human baseline (0.49) using TOST equivalence test.
5. **D2 (Confidence Calibration)**: Tests if agent's average confidence matches human baseline (3.85) using TOST equivalence test.

## Implementation Notes
- Present anchors naturally (e.g., "randomly generated number")
- Ensure participants understand anchor is uninformative
- Use diverse questions to test generalizability
- Counterbalance question order within conditions
