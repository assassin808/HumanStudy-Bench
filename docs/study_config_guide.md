# Study Configuration System Guide

## 概述

从 v0.3.0 开始，HumanStudyBench 采用模块化的 **Per-Study Configuration** 架构。每个 study 都有独立的配置文件，完全封装：

1. **Trials 生成**：从 specification 到具体的实验试次
2. **Prompt 构建**：使用 PromptBuilder 生成参与者指令
3. **结果聚合**：计算描述性统计、效应量等
4. **自定义评分**：可选的 study-specific scoring logic

## 架构优势

### ✅ 模块化
- 每个 study 逻辑完全独立
- 不影响其他 studies

### ✅ 易扩展
- 添加新 study 只需创建一个配置文件
- 注册系统自动发现

### ✅ 清晰的关注点分离
- Study-specific logic 不污染共享代码
- 易于维护和测试

## 快速开始：添加新 Study

### Step 1: 创建配置文件

在 `src/studies/` 目录创建 `study_XXX_config.py`：

```python
"""
Study XXX Configuration - [Study Title]

完整封装 [Study Name] 实验的所有逻辑
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np

from src.core.study_config import BaseStudyConfig, StudyConfigRegistry


@StudyConfigRegistry.register("study_XXX")
class StudyXXXConfig(BaseStudyConfig):
    """
    [Study Name] 配置
    
    [Brief description of the study]
    """
    
    def __init__(self, study_path: Path, specification: Dict[str, Any]):
        super().__init__(study_path, specification)
        
        # Study-specific parameters
        self.param1 = specification.get("param1", default_value)
        self.param2 = specification.get("param2", default_value)
    
    def create_trials(self, n_trials: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        生成实验 trials
        
        Args:
            n_trials: 可选，限制 trial 数量
        
        Returns:
            Trial dictionaries 列表
        """
        trials = []
        
        # TODO: Implement trial generation logic
        # Example:
        for i in range(n_trials or self.default_n_trials):
            trials.append({
                "trial_number": i + 1,
                "study_type": "your_study_type",
                # ... study-specific fields
            })
        
        return trials
    
    def aggregate_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Study-specific 结果聚合
        
        Args:
            raw_results: ParticipantPool.run_experiment() 返回的原始结果
        
        Returns:
            增强的结果字典，包含 study-specific 分析
        """
        # Extract individual data
        individual_data = raw_results.get("individual_data", [])
        raw_responses = raw_results.get("raw_responses", [])
        
        # TODO: Compute study-specific statistics
        # Example: calculate main dependent variable
        
        enhanced_results = {
            "descriptive_statistics": {
                "main_metric": {
                    "experimental": {
                        "mean": 0.0,
                        "sd": 0.0,
                        # ...
                    }
                }
            },
            "inferential_statistics": raw_results.get("inferential_statistics", {}),
            "individual_data": individual_data,
            "raw_responses": raw_responses,
            "study_specific": {
                # Study-specific metadata
            }
        }
        
        return enhanced_results
    
    def custom_scoring(
        self, 
        results: Dict[str, Any], 
        ground_truth: Dict[str, Any]
    ) -> Optional[Dict[str, float]]:
        """
        自定义评分逻辑（可选）
        
        如果需要比默认 Scorer 更复杂的评分，实现此方法。
        
        Returns:
            None（使用默认 Scorer）或自定义分数字典
        """
        return None  # Use default scorer
    
    def __repr__(self) -> str:
        return f"StudyXXXConfig([Study Name], ...)"
```

### Step 2: 注册配置

在 `src/core/study_config.py` 的 `get_study_config()` 函数添加 lazy import：

```python
def get_study_config(
    study_id: str, 
    study_path: Path, 
    specification: Dict[str, Any]
) -> BaseStudyConfig:
    # ...
    
    # 添加新 study 的 import
    if study_id == "study_XXX":
        from src.studies.study_XXX_config import StudyXXXConfig
    
    # ...
```

### Step 3: 测试

```bash
# 测试单个 study
python run_full_benchmark.py --studies study_XXX

# 测试所有 studies
python run_full_benchmark.py
```

## 详细示例：Asch Conformity Study

### 1. Study 001 Config Structure

```python
@StudyConfigRegistry.register("study_001")
class Study001Config(BaseStudyConfig):
    def __init__(self, study_path: Path, specification: Dict[str, Any]):
        super().__init__(study_path, specification)
        
        # Asch-specific parameters
        self.n_confederates = 6
        self.n_practice_trials = 2
        self.n_critical_trials = 12
        self.n_neutral_trials = 4
        self.total_trials = 18
```

### 2. Trials Generation

Asch 实验生成 18 个 trials：
- 2 practice trials（中立，无 confederates）
- 12 critical trials（confederates 一致给错误答案）
- 4 neutral trials（无 confederates）

```python
def create_trials(self, n_trials: Optional[int] = None) -> List[Dict[str, Any]]:
    trials = []
    
    # Practice trials
    for i in range(1, self.n_practice_trials + 1):
        trials.append({
            "trial_number": i,
            "study_type": "asch_conformity",
            "trial_type": "practice",
            "standard_line_length": 8 + i,
            "comparison_lines": {"A": 7, "B": 9 + i, "C": 12},
            "correct_answer": "B",
            "confederate_responses": []
        })
    
    # Main trials: mix of critical and neutral
    # ...
    
    return trials
```

### 3. Result Aggregation

计算 Asch-specific 统计量：

```python
def aggregate_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
    # Calculate conformity rate
    conformity_rates = [p.get("conformity_rate") for p in individual_data]
    
    conformity_stats = {
        "mean": float(np.mean(conformity_rates)),
        "sd": float(np.std(conformity_rates, ddof=1)),
        "never_conformed": count_never,
        "always_conformed": count_always,
        # ...
    }
    
    return {
        "descriptive_statistics": {
            "conformity_rate": {"experimental": conformity_stats}
        },
        # ...
    }
```

## API Reference

### BaseStudyConfig

所有 study configs 的基类。

**必须实现的方法**：
- `create_trials(n_trials=None) -> List[Dict]`: 生成实验 trials

**可选重写的方法**：
- `aggregate_results(raw_results) -> Dict`: 聚合结果
- `custom_scoring(results, ground_truth) -> Optional[Dict]`: 自定义评分

**工具方法**：
- `get_prompt_builder() -> PromptBuilder`: 获取 prompt builder
- `get_instructions() -> str`: 读取实验指令
- `get_n_participants() -> int`: 获取参与者数量
- `get_study_type() -> str`: 获取研究类型

### StudyConfigRegistry

配置注册表，自动管理所有 study configs。

**装饰器**：
```python
@StudyConfigRegistry.register("study_ID")
class StudyConfig(BaseStudyConfig):
    pass
```

**方法**：
- `get_config_class(study_id) -> type`: 获取配置类
- `create_config(study_id, study_path, spec) -> BaseStudyConfig`: 创建实例
- `list_registered_studies() -> List[str]`: 列出已注册的 studies

### get_study_config()

工厂函数，根据 study_id 创建配置实例。

```python
config = get_study_config(
    study_id="study_001",
    study_path=Path("data/studies/study_001"),
    specification=spec
)

trials = config.create_trials()
results = config.aggregate_results(raw_results)
```

## Trial 格式规范

每个 trial 是一个字典，必须包含：

```python
{
    "trial_number": int,      # 1-based trial number
    "study_type": str,        # e.g., "asch_conformity", "milgram_obedience"
    
    # Study-specific fields
    # For Asch:
    "trial_type": str,                # "practice", "critical", "neutral"
    "standard_line_length": float,
    "comparison_lines": Dict[str, float],
    "correct_answer": str,
    "confederate_responses": List[str],
    
    # For Milgram:
    "shock_level": int,
    "voltage": int,
    "label": str,
    "experimenter_instruction": str,
    "learner_response": str,
}
```

## Result 格式规范

`aggregate_results()` 应返回：

```python
{
    "descriptive_statistics": {
        "main_metric": {
            "experimental": {
                "n": int,
                "mean": float,
                "sd": float,
                "median": float,
                "min": float,
                "max": float,
                # Study-specific fields
            }
        },
        # Other metrics
    },
    "inferential_statistics": {
        # T-tests, chi-square, etc.
    },
    "individual_data": List[Dict],  # Per-participant data
    "raw_responses": List[List[Dict]],  # All trial responses
    "study_specific": {
        # Study-specific metadata
    }
}
```

## 最佳实践

### 1. 参数化配置

不要硬编码数字，从 specification 读取：

```python
def __init__(self, study_path: Path, specification: Dict[str, Any]):
    super().__init__(study_path, specification)
    
    # Read from specification
    self.n_trials = specification.get("procedure", {}).get("n_trials", 20)
    self.trial_duration = specification["timing"]["trial_duration"]
```

### 2. 健壮的错误处理

```python
def aggregate_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
    individual_data = raw_results.get("individual_data", [])
    
    if not individual_data:
        # Return minimal valid structure
        return raw_results
    
    # Process data...
```

### 3. 清晰的文档

```python
def create_trials(self, n_trials: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    生成实验 trials
    
    Structure:
    - Trials 1-5: Practice phase
    - Trials 6-20: Main experimental phase
    
    Args:
        n_trials: 可选，限制 trial 数量（用于快速测试）
    
    Returns:
        List of trial dictionaries with structure:
        {
            "trial_number": int,
            "condition": str,  # "control" or "experimental"
            ...
        }
    """
```

### 4. 可测试性

```python
# In your config class
def get_expected_main_metric(self) -> float:
    """从 specification 获取预期指标"""
    return self.specification.get("expected_results", {}).get("main_metric", 0.5)

def get_critical_trials_indices(self) -> List[int]:
    """获取关键 trials 的索引（方便测试）"""
    return [t["trial_number"] for t in self.create_trials() 
            if t.get("is_critical")]
```

## 现有 Studies

### Study 001: Asch Conformity (1952)
- **Config**: `src/studies/study_001_config.py`
- **Trials**: 18 (2 practice + 12 critical + 4 neutral)
- **Main Metric**: Conformity rate on critical trials
- **Features**: 
  - 6 confederates giving unanimous wrong answers
  - Trial-by-trial conformity pattern analysis
  - Individual differences (never/always conformed)

### Study 002: Milgram Obedience (1963)
- **Config**: `src/studies/study_002_config.py`
- **Trials**: 30 shock levels (15V to 450V)
- **Main Metric**: Obedience rate (% reaching 450V)
- **Features**:
  - Shock level labels (Slight → Danger → XXX)
  - Stop point distribution analysis
  - Trial-by-trial defiance rates
  - Learner responses (ugh → screams → silence)

## 故障排除

### ImportError: circular import

**问题**: Study config imports `BaseStudyConfig`，而 `study_config.py` imports study configs。

**解决**: 使用 lazy import 在 `get_study_config()` 内部导入：

```python
def get_study_config(study_id, study_path, specification):
    if study_id == "study_XXX":
        from src.studies.study_XXX_config import StudyXXXConfig
    # ...
```

### ValueError: No configuration found

**问题**: Study config 没有被注册。

**解决**:
1. 确保使用 `@StudyConfigRegistry.register("study_ID")` 装饰器
2. 在 `get_study_config()` 添加 lazy import
3. Study ID 必须完全匹配（包括大小写）

### Results 不包含 study-specific 字段

**问题**: `aggregate_results()` 没有正确调用。

**解决**: 检查 `run_full_benchmark.py` 使用：

```python
raw_results = pool.run_experiment(...)
results = study_config.aggregate_results(raw_results)  # Must call this!
```

## 总结

Per-Study Configuration 系统提供：

✅ **完全模块化** - 每个 study 独立封装  
✅ **易于扩展** - 添加新 study 只需一个文件  
✅ **类型安全** - 明确的接口和类型提示  
✅ **可测试** - 每个 config 可以独立测试  
✅ **灵活** - 支持 study-specific 自定义逻辑  

开始创建你的第一个 study config 吧！🚀
