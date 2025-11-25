# Study 001: The "False Consensus Effect": An Egocentric Bias in Social Perception and Attribution Processes

## Citation
Ross, L., Greene, D., & House, P. (1977). The "false consensus effect": An egocentric bias in social perception and attribution processes. *Journal of Experimental Social Psychology*, 13(3), 279-301.

## Overview
This classic study demonstrated the **False Consensus Effect** (FCE): the tendency for people to overestimate the extent to which others share their opinions, attributes, and behaviors.

The paper consists of four studies. 
- **Study 1** used hypothetical social conflict situations.
- **Study 2** used a real-world behavioral choice (the famous "Eat at Joe's" sign).
- **Studies 3 & 4** explored attributional mechanisms and trait descriptions.

## Key Phenomenon
**False Consensus Effect**: People who engage in a given behavior estimate that a higher proportion of others will engage in that behavior than do people who do not engage in it.

For example, in Study 2, students who agreed to wear an "Eat at Joe's" sandwich board estimated that 62% of peers would also agree, whereas those who refused estimated that 67% would refuse (i.e., only 33% would agree).

## Experimental Design

### Study 1: Hypothetical Situations
Participants read 4 stories involving a conflict or choice (e.g., contesting a traffic ticket, witnessing shoplifting).
**Task**: 
1. Choose an option (A or B).
2. Estimate the percentage of peers who would choose A vs B.
3. Rate the personality traits of a typical person who chooses A and B.

### Study 2: The "Eat at Joe's" Sign
**Procedure**: Participants were asked if they would wear a sandwich board saying "EAT AT JOE'S" around campus for 30 minutes.
**Task**:
1. Decide to Wear or Refuse.
2. Estimate peer compliance rates.
3. Make trait inferences about those who choose differently.

### Study 3: Personal Traits and Preferences
Participants rated themselves on 35 personal trait dimensions (e.g., Shy/Outgoing) and estimated the percentage of peers who fit each category.
**Finding**: Participants who categorized themselves as "Shy" estimated a higher prevalence of shyness than did those who categorized themselves as "Outgoing".

### Study 4: Diagnosis from Consensus Info
Participants were given information about a target person's choice (e.g., Paying a Traffic Ticket) and the consensus statistics (e.g., "65% of people pay"). They then made attributions about the target's personality.
**Finding**: Attributions were more extreme when the target's behavior was presented as deviant (low consensus) than when it was common (high consensus).

## Benchmark Implementation
This benchmark implements:
1. **Study 1 Scenarios**: Supermarket, Term Paper, Traffic Ticket, Space Program.
2. **Study 2 Scenario**: Eat at Joe's Sign.
3. **Study 3 Scenario**: Assessment of personal traits (Shy/Outgoing, Optimistic/Pessimistic, etc.) and peer prevalence estimates.
4. **Evaluation**: Checks if the agent, when assigned a choice/trait (or making one), estimates a higher consensus for that choice/trait compared to the alternative.
