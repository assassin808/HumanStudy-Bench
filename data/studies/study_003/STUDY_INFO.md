# Study 003: The Framing of Decisions and the Psychology of Choice

## Overview

**Title:** The Framing of Decisions and the Psychology of Choice  
**Authors:** Amos Tversky & Daniel Kahneman  
**Year:** 1981  
**Journal:** Science, 211(4481), 453-458  
**DOI:** 10.1126/science.7455683

## Study Description

This is the famous **Asian Disease Problem**, a landmark demonstration of the **framing effect** in decision making under risk. The study shows that people's choices between identical options can be reversed simply by changing how the outcomes are described (framed).

### The Core Finding

When options are framed as **gains** (lives saved):
- 72% choose the certain option (save 200 for sure)
- 25% choose the risky option (1/3 chance save all 600, 2/3 chance save none)
- **Risk-averse preference**

When the same options are framed as **losses** (lives lost):
- 22% choose the certain option (400 die for sure)  
- 78% choose the risky option (1/3 chance nobody dies, 2/3 chance all 600 die)
- **Risk-seeking preference**

**Key insight:** The options have identical expected values (200 saved = 400 die out of 600), yet framing induces a ~50 percentage point preference reversal.

## Theoretical Significance

### Prospect Theory
This study provides strong evidence for **Prospect Theory** (Kahneman & Tversky, 1979), which proposes that:

1. **Value function is reference-dependent:** Outcomes are evaluated as gains or losses relative to a reference point
2. **Loss aversion:** Losses loom larger than equivalent gains
3. **Diminishing sensitivity:** Marginal impact decreases with distance from reference point
4. **Risk attitude depends on frame:** Risk-averse for gains, risk-seeking for losses

### Violation of Rational Choice Theory
The finding violates the **invariance principle** of rational choice theory, which states that preference between options should be independent of how they are described. Logically equivalent descriptions should not produce different choices.

## Design Details

### Participants
- **N = 152** (76 per condition)
- University students and faculty
- Random assignment to frame condition

### Procedure
1. Participants read scenario about disease outbreak (600 expected deaths)
2. Choose between two programs:
   - **Program A:** Certain outcome (200 saved / 400 die)
   - **Program B:** Risky outcome (1/3 prob: all saved/none die; 2/3 prob: none saved/all die)
3. Frame manipulated between subjects (positive vs negative)

### Key Manipulation
**Positive frame:** Outcomes described as lives saved (gains)  
**Negative frame:** Outcomes described as lives lost (losses)

Both frames present objectively identical options (expected value = 200 saved/400 dead).

## Results

| Frame | Certain Option (A) | Risky Option (B) | Preference |
|-------|-------------------|------------------|------------|
| Positive (gains) | 72% | 25% | Risk-averse |
| Negative (losses) | 22% | 78% | Risk-seeking |
| **Difference** | **50 pp** | **53 pp** | **Reversal** |

**Statistical test:** χ²(1) = 41.7, p < 0.001 (highly significant)

## Implications

### For Theory
- Demonstrates systematic violation of rational choice axioms
- Supports descriptive models (Prospect Theory) over normative models (Expected Utility Theory)
- Shows that decision frames affect value assessment

### For Practice
- Policy communication matters: how options are framed influences public support
- Medical decisions affected by gain/loss framing (e.g., survival vs mortality rates)
- Marketing and persuasion: frame products/services as gains or loss prevention
- Financial decisions: investment framing affects risk tolerance

## Replication History

This is one of the most robust and replicated findings in behavioral science:
- Replicated across cultures (Western and Eastern)
- Robust across age groups and education levels  
- Effect size typically 40-60 percentage points
- Works with various scenarios (medical, financial, environmental)

**Meta-analysis:** Effect persists even when participants are informed about framing manipulation, though magnitude may decrease with awareness.

## Validation Criteria for This Study

To pass validation, an LLM agent replication must demonstrate:

1. **✓ Framing effect direction** (Critical): Higher risk aversion in positive frame (≥30 pp difference)
2. **✓ Positive frame risk aversion** (Critical): 65-85% choose certain option
3. **✓ Negative frame risk seeking** (Critical): 70-90% choose risky option  
4. **Statistical significance**: p < 0.05 for frame effect
5. **Large effect size**: 40-65 percentage point difference

**Pass threshold:** 70% weighted score across tests

## LLM Agent Considerations

### Expected Challenges
- LLMs may calculate expected values explicitly and make "rational" choices
- Language models might recognize the framing manipulation from training data
- May show reduced susceptibility to framing compared to humans
- Could exhibit different patterns based on system prompt framing

### Implementation Notes
- Use diverse participant profiles (some analytical, some intuitive)
- Consider varying the scenario or using less-known framing problems
- May need to emphasize intuitive/fast decision-making in prompts
- Check for response patterns indicating recognition of the manipulation

### Research Questions
- Do LLM agents show framing effects similar to humans?
- How does prompt engineering (e.g., "think carefully" vs "respond quickly") affect susceptibility?
- Are certain model architectures more or less susceptible to framing?
- Can we identify which models exhibit more "human-like" vs "rational" patterns?

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
**Difficulty:** Easy (simple design, large effect)  
**Estimated Time:** 10 minutes per participant
