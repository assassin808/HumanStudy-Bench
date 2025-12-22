# Getting Started with HumanStudyBench

This guide will help you get up and running with HumanStudyBench quickly.

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/HS_bench.git
cd HS_bench
```

### Step 2: Create a Virtual Environment (Recommended)

```bash
# Using venv
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Or using conda
conda create -n hs_bench python=3.9
conda activate hs_bench
```

### Step 3: Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install in development mode (for contributors)
pip install -e .

# Optional: Install development tools
pip install -e ".[dev]"
```

## Quick Start

### Example 1: Load and Explore a Study

```python
from src.core.benchmark import HumanStudyBench

# Initialize the benchmark
benchmark = HumanStudyBench(data_dir="data")

# List all available studies
studies = benchmark.registry["studies"]
print(f"Total studies: {len(studies)}")

# Load a specific study
study = benchmark.load_study("study_001")

# Inspect study metadata
print(f"Title: {study.metadata['title']}")
print(f"Domain: {study.metadata['domain']}")
print(f"Year: {study.metadata['year']}")

# View experimental design
design = study.specification["design"]
print(f"Design type: {design['type']}")
print(f"IVs: {[iv['name'] for iv in design['independent_variables']]}")
print(f"DVs: {[dv['name'] for dv in design['dependent_variables']]}")
```

### Example 2: Run LLM Participant Agent on Asch Study

```python
from src.core.benchmark import HumanStudyBench
from src.agents.llm_participant_agent import ParticipantPool
from src.evaluation.scorer import Scorer

# Initialize
benchmark = HumanStudyBench(data_dir="data")
study = benchmark.load_study("study_001")

# Create participant pool with auto-generated profiles
pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=50,
    use_real_llm=False  # Set to True to use real LLM API
)

# Prepare experiment
trials = pool.prepare_trials(study.specification)
instructions = pool.prepare_instructions(study.materials_path)

# Run experiment
results = pool.run_experiment(trials, instructions)

# Evaluate results
scorer = Scorer()
score, report = scorer.score_study(study, results)

print(f"Score: {score:.1f}%")
print(f"Grade: {report['grade']}")
print(f"Conformity Rate: {results['descriptive_statistics']['conformity_rate']['experimental']['mean']:.2%}")
```

### Example 3: Create Custom Participant Profiles

```python
from src.agents.llm_participant_agent import LLMParticipantAgent

# Create a specific participant
independent_thinker = LLMParticipantAgent(
    participant_id=1,
    profile={
        "age": 22,
        "gender": "male",
        "education": "college senior",
        "personality_traits": {
            "conformity_tendency": 0.1,  # Low conformity
            "independence": 0.9,
            "confidence": 0.85
        }
    },
    use_real_llm=False
)

# Participant receives instructions
independent_thinker.receive_instructions("You will judge line lengths...")

# Participant completes a trial
trial = {
    "trial_number": 1,
    "study_type": "asch_conformity",
    "standard_line_length": 10,
    "comparison_lines": {"A": 8, "B": 10, "C": 12},
    "correct_answer": "B",
    "confederate_responses": ["A", "A", "A", "A", "A", "A"]
}

response = independent_thinker.complete_trial(trial)
print(f"Response: {response['response']}")
print(f"Correct: {response['is_correct']}")

# Get participant summary
summary = independent_thinker.get_summary()
print(f"Conformity rate: {summary['conformity_rate']:.2%}")
```

## Understanding the Data Structure

### Study Directory Layout

Each study is organized as follows:

```
data/studies/study_001/
├── metadata.json          # Title, authors, citation, domain
├── specification.json     # Experimental design and procedures
├── ground_truth.json      # Original results and validation criteria
└── materials/             # Experimental materials
    ├── instructions.txt
    ├── stimuli/
    └── questionnaires/
```

### Key Files

**metadata.json**: Basic information about the study
```json
{
  "id": "study_001",
  "title": "Study Title",
  "authors": ["Author 1", "Author 2"],
  "year": 2020,
  "domain": "cognitive_psychology"
}
```

**specification.json**: What the agent needs to replicate
```json
{
  "design": {...},
  "participants": {...},
  "procedure": {...},
  "materials": {...}
}
```

**ground_truth.json**: Expected outcomes for validation
```json
{
  "original_results": {...},
  "validation_criteria": {...}
}
```

## Creating Your Own Agent

HumanStudyBench uses the **LLM-as-Participant** architecture. To create custom agents:

### Option 1: Use ParticipantPool with Custom Profiles

```python
from src.agents.llm_participant_agent import ParticipantPool

# Define custom profiles
custom_profiles = [
    {
        "age": 22,
        "gender": "male",
        "personality_traits": {"conformity_tendency": 0.1}
    },
    {
        "age": 20,
        "gender": "female",
        "personality_traits": {"conformity_tendency": 0.8}
    },
    # ... more profiles
]

# Create pool with custom profiles
pool = ParticipantPool(
    study_specification=specification,
    custom_profiles=custom_profiles,
    use_real_llm=True,
    model="gpt-4"
)
```

### Option 2: Create Individual Participants

```python
from src.agents.llm_participant_agent import LLMParticipantAgent

# Create a specific participant
participant = LLMParticipantAgent(
    participant_id=1,
    profile={
        "age": 22,
        "gender": "male",
        "personality_traits": {
            "conformity_tendency": 0.37,
            "independence": 0.63
        }
    },
    system_prompt_override="You are a college student...",  # Optional
    use_real_llm=True,
    model="gpt-4",
    api_key="your-api-key"
)

# Use the participant
participant.receive_instructions(instructions_text)
response = participant.complete_trial(trial_dict)
```

See the [LLM Participant Agent Guide](llm_participant_agent_guide.md) for comprehensive documentation.

## Next Steps

- Read the [**LLM Participant Agent Guide**](llm_participant_agent_guide.md) for detailed usage
- Read the [Benchmark Overview](benchmark_overview.md) to understand the design philosophy
- Check out [API Reference](api_reference.md) for detailed documentation
- See `run_full_benchmark.py` for complete benchmark execution examples
- Review [Paper Curation Guide](paper_curation_guide.md) if you want to contribute studies

## Troubleshooting

### Import Errors

If you get import errors, make sure you've installed the package:

```bash
pip install -e .
```

### Missing Dependencies

```bash
pip install -r requirements.txt
```

### Study Loading Errors

Validate a study's structure using the validation pipeline:

```bash
python validation_pipeline/run_validation.py --study-id study_001
```

## Getting Help

- Check the [documentation](../docs/)
- Open an issue on [GitHub](https://github.com/yourusername/HS_bench/issues)
- Join discussions on [GitHub Discussions](https://github.com/yourusername/HS_bench/discussions)
