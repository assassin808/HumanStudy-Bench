# API Reference

## Core Classes

### `HumanStudyBench`

```python
from src.core.benchmark import HumanStudyBench

benchmark = HumanStudyBench(data_dir="data")
study = benchmark.load_study("study_001")
studies = benchmark.get_studies(domain="cognitive_psychology")
results = benchmark.evaluate(agent, study_ids=["study_001"])
```

**Methods:**
- `load_study(study_id: str) -> Study`
- `get_studies(domain=None, difficulty=None, tags=None) -> List[Study]`
- `evaluate(agent, study_ids=None) -> Dict`
- `get_registry() -> Dict`

### `Study`

```python
from src.core.study import Study

study = Study.load(Path("data/studies/study_001"))
```

**Attributes:** `id`, `metadata`, `specification`, `ground_truth`, `materials_path`

**Methods:**
- `get_validation_criteria() -> List[Dict]`
- `get_materials(material_type=None) -> Dict | Path`
- `validate() -> bool`

### `ParticipantPool`

```python
from src.agents.llm_participant_agent import ParticipantPool

pool = ParticipantPool(
    study_specification=study.specification,
    n_participants=50,
    use_real_llm=True,
    model="mistralai/mistral-nemo"
)
results = pool.run_experiment(trials, instructions)
```

### `Scorer`

```python
from src.evaluation.scorer import Scorer

scorer = Scorer()
score_report = scorer.score_study(study, agent_results)
```

**Returns:** Dictionary with `total_score`, `phenomenon_result`, `data_result`, `tests`

### `MetricsCalculator`

```python
from src.evaluation.metrics import MetricsCalculator

metrics = MetricsCalculator()
d = metrics.cohens_d(mean1, mean2, sd1, sd2, n1, n2)
eta = metrics.eta_squared(f_stat, df_effect, df_error)
ci = metrics.confidence_interval(mean, se)
```

## Exceptions

```python
from src.core.exceptions import (
    StudyNotFoundError,
    ValidationError,
    SchemaError,
    AgentError
)
```

## Configuration

```python
config = {
    "evaluation": {
        "significance_threshold": 0.05,
        "effect_size_tolerance": 0.5,
        "descriptive_tolerance": 0.20,
        "passing_threshold": 0.75
    }
}
```
