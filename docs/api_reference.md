# API Reference

Complete API documentation for HumanStudyBench.

## Core Classes

### `HumanStudyBench`

Main benchmark class for loading and evaluating studies.

**Location**: `src/core/benchmark.py`

#### Constructor

```python
HumanStudyBench(data_dir: str | Path, config: Dict[str, Any] = None)
```

**Parameters**:
- `data_dir`: Path to data directory containing studies
- `config`: Optional configuration dictionary

**Example**:
```python
from src.core.benchmark import HumanStudyBench

benchmark = HumanStudyBench(data_dir="data")
```

#### Methods

##### `load_study(study_id: str) -> Study`

Load a specific study by ID.

**Parameters**:
- `study_id`: Study identifier (e.g., "study_001")

**Returns**: `Study` object

**Raises**: `StudyNotFoundError` if study doesn't exist

**Example**:
```python
study = benchmark.load_study("study_001")
print(study.metadata["title"])
```

##### `get_studies(domain: str = None, difficulty: str = None, tags: List[str] = None) -> List[Study]`

Get filtered list of studies.

**Parameters**:
- `domain`: Filter by domain (e.g., "cognitive_psychology")
- `difficulty`: Filter by difficulty ("easy", "medium", "hard")
- `tags`: Filter by tags (list of strings)

**Returns**: List of `Study` objects

**Example**:
```python
# Get all easy cognitive psychology studies
studies = benchmark.get_studies(
    domain="cognitive_psychology",
    difficulty="easy"
)
```

##### `evaluate(agent: BaseAgent, study_ids: List[str] = None, **kwargs) -> Dict[str, Any]`

Evaluate an agent on specified studies.

**Parameters**:
- `agent`: Agent instance (must inherit from `BaseAgent`)
- `study_ids`: List of study IDs to evaluate on (None = all studies)
- `**kwargs`: Additional evaluation parameters

**Returns**: Dictionary with evaluation results

**Example**:
```python
from src.agents.llm_participant_agent import ParticipantPool

pool = ParticipantPool(study_specification, n_participants=50)
results = pool.run_experiment(trials, instructions)

# Evaluate with benchmark
from src.evaluation.scorer import Scorer
scorer = Scorer()
score, report = scorer.score_study(study, results)

print(f"Overall Score: {score:.1f}%")
print(f"Grade: {report['grade']}")
```

##### `get_registry() -> Dict[str, Any]`

Get the study registry.

**Returns**: Dictionary containing registry information

**Example**:
```python
registry = benchmark.get_registry()
print(f"Total studies: {registry['total_studies']}")
```

---

### `Study`

Represents a single study in the benchmark.

**Location**: `src/core/study.py`

#### Attributes

- `id` (str): Study identifier
- `metadata` (Dict): Study metadata
- `specification` (Dict): Experimental specification
- `ground_truth` (Dict): Original results and validation criteria
- `materials_path` (Path): Path to study materials

#### Class Methods

##### `load(study_path: Path) -> Study`

Load a study from disk.

**Parameters**:
- `study_path`: Path to study directory

**Returns**: `Study` object

**Example**:
```python
from pathlib import Path
from src.core.study import Study

study = Study.load(Path("data/studies/study_001"))
```

#### Methods

##### `get_validation_criteria() -> List[Dict]`

Get validation criteria for this study.

**Returns**: List of validation test dictionaries

##### `get_materials(material_type: str = None) -> Dict | Path`

Get study materials.

**Parameters**:
- `material_type`: Type of material ("stimuli", "instructions", etc.)

**Returns**: Path to materials or dictionary of material information

##### `validate() -> bool`

Validate study data integrity.

**Returns**: True if valid, False otherwise

**Example**:
```python
if study.validate():
    print("Study data is valid")
```

---

## Agent Interface

### `BaseAgent`

Abstract base class for all agents.

**Location**: `src/agents/base_agent.py`

#### Constructor

```python
BaseAgent(config: Dict[str, Any] = None)
```

**Parameters**:
- `config`: Optional configuration dictionary

#### Abstract Methods

##### `run_study(specification: Dict[str, Any]) -> Dict[str, Any]`

Execute a study based on specification.

**Parameters**:
- `specification`: Study specification dictionary

**Returns**: Dictionary containing study results in standardized format

**Required return format**:
```python
{
    "descriptive_statistics": {
        "variable_name": {
            "condition_1": {"mean": float, "sd": float, "n": int},
            "condition_2": {"mean": float, "sd": float, "n": int}
        }
    },
    "inferential_statistics": {
        "test_name": {
            "statistic": float,
            "p_value": float,
            "df": int | List[int],
            "effect_size": str,
            "effect_size_value": float
        }
    },
    "raw_data": List[Dict]  # Optional
}
```

**Example Implementation**:
```python
from src.agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def run_study(self, specification: Dict[str, Any]) -> Dict[str, Any]:
        # Your implementation
        design = specification["design"]
        participants = specification["participants"]
        
        # Run experiment
        results = self._execute_experiment(design, participants)
        
        return {
            "descriptive_statistics": results["descriptives"],
            "inferential_statistics": results["inferentials"]
        }
    
    def _execute_experiment(self, design, participants):
        # Your experiment logic
        pass
```

---

## Evaluation Classes

### `Scorer`

Scores agent results against ground truth.

**Location**: `src/evaluation/scorer.py`

#### Constructor

```python
Scorer(config: Dict[str, Any] = None)
```

#### Methods

##### `score_study(study: Study, agent_results: Dict) -> Dict[str, Any]`

Score agent results for a single study.

**Parameters**:
- `study`: Study object
- `agent_results`: Results returned by agent

**Returns**: Dictionary with scores and test results

**Example**:
```python
from src.evaluation.scorer import Scorer

scorer = Scorer()
score_report = scorer.score_study(study, agent_results)

print(f"Total Score: {score_report['total_score']:.2f}")
for test_name, test_result in score_report['tests'].items():
    print(f"{test_name}: {test_result['score']:.2f}")
```

##### `score_benchmark(benchmark_results: Dict) -> Dict[str, Any]`

Score agent across all benchmark studies.

**Parameters**:
- `benchmark_results`: Results from `benchmark.evaluate()`

**Returns**: Dictionary with overall scores and breakdowns

---

### `Validator`

Validates agent results and study data.

**Location**: `src/evaluation/validator.py`

#### Methods

##### `validate_results(results: Dict, schema: Dict) -> Tuple[bool, List[str]]`

Validate agent results against schema.

**Parameters**:
- `results`: Agent results dictionary
- `schema`: Expected schema

**Returns**: Tuple of (is_valid, list_of_errors)

**Example**:
```python
from src.evaluation.validator import Validator

validator = Validator()
is_valid, errors = validator.validate_results(agent_results, results_schema)

if not is_valid:
    for error in errors:
        print(f"Validation error: {error}")
```

##### `validate_study(study: Study) -> Tuple[bool, List[str]]`

Validate study data integrity.

---

### `MetricsCalculator`

Calculate statistical metrics.

**Location**: `src/evaluation/metrics.py`

#### Methods

##### `cohens_d(mean1: float, mean2: float, sd1: float, sd2: float, n1: int, n2: int) -> float`

Calculate Cohen's d effect size.

##### `eta_squared(f_stat: float, df_effect: int, df_error: int) -> float`

Calculate eta-squared effect size.

##### `confidence_interval(mean: float, se: float, confidence: float = 0.95) -> Tuple[float, float]`

Calculate confidence interval.

##### `relative_error(observed: float, expected: float) -> float`

Calculate relative error.

**Example**:
```python
from src.evaluation.metrics import MetricsCalculator

metrics = MetricsCalculator()
d = metrics.cohens_d(mean1=750, mean2=550, sd1=120, sd2=80, n1=100, n2=100)
print(f"Cohen's d: {d:.2f}")
```

---

## Utility Functions

### Data Loading

**Location**: `src/utils/loaders.py`

##### `load_json(filepath: Path) -> Dict`

Load and parse JSON file.

##### `load_study_metadata(study_path: Path) -> Dict`

Load study metadata.

##### `load_study_specification(study_path: Path) -> Dict`

Load study specification.

### Validation

**Location**: `src/utils/validators.py`

##### `validate_json_schema(data: Dict, schema: Dict) -> bool`

Validate data against JSON schema.

##### `check_required_fields(data: Dict, required_fields: List[str]) -> List[str]`

Check for required fields.

### Parsing

**Location**: `src/utils/parsers.py`

##### `parse_statistical_test(test_dict: Dict) -> StatisticalTest`

Parse statistical test from dictionary.

---

## Visualization

### `BenchmarkPlotter`

Create visualizations of benchmark results.

**Location**: `src/visualization/plots.py`

#### Methods

##### `plot_overall_scores(results: Dict, save_path: str = None)`

Plot overall benchmark scores.

##### `plot_by_domain(results: Dict, save_path: str = None)`

Plot scores by domain.

##### `plot_by_difficulty(results: Dict, save_path: str = None)`

Plot scores by difficulty level.

##### `plot_study_details(study_results: Dict, save_path: str = None)`

Plot detailed results for a single study.

**Example**:
```python
from src.visualization.plots import BenchmarkPlotter

plotter = BenchmarkPlotter()
plotter.plot_overall_scores(results, save_path="results/scores.png")
plotter.plot_by_domain(results, save_path="results/by_domain.png")
```

---

## Configuration

### Configuration Dictionary Format

```python
config = {
    "evaluation": {
        "significance_threshold": 0.05,
        "effect_size_tolerance": 0.5,
        "descriptive_tolerance": 0.20,
        "passing_threshold": 0.75
    },
    "scoring": {
        "weights": {
            "statistical_significance": 1.0,
            "effect_direction": 1.0,
            "effect_size": 1.0,
            "descriptive_similarity": 1.0
        },
        "aggregation_method": "weighted_average"
    },
    "agent": {
        "n_runs": 1,
        "random_seed": 42,
        "parallel": False
    }
}
```

---

## Exceptions

### Custom Exceptions

**Location**: `src/core/exceptions.py`

##### `StudyNotFoundError`

Raised when requested study doesn't exist.

##### `ValidationError`

Raised when data validation fails.

##### `SchemaError`

Raised when schema validation fails.

##### `AgentError`

Raised when agent execution fails.

**Example**:
```python
from src.core.exceptions import StudyNotFoundError

try:
    study = benchmark.load_study("nonexistent_study")
except StudyNotFoundError as e:
    print(f"Error: {e}")
```

---

## Type Hints

### Common Types

**Location**: `src/core/types.py`

```python
from typing import TypedDict, List, Dict, Any

class StudyMetadata(TypedDict):
    id: str
    title: str
    authors: List[str]
    year: int
    domain: str

class DescriptiveStats(TypedDict):
    mean: float
    sd: float
    n: int

class InferentialStats(TypedDict):
    statistic: float
    p_value: float
    df: int | List[int]
    effect_size: str
    effect_size_value: float
```

---

## Command Line Interface

### Run Evaluation

```bash
python -m src.cli evaluate \
    --agent my_agent \
    --study-ids study_001 study_002 \
    --output results/run_001.json
```

### Validate Study

```bash
python -m src.cli validate \
    --study-id study_001
```

### Generate Report

```bash
python -m src.cli report \
    --results results/run_001.json \
    --output results/report.html
```

---

## Examples

See `examples/` directory for complete working examples:

1. `01_load_benchmark.py` - Loading and exploring the benchmark
2. `02_run_single_study.py` - Running a single study
3. `03_evaluate_agent.py` - Full agent evaluation
4. `04_add_new_study.py` - Adding a new study
5. `05_custom_metrics.py` - Custom evaluation metrics

---

## Version History

### v0.1.0 (Current)
- Initial API design
- Core classes implemented
- Basic evaluation metrics

---

For more information, see:
- [Getting Started Guide](getting_started.md)
- [Benchmark Overview](benchmark_overview.md)
- [GitHub Repository](https://github.com/yourusername/HS_bench)
