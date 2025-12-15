# Study 001: The "False Consensus Effect": An Egocentric Bias in Social Perception and Attribution Processes

## Citation
Ross, L., Greene, D., & House, P. (1977). The "false consensus effect": An egocentric bias in social perception and attribution processes. *Journal of Experimental Social Psychology*, 13(3), 279-301.

## Overview
This classic study demonstrated the **False Consensus Effect** (FCE): the tendency for people to overestimate the extent to which others share their opinions, attributes, and behaviors.

The paper consists of four studies. 
- **Study 1** used hypothetical social conflict situations (stories).
- **Study 2** used a questionnaire regarding personal traits and preferences.
- **Study 3** used a hypothetical choice regarding wearing a sandwich board sign.
- **Study 4** used a real-world behavioral choice (the famous "Eat at Joe's" sign) and subsequent trait ratings.

## Key Phenomenon
**False Consensus Effect**: People who engage in a given behavior estimate that a higher proportion of others will engage in that behavior than do people who do not engage in it.

For example, in Study 4, students who agreed to wear an "Eat at Joe's" sandwich board estimated that 62% of peers would also agree, whereas those who refused estimated that 67% would refuse (i.e., only 33% would agree).

## Experimental Design

### Study 1: Hypothetical Situations
Participants read 4 stories involving a conflict or choice (Supermarket, Term Paper, Traffic Ticket, Space Program).
**Task**: 
1. Choose an option (A or B).
2. Estimate the percentage of peers who would choose A vs B.
(Note: The original study also included trait ratings, but reported them only as aggregated indices combining multiple traits. Due to the lack of granular ground truth data for individual traits, this benchmark focuses only on the verifiable False Consensus Effect component.)

### Study 2: Personal Traits and Preferences
Participants rated themselves on 35 personal description items (e.g., Shy/Outgoing, Preferences for Brown/White Bread, etc.) and estimated the percentage of "college students in general" who fit each category.
**Finding**: Participants who placed themselves in a given category consistently estimated a higher percentage of peers in that category than did those who placed themselves in the alternative category.

### Study 3: Hypothetical "Eat at Joe's" / "Repent" Sign
Participants read a story about being asked to wear a sandwich board sign ("Eat at Joe's" or "Repent").
**Task**:
1. Decide whether they would hypothetically wear the sign.
2. Estimate the percentage of peers who would wear it.
(Note: Trait inference component omitted due to data aggregation in the original paper preventing granular validation.)

### Study 4: Real "Eat at Joe's" / "Repent" Sign
**Procedure**: Participants were actually asked if they would wear a sandwich board saying "EAT AT JOE'S" (or "REPENT") around campus for 30 minutes.
**Task**:
1. Decide to Wear or Refuse (Real behavior).
2. Estimate peer compliance rates.
3. Make trait inferences about specific individuals who chose differently.

## Benchmark Implementation
This benchmark implements:
1. **Study 1 Scenarios**: Supermarket, Term Paper, Traffic Ticket, Space Program.
2. **Study 2 Scenario**: Personal Traits and Preferences Questionnaire.
3. **Study 3 Scenario**: Eat at Joe's / Repent Sign (Hypothetical).
4. **Evaluation**: Checks if the agent, when assigned a choice/trait (or making one), estimates a higher consensus for that choice/trait compared to the alternative.
