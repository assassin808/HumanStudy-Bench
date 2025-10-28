# HumanStudyBench

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> A realistic, sustainable, and systematic benchmark for evaluating AI agents' ability to reproduce published human studies.

## Overview

**HumanStudyBench** is a benchmark designed to evaluate AI agents on their capability to replicate human behavioral and cognitive studies from published research. The benchmark curates studies from classic and contemporary peer-reviewed literature, including full experimental specifications—designs, participant profiles, measurement protocols, and reported results.

Given these specifications, agents must replicate procedures under realistic constraints and aim to match the original outcomes. Performance is scored via unit tests: each literature-derived study constitutes a unit test, automatically checked against its reported outcomes.

## Features

- 🧪 **Curated Studies**: Hand-selected studies from peer-reviewed literature across multiple domains
- 📊 **Structured Data**: Standardized JSON schemas for metadata, specifications, and ground truth
- 🤖 **Agent Interface**: Simple API for implementing and evaluating custom agents
- 🧑‍� **LLM-as-Participant**: AI agents act as human participants, not researchers
- �📈 **Automated Evaluation**: Built-in metrics and validation criteria
- 🔄 **Extensible**: Easy to add new studies and evaluation metrics
- 📚 **Well-Documented**: Comprehensive documentation and examples

## 🏛️ Architecture: LLM-as-Participant

HumanStudyBench uses a unique **LLM-as-Participant** architecture:

```
📚 Literature → 👤 Participant Profiles → 🤖 LLM Agents → 🧪 Experiment → 📊 Results → ✅ Evaluation
```

- **AI Agent = Individual Participant**: Each agent represents a single human participant with a specific profile (age, gender, personality traits)
- **Multiple Agents per Study**: Studies run with N agents (e.g., 50 participants) to generate group-level statistics
- **Two Usage Modes**:
  1. **Default Mode**: Auto-generate participant profiles from literature specifications
  2. **Custom Mode**: User-defined profiles with specific characteristics and custom system prompts

### Example: Asch Conformity Experiment

```python
from src.agents.llm_participant_agent import ParticipantPool

# Create 50 participants with auto-generated profiles
pool = ParticipantPool(study_specification, n_participants=50)

# Or create custom participants
custom_profile = {
    "age": 22,
    "gender": "male",
    "personality_traits": {
        "conformity_tendency": 0.1,  # Independent thinker
        "confidence": 0.85
    }
}

# Run experiment and collect group statistics
results = pool.run_experiment(trials, instructions)
# Results: conformity_rate, individual differences, etc.
```

See [LLM Participant Agent Guide](docs/llm_participant_agent_guide.md) for detailed usage.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/HS_bench.git
cd HS_bench

# Install dependencies
pip install -r requirements.txt

# Install as a package (development mode)
pip install -e .
```

## Quick Start

### 1. Test Your Installation

```bash
# Quick validation test
python scripts/quick_test.py
```

### 2. Using Prompt Builder (Recommended - NEW!)

**Problem**: How do I convert `specification.json` into LLM prompts?

**Solution**: Use the new **Prompt Builder** system:

```python
from src.core.benchmark import HumanStudyBench
from src.agents.prompt_builder import get_prompt_builder

# Load study
benchmark = HumanStudyBench("data")
study = benchmark.load_study("study_001")  # Asch Conformity

# Create prompt builder (automatic specification → prompt conversion)
builder = get_prompt_builder("study_001")

# Define participant profile
participant_profile = {
    "age": 19,
    "gender": "male",
    "education": "college student",
    "personality_traits": {
        "conformity_tendency": 0.75  # High conformity
    }
}

# Automatically generate prompts
system_prompt = builder.build_system_prompt(participant_profile)
instructions = builder.get_instructions()

# Define trial data (from specification)
trial_data = {
    "trial_number": 7,
    "standard_length": 10,
    "comparison_lines": {"A": 8, "B": 10, "C": 12},
    "confederate_responses": ["A", "A", "A", "A", "A", "A"]
}

trial_prompt = builder.build_trial_prompt(trial_data)

# Call LLM with properly formatted prompts
import openai
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": instructions},
        {"role": "assistant", "content": "Yes, I understand."},
        {"role": "user", "content": trial_prompt}
    ]
)
```

**See**: [`docs/prompt_builder_guide.md`](docs/prompt_builder_guide.md) for complete guide

### 3. Using LLM Participant Agent (Full Workflow)

```python
from src.core.benchmark import HumanStudyBench
from src.agents.llm_participant_agent import ParticipantPool

# Load the benchmark
benchmark = HumanStudyBench(data_dir="data")
study = benchmark.load_study("study_001")  # Asch Conformity Experiment

# Create 50 participants with auto-generated profiles from literature
pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=50,
    use_real_llm=True,  # Set to False for simulation mode
    model="gpt-4",
    api_key="your-openai-api-key"
)

# Prepare experiment materials
trials = pool.prepare_trials(study.specification)
instructions = pool.prepare_instructions(study.materials_path)

# Run experiment
results = pool.run_experiment(trials, instructions)

# Evaluate results
from src.evaluation.scorer import Scorer
scorer = Scorer()
score, report = scorer.score_study(study, results)
print(f"Score: {score:.1f}% - {report['grade']}")
```

See more examples in the `examples/` directory:
- `10_llm_participant_demo.py` - Full experiment with auto-generated profiles
- `11_custom_profiles.py` - Custom participant personalities

## Project Structure

```
HS_bench/
├── data/                           # Benchmark data
│   ├── registry.json              # Study registry
│   ├── schemas/                   # JSON validation schemas
│   └── studies/                   # Individual studies
│       └── study_001/             # Asch Conformity Experiment (1952)
│           ├── metadata.json      # Study identification
│           ├── specification.json # Experimental design & procedures
│           ├── ground_truth.json  # Original results & validation tests
│           ├── STUDY_INFO.md     # Comprehensive documentation
│           └── materials/         # Stimuli & instructions
├── src/                           # Source code
│   ├── agents/                    # Agent implementations
│   │   ├── base_agent.py         # Abstract base class
│   │   ├── llm_participant_agent.py  # LLM-as-participant agent
│   │   └── example_agents/       # Example implementations (empty)
│   ├── core/                      # Core benchmark functionality
│   ├── evaluation/                # Scoring and metrics
│   └── __init__.py
├── tests/                         # Unit tests
├── examples/                      # Usage examples
│   ├── 10_llm_participant_demo.py # LLM participants (auto profiles)
│   └── 11_custom_profiles.py     # Custom participant profiles
├── scripts/                       # Utility scripts
├── docs/                          # Documentation
│   ├── getting_started.md
│   ├── llm_participant_agent_guide.md  # NEW: Detailed agent guide
│   └── ...
└── notebooks/                     # Jupyter notebooks
```

## 📚 Current Studies

### Study 001: Asch Conformity Experiment (1952)

**Classic social psychology study on group pressure and conformity**

- **Domain**: Social Psychology
- **Design**: Mixed (Between: control vs experimental; Within: neutral vs critical trials)
- **Participants**: 123 (50 experimental, 37 control, 36 confederates)
- **Task**: Line length judgment with confederate pressure
- **Key Finding**: 37% conformity rate when group unanimously gives wrong answer
- **Validation**: 5 tests (conformity rate range, group differences, individual differences, control accuracy, majority conformity)

**Research Questions Testable**:
- Do LLM agents show conformity like humans?
- Are there individual differences in conformity behavior?
- Does explicit confidence/independence in profiles affect conformity?
- How do different LLM models compare in social behavior?

See `data/studies/study_001/STUDY_INFO.md` for full documentation.

## 📊 Evaluation & Pass Criteria

HumanStudyBench uses a two-level pass/fail system to rigorously evaluate agent performance:

### Study-Level Evaluation

Each individual study has validation tests with weights and critical flags. Agents must pass both overall score and critical test thresholds.

| Overall Score | Grade | Status | Description |
|--------------|-------|--------|-------------|
| **100%** | Perfect | ✅ Pass | Replicated all findings exactly |
| **≥ 85%** | High Quality | ✅ Pass | Excellent replication with minor deviations |
| **≥ 70%** | Pass | ✅ Pass | Acceptable replication meeting core criteria |
| **< 70%** | Fail | ❌ Fail | Insufficient replication quality |

**Critical Tests**: Some tests are marked as `critical: true`. Failing any critical test results in automatic study failure regardless of overall score.

### Benchmark-Level Evaluation

To pass the benchmark, agents must meet **BOTH** criteria:

| Criterion | Threshold | Weight |
|-----------|-----------|--------|
| **Average Score** | ≥ 60% | Measures overall replication quality |
| **Pass Rate** | ≥ 50% | Percentage of studies passed |

**Grade System**:
- **Excellent** (≥ 85% score + ≥ 80% pass rate): Outstanding systematic replication
- **Good** (≥ 75% score + ≥ 65% pass rate): Strong systematic performance
- **Pass** (≥ 60% score + ≥ 50% pass rate): Meets minimum benchmark requirements
- **Fail** (below thresholds): Insufficient systematic performance

**Rationale**: Dual criteria prevent gaming—agents cannot pass by perfectly replicating only a few studies while ignoring others, nor by barely passing many studies without deep replication quality.

## Documentation

- [Getting Started](docs/getting_started.md) - Installation and basic usage
- [**LLM Participant Agent Guide**](docs/llm_participant_agent_guide.md) - **How to use AI agents as participants** 🆕
- [Benchmark Overview](docs/benchmark_overview.md) - Design philosophy and structure
- [Paper Curation Guide](docs/paper_curation_guide.md) - How to add new studies
- [Evaluation Metrics](docs/evaluation_metrics.md) - Scoring and validation
- [API Reference](docs/api_reference.md) - Detailed API documentation
- [Development Guide](DEVELOPMENT.md) - For contributors

## Contributing

We welcome contributions! Please see our [Paper Curation Guide](docs/paper_curation_guide.md) for information on adding new studies.

## Citation

If you use HumanStudyBench in your research, please cite:

```bibtex
@misc{humanstudybench2025,
  title={HumanStudyBench: A Benchmark for Evaluating AI Agents on Human Study Replication},
  author={Your Name},
  year={2025},
  url={https://github.com/yourusername/HS_bench}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

We thank the authors of the original studies included in this benchmark and the OSF community for making research materials openly accessible.

## Contact

For questions or feedback, please open an issue on GitHub or contact [your.email@example.com](mailto:your.email@example.com).
