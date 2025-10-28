# Paper Curation Guide

This guide explains how to curate and add new studies to HumanStudyBench.

## Overview

Adding a study involves:
1. Selecting an appropriate paper
2. Extracting key information
3. Structuring data according to schemas
4. Validating the study
5. Submitting for inclusion

## Study Selection Criteria

### Must Have
✅ **Published in peer-reviewed venue**: Journal article or conference proceeding  
✅ **Complete experimental details**: Design, procedure, materials clearly described  
✅ **Quantitative results**: Statistical tests and effect sizes reported  
✅ **Replicable**: Another researcher could reproduce the study  
✅ **Ethical**: Study follows ethical guidelines and respect participants

### Nice to Have
⭐ **Open data/materials**: Available on OSF, GitHub, or journal supplement  
⭐ **Pre-registered**: Study was pre-registered  
⭐ **Replicated**: Independent replication exists  
⭐ **High impact**: Classic study or highly cited  
⭐ **Diverse sample**: Non-WEIRD participants

### Exclusion Criteria
❌ **No quantitative data**: Purely qualitative studies  
❌ **Incomplete information**: Key details missing  
❌ **Unethical methods**: Violates modern ethical standards  
❌ **Too complex**: Requires specialized equipment/expertise  
❌ **Proprietary materials**: Cannot be shared due to licensing

## Study Curation Process

### Step 1: Identify Candidate Paper

Sources:
- Classic studies (e.g., Stroop, Milgram, Kahneman & Tversky)
- Recent high-impact papers
- OSF preregistrations with data
- Replication projects (Many Labs, Psych Science Accelerator)

Check:
- Is full text accessible?
- Are materials available?
- Are results clearly reported?

### Step 2: Extract Information

Create a working document with:

#### Metadata
- Title, authors, year
- Journal/venue
- DOI
- Domain and subdomain
- Keywords/tags

#### Design
- Independent variables (names, levels, manipulation)
- Dependent variables (names, units, measurement method)
- Design type (between/within/mixed)
- Sample size
- Randomization scheme

#### Procedure
- Step-by-step instructions
- Trial structure
- Timing information
- Counterbalancing
- Participant instructions

#### Materials
- Stimuli (images, text, videos)
- Questionnaires
- Equipment requirements
- Software used

#### Results
- Descriptive statistics (means, SDs)
- Inferential statistics (t, F, p-values)
- Effect sizes (Cohen's d, eta-squared)
- Key findings

#### Validation Criteria
- What would count as "replication"?
- Critical statistical tests
- Acceptable ranges for effects

### Step 3: Structure Data

Create study directory:
```bash
mkdir -p data/studies/study_XXX
cd data/studies/study_XXX
mkdir materials materials/stimuli
```

#### Create metadata.json

Template:
```json
{
  "id": "study_XXX",
  "title": "Full Title of the Study",
  "authors": ["First Author", "Second Author"],
  "year": 2020,
  "source": {
    "type": "journal_article",
    "journal": "Journal Name",
    "volume": 10,
    "issue": 2,
    "pages": "123-145",
    "doi": "10.1234/journal.2020.123",
    "url": "https://doi.org/10.1234/journal.2020.123",
    "osf_link": "https://osf.io/xxxxx/"
  },
  "domain": "cognitive_psychology",
  "subdomain": "attention",
  "difficulty": "medium",
  "estimated_time_minutes": 20,
  "tags": ["attention", "interference", "reaction_time"],
  "citation": "Author, A., & Author, B. (2020). Full citation in APA format.",
  "license": "CC-BY-4.0",
  "notes": "Any additional notes about this study"
}
```

#### Create specification.json

Template:
```json
{
  "study_id": "study_XXX",
  "design": {
    "type": "within_subjects",
    "independent_variables": [
      {
        "name": "condition",
        "type": "categorical",
        "levels": ["level1", "level2", "level3"],
        "description": "Description of this variable"
      }
    ],
    "dependent_variables": [
      {
        "name": "reaction_time",
        "type": "continuous",
        "unit": "milliseconds",
        "measurement": "time from stimulus onset to response",
        "range": [0, 5000]
      }
    ],
    "counterbalancing": "latin_square",
    "randomization": "fully_randomized"
  },
  "participants": {
    "n": 100,
    "age_range": [18, 35],
    "age_mean": 22.5,
    "gender_distribution": {"male": 45, "female": 53, "other": 2},
    "recruitment_source": "university_participant_pool",
    "recruitment_criteria": [
      "native_english_speaker",
      "normal_or_corrected_vision",
      "no_neurological_disorders"
    ],
    "exclusion_criteria": [
      "previous_participation",
      "incomplete_data"
    ],
    "compensation": "course_credit"
  },
  "procedure": {
    "description": "Detailed description of the experimental procedure",
    "steps": [
      {
        "step": 1,
        "description": "Informed consent",
        "duration_minutes": 2
      },
      {
        "step": 2,
        "description": "Instructions",
        "duration_minutes": 3,
        "materials": "materials/instructions.txt"
      },
      {
        "step": 3,
        "description": "Practice trials",
        "n_trials": 10
      },
      {
        "step": 4,
        "description": "Experimental trials",
        "n_trials": 120,
        "blocks": 4
      },
      {
        "step": 5,
        "description": "Debriefing",
        "duration_minutes": 2
      }
    ],
    "trial_structure": {
      "fixation_ms": 500,
      "stimulus_ms": 200,
      "response_window_ms": 2000,
      "iti_ms": 1000
    },
    "instructions_file": "materials/instructions.txt",
    "stimuli_directory": "materials/stimuli/"
  },
  "materials": {
    "stimuli": {
      "type": "text",
      "count": 60,
      "format": "words in colored text",
      "source": "materials/stimuli/"
    },
    "equipment": ["computer", "keyboard"],
    "software": "PsychoPy 3.0",
    "display": {
      "resolution": "1920x1080",
      "refresh_rate": 60,
      "viewing_distance_cm": 60
    }
  }
}
```

#### Create ground_truth.json

Template:
```json
{
  "study_id": "study_XXX",
  "original_results": {
    "descriptive_statistics": {
      "reaction_time": {
        "condition_1": {
          "n": 100,
          "mean": 550,
          "sd": 80,
          "median": 540,
          "min": 380,
          "max": 850
        },
        "condition_2": {
          "n": 100,
          "mean": 750,
          "sd": 120,
          "median": 735,
          "min": 480,
          "max": 1100
        }
      },
      "accuracy": {
        "condition_1": {"mean": 0.95, "sd": 0.05},
        "condition_2": {"mean": 0.87, "sd": 0.08}
      }
    },
    "inferential_statistics": {
      "main_effect": {
        "test": "repeated_measures_ANOVA",
        "F": 45.2,
        "df": [2, 198],
        "p": 0.001,
        "effect_size": "eta_squared",
        "effect_size_value": 0.314
      },
      "pairwise_comparisons": [
        {
          "comparison": "condition_2_vs_condition_1",
          "test": "paired_t_test",
          "t": 8.5,
          "df": 99,
          "p": 0.001,
          "cohens_d": 1.85,
          "ci_95": [160, 240]
        }
      ]
    },
    "key_findings": [
      "Significant main effect of condition on reaction time",
      "Condition 2 produced slower responses than Condition 1",
      "Large effect size (d = 1.85)"
    ]
  },
  "validation_criteria": {
    "required_tests": [
      {
        "test_id": "main_effect",
        "test_name": "Main effect of condition",
        "description": "Significant difference between conditions",
        "type": "statistical_significance",
        "statistic": "p_value",
        "threshold": 0.05,
        "comparison": "less_than"
      },
      {
        "test_id": "effect_direction",
        "test_name": "Effect direction",
        "description": "Condition 2 RT > Condition 1 RT",
        "type": "direction_test",
        "expected": "condition_2 > condition_1"
      },
      {
        "test_id": "effect_size",
        "test_name": "Effect size magnitude",
        "description": "Cohen's d between 1.5 and 2.5",
        "type": "range_test",
        "statistic": "cohens_d",
        "min": 1.5,
        "max": 2.5
      },
      {
        "test_id": "descriptive_match",
        "test_name": "Descriptive statistics similarity",
        "description": "Means within 20% of original",
        "type": "similarity_test",
        "tolerance": 0.20
      }
    ],
    "scoring": {
      "total_points": 4.0,
      "test_weights": {
        "main_effect": 1.0,
        "effect_direction": 1.0,
        "effect_size": 1.0,
        "descriptive_match": 1.0
      },
      "passing_threshold": 0.75
    }
  },
  "replication_history": [
    {
      "citation": "Replicator et al. (2022)",
      "result": "successful",
      "notes": "Direct replication with n=200"
    }
  ]
}
```

#### Add Materials

```
materials/
├── instructions.txt          # Full participant instructions
├── stimuli/                  # Stimulus files
│   ├── stimulus_001.txt
│   ├── stimulus_002.txt
│   └── ...
└── questionnaires/           # Any questionnaires used
    └── demographics.json
```

### Step 4: Validate Study

Run validation script:
```bash
python scripts/validate_study.py study_XXX
```

This checks:
- JSON files are valid
- Required fields present
- Schemas are followed
- Files referenced exist
- IDs are consistent

Fix any errors reported.

### Step 5: Update Registry

Add entry to `data/registry.json`:

```json
{
  "id": "study_XXX",
  "title": "Study Title",
  "domain": "cognitive_psychology",
  "difficulty": "medium",
  "tags": ["tag1", "tag2"],
  "status": "active",
  "added_date": "2025-10-27",
  "version": "1.0"
}
```

### Step 6: Test with Example Agent

```bash
python examples/02_run_single_study.py --study_id study_XXX
```

Verify:
- Agent can load the study
- Specifications are clear
- Validation tests run
- Scoring works

### Step 7: Document

Add study to documentation:

**docs/studies_catalog.md**:
```markdown
### Study XXX: [Title]
- **Domain**: Cognitive Psychology
- **Difficulty**: Medium
- **Authors**: Author et al. (2020)
- **Key Finding**: Brief description
- **Why included**: Rationale for inclusion
```

### Step 8: Submit

Create pull request with:
- Study files
- Updated registry
- Validation output
- Brief description in PR

## Quality Checklist

Before submitting, verify:

- [ ] All JSON files valid and complete
- [ ] Validation script passes
- [ ] Materials included (or clearly documented why not)
- [ ] Citations are accurate
- [ ] Appropriate difficulty level
- [ ] Validation criteria are reasonable
- [ ] Can be run by example agent
- [ ] Documentation updated
- [ ] License cleared for materials

## Common Issues

### Issue: Missing Materials
**Solution**: Document where to obtain them, or create simplified versions

### Issue: Complex Analysis
**Solution**: Focus on main effects, document full analysis in notes

### Issue: Proprietary Stimuli
**Solution**: Use similar open-source alternatives, document substitution

### Issue: Unclear Procedures
**Solution**: Consult original paper supplements, contact authors if needed

## Domain-Specific Guidelines

### Cognitive Psychology
- Include trial timings
- Specify response mappings
- Document counterbalancing

### Social Psychology
- Include cover story
- Specify manipulation checks
- Document deception procedures (if any)

### Behavioral Economics
- Include payment structure
- Specify decision scenarios
- Document incentive compatibility

## Tips for High-Quality Studies

1. **Be thorough**: Include all details, even if they seem minor
2. **Test yourself**: Could you run this study from your specification?
3. **Think about validity**: What would truly count as replication?
4. **Document uncertainties**: If something is unclear, note it
5. **Preserve context**: Include background information in notes

## Getting Help

Questions during curation? Reach out:
- GitHub Discussions: Ask the community
- Issue tracker: Report problems with process
- Email maintainers: For private questions

## Recognition

Contributors who curate studies will be:
- Listed in CONTRIBUTORS.md
- Acknowledged in papers using the benchmark
- Invited as co-authors on benchmark papers (if substantial contribution)

Thank you for contributing to HumanStudyBench! 🎉
