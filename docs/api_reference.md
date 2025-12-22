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

> **Note**: The `Validator` class is not yet implemented in the current version. Study validation is handled through the `Study.validate()` method and schema validation in the core modules.

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

> **Note**: Utility functions for data loading, validation, and parsing are currently integrated into the core modules (`Study`, `HumanStudyBench`) rather than being in separate utility modules. JSON loading is handled directly in the core classes.

---

## Visualization

> **Note**: Visualization functionality is not yet implemented in the current version. Results are available as structured dictionaries that can be visualized using external plotting libraries (matplotlib, plotly, etc.) or by using the `evaluate_results.py` script for result analysis.

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

> **Note**: Type hints are defined inline in the source code rather than in a separate `types.py` module. See the actual class definitions in `src/core/study.py`, `src/core/benchmark.py`, and `src/evaluation/scorer.py` for type information.

---

## Command Line Interface

> **Note**: A dedicated CLI module is not yet implemented. Instead, use the following scripts:
> - `run_full_benchmark.py` - Run experiments on studies
> - `evaluate_results.py` - Evaluate cached results without making API calls
> - `validation_pipeline/run_validation.py` - Validate study data

**Example**:
```bash
# Run full benchmark
python run_full_benchmark.py --real-llm --model mistralai/mistral-nemo

# Evaluate cached results
python evaluate_results.py --results-dir results/cache
```

---

## Examples

> **Note**: Example scripts are not yet in a dedicated `examples/` directory. See the main scripts for usage:
> - `run_full_benchmark.py` - Complete benchmark execution
> - `evaluate_results.py` - Result evaluation and analysis
> 
> For detailed usage examples, see:
> - [Getting Started Guide](getting_started.md)
> - [LLM Participant Agent Guide](llm_participant_agent_guide.md)
> - [Study Config Guide](study_config_guide.md)

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
