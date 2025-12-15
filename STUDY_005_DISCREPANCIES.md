# Check of STUDY_INFO.md vs Original Paper (Study 005)

I have compared `data/studies/study_005/STUDY_INFO.md` with the provided original paper text `data/studies/study_005/Administrative Obedience: Carrying Out Orders to use Psychological-Administrative Violence.md`.

## Summary of Findings
**Status:** Mostly Consistent, with specific discrepancies in statistical reporting.

The experimental design, procedure, stimuli (stress remarks), and participant counts are described accurately. However, the **Results** section in `STUDY_INFO.md` reports different statistical metrics (Means/t-tests) than the original paper (Medians/Mann-Whitney U/Fisher Exact), and the Mean value for the Control condition (3.20) differs notably from the Median reported in the paper (6.75).

## Detailed Comparison

| Section | STUDY_INFO.md | Original Paper | Consistency |
| :--- | :--- | :--- | :--- |
| **Title & Authors** | Correctly cites Meeus & Raaijmakers (1986). | Meeus & Raaijmakers (1986). | ✅ Consistent |
| **Sample Size** | Baseline N=24, Control N=15. | Baseline N=24, Control N=15 (Line 55). | ✅ Consistent |
| **Obedience Rate** | Baseline: 92% (22/24). Control: 0% (0/15). | Baseline: 91.7%. Control: 0.00% (Table 1). | ✅ Consistent |
| **Statistical Test (Obedience)** | Reports **Chi-square**: χ²(1) = 30.67. | Reports **Fisher exact**: p < 0.001 (Line 161). | ⚠️ **Discrepancy**: Paper used Fisher Exact. |
| **Central Tendency** | Reports **Means**: Obedience M=14.58, Control M=3.20. | Reports **Medians**: Obedience Mdn=14.81, Control Mdn=6.75 (Table 1). | ⚠️ **Discrepancy**: Paper uses Medians. The Control Mean (3.20) is much lower than the Control Median (6.75). |
| **Statistical Test (Remarks)** | Reports **t-test**: t(37)=18.45. | Reports **Mann-Whitney U**: z=5.22 (Line 161). | ⚠️ **Discrepancy**: Paper used Non-parametric test. |
| **Procedure** | 32 questions, 4 sets, remarks start set 2, consent withdrawn at remark 10. | Matches descriptions in Lines 99-105. | ✅ Consistent |
| **Stimuli** | Lists 15 specific stress remarks. | Matches Appendix (Lines 263-279) exactly. | ✅ Consistent |
| **Confederate Script** | Describes escalating protests, withdrawal at #10. | Matches "Protests by the applicant" (Lines 103-105). | ✅ Consistent |

## Recommendations

1.  **Update Statistical Reporting:** The `STUDY_INFO.md` should ideally report the **Medians** and **Mann-Whitney U** test results to match the original paper, or explicitly state that the Means and t-tests are calculated for the benchmark's internal comparison purposes (though the difference in Control value 3.20 vs 6.75 suggests the distribution might be interpreted differently).
2.  **Clarify Control Condition Data:** The discrepancy between Mean (3.20) and Median (6.75) for the Control condition is significant. A median of 6.75 implies half the control subjects went at least halfway, whereas a mean of 3.20 implies most stopped very early. This should be verified if raw data is available, or the paper's Median should be prioritized.

The narrative description of the study is highly accurate and faithful to the text.
