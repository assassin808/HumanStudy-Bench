# Quick Start Guide

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Basic Usage

### Run an Experiment

```bash
# With real LLM (requires OPENROUTER_API_KEY)
export OPENROUTER_API_KEY="your-key"
python run_full_benchmark.py --real-llm --model mistralai/mistral-nemo --studies study_001

# Mock mode (no API calls)
python run_full_benchmark.py --studies study_001
```

### Evaluate Results

```bash
# Evaluate latest cached result
python evaluate_results.py --latest

# Evaluate all cached results
python evaluate_results.py --all
```

## Key Options

| Option | Description |
|--------|-------------|
| `--real-llm` | Use real LLM API |
| `--model MODEL` | Model ID (default: mistralai/mistral-nemo) |
| `--studies STUDY [STUDY...]` | Studies to run |
| `--n-participants N` | Number of participants |
| `--use-cache` | Enable result caching |
| `--num-workers N` | Parallel workers |

## Python API

```python
from src.core.benchmark import HumanStudyBench
from src.agents.llm_participant_agent import ParticipantPool
from src.evaluation.scorer import Scorer

# Load study
benchmark = HumanStudyBench("data")
study = benchmark.load_study("study_001")

# Run experiment
pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=50,
    use_real_llm=True
)
results = pool.run_experiment(trials, instructions)

# Evaluate
scorer = Scorer()
score_report = scorer.score_study(study, results)
```

## Adding a New Study

1. Create `data/studies/study_XXX/` directory
2. Add `metadata.json`, `specification.json`, `ground_truth.json`
3. Create `src/studies/study_XXX_config.py` implementing `BaseStudyConfig`
4. Update `data/registry.json`

See `validation_pipeline/` for validation tools.

