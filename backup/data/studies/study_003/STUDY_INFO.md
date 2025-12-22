# Study 003: The Framing of Decisions and the Psychology of Choice

## Overview

**Title:** The Framing of Decisions and the Psychology of Choice  
**Authors:** Amos Tversky & Daniel Kahneman  
**Year:** 1981  
**Journal:** Science, 211(4481), 453-458  
**DOI:** 10.1126/science.7455683

## Study Description

This study investigates systematic reversals of preference caused by variations in the framing of acts, contingencies, and outcomes. The benchmark replicates four key experiments from the original paper, demonstrating how decision frames affect value assessment and risk attitudes.

### Experiment 1: The Framing of Acts (Asian Disease Problem)
The classic demonstration of risk aversion in the domain of gains and risk seeking in the domain of losses.
- **Problem 1 (Positive Frame):** Save 200 lives vs. 1/3 chance to save 600.
- **Problem 2 (Negative Frame):** 400 die vs. 2/3 chance 600 die.
*(Note: Problems 3 & 4 also explore the framing of acts with monetary outcomes, showing violations of dominance when decisions are framed concurrently)*

### Experiment 2: The Framing of Contingencies (Certainty Effect)
Demonstrates that reducing a probability by a constant factor has more impact when the outcome was initially certain.
- **Problem 5:** Certain win ($30) vs. Risky win (80% chance of $45).
- **Problem 7:** Low probability win (25% chance of $30) vs. Lower probability win (20% chance of $45).
*(Note: Problem 6 investigates pseudocertainty, showing preferences similar to Problem 5)*

### Experiment 3: The Framing of Outcomes (Psychological Accounting - Ticket)
Investigates how "sunk costs" are accounted for depending on whether they are linked to a specific transaction (minimal vs. inclusive account).
- **Problem 8 (Lost Cash):** Lost $10 bill. Buy $10 ticket?
- **Problem 9 (Lost Ticket):** Lost $10 ticket. Buy another $10 ticket?

### Experiment 4: The Framing of Outcomes (Psychological Accounting - Calculator)
Investigates whether the value of a saving is evaluated relative to the base price.
- **Problem 10 (Low Price):** Drive 20 min to save $5 on $15 calculator?
- **Problem 10 (High Price):** Drive 20 min to save $5 on $125 calculator?

## Design & Results

### Participants
Original study involved university students (Stanford & UBC) responding to questionnaires in a classroom setting. Each problem was presented to a different group of respondents (between-subjects design).

### Detailed Results Table

| Problem | Description | N | Key Result |
| :--- | :--- | :--- | :--- |
| **1** | Asian Disease (Gain) | 152 | 72% Risk Averse (Safe) |
| **2** | Asian Disease (Loss) | 155 | 78% Risk Seeking (Risky) |
| **3** | Monetary Acts (Concurrent) | 150 | 73% chose inconsistent pair (A&D) |
| **4** | Monetary Acts (Combined) | 86 | 100% chose dominant pair (B&C) |
| **5** | Certainty Effect | 77 | 78% prefer Certainty ($30) |
| **6** | Pseudocertainty | 85 | 74% prefer "Certainty" ($30) |
| **7** | No Certainty (Control) | 81 | 58% prefer Risky ($45) |
| **8** | Lost Cash | 183 | 88% Willing to buy ticket |
| **9** | Lost Ticket | 200 | 46% Willing to buy ticket |
| **10 (v1)** | Calculator ($15) | 93 | 68% Willing to drive |
| **10 (v2)** | Calculator ($125) | 88 | 29% Willing to drive |

## Validation Criteria

To pass validation, an LLM agent must replicate the direction of the framing effects across these domains, as defined in `ground_truth.json`.

1.  **✓ Framing Effect (P1)**: Replicate preference reversal between Problems 1 & 2. (Critical)
2.  **✓ Certainty Effect (P2)**: Replicate shift from Safe preference in Problem 5 to Risky preference in Problem 7.
3.  **✓ Accounting - Ticket (P3)**: Significantly higher willingness to buy in Problem 8 vs Problem 9.
4.  **✓ Accounting - Calculator (P4)**: Significantly higher willingness to drive in Problem 10 (v1) vs Problem 10 (v2).

**Pass threshold:** 70% weighted score across phenomenon-level tests and data-level matching.

## Replication History

This is one of the most robust and replicated findings in behavioral science:
- Replicated across cultures (Western and Eastern)
- Robust across age groups and education levels
- Effect size typically 40-60 percentage points
- Works with various scenarios (medical, financial, environmental)

## References

**Primary source:**
- Tversky, A., & Kahneman, D. (1981). The framing of decisions and the psychology of choice. *Science*, *211*(4481), 453-458.

**Related works:**
- Kahneman, D., & Tversky, A. (1979). Prospect theory: An analysis of decision under risk. *Econometrica*, 47(2), 263-291.
- Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.

## Citation

```bibtex
@article{tversky1981framing,
  title={The framing of decisions and the psychology of choice},
  author={Tversky, Amos and Kahneman, Daniel},
  journal={Science},
  volume={211},
  number={4481},
  pages={453--458},
  year={1981},
  doi={10.1126/science.7455683}
}
```

---

**Study Type:** Between-subjects experiment  
**Domain:** Behavioral Economics / Judgment and Decision Making  
**Difficulty:** Medium (multiple experiments)  
**Estimated Time:** 10 minutes per participant
