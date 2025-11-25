"""
Study Configuration Base Class

每个 study 都应该有一个独立的配置类，完全封装：
1. Trials 生成（从 specification 到具体实验试次）
2. Prompt 构建（使用 PromptBuilder）
3. 结果聚合（计算描述性统计、效应量等）
4. 自定义评分逻辑（可选）

这样每个 study 的逻辑完全独立，易于维护和扩展。
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from pathlib import Path

from src.agents.prompt_builder import PromptBuilder


class BaseStudyConfig(ABC):
    """
    Study 配置基类
    
    每个 study 继承这个类并实现：
    - create_trials(): 生成实验 trials
    - aggregate_results(): 聚合结果（可选，有默认实现）
    - custom_scoring(): 自定义评分逻辑（可选）
    """
    
    def __init__(self, study_path: Path, specification: Dict[str, Any]):
        """
        Args:
            study_path: 研究目录路径 (e.g., data/studies/study_003/)
            specification: 研究 specification.json 内容
        """
        self.study_path = Path(study_path)
        self.specification = specification
        self.study_id = specification["study_id"]
        
        # 自动加载 prompt builder
        from src.agents.prompt_builder import create_prompt_builder
        self.prompt_builder = create_prompt_builder(study_path)
    
    @abstractmethod
    def create_trials(self, n_trials: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        根据 specification 生成实验 trials
        
        Args:
            n_trials: 试次数量（None = 使用 specification 中的默认值）
        
        Returns:
            List of trial dictionaries，每个包含：
            - trial_number: int
            - study_type: str (e.g., "framing_effect")
            - trial_type: str (e.g., "practice", "critical", "neutral")
            - 其他 study-specific 字段
        """
        raise NotImplementedError
    
    def get_prompt_builder(self) -> PromptBuilder:
        """获取 prompt builder"""
        return self.prompt_builder
    
    def get_instructions(self) -> str:
        """获取实验说明"""
        return self.prompt_builder.get_instructions()
    
    def aggregate_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        聚合实验结果
        
        默认实现：直接返回 ParticipantPool.run_experiment() 的结果
        子类可以重写以添加自定义统计分析
        
        Args:
            raw_results: ParticipantPool.run_experiment() 返回的原始结果
        
        Returns:
            聚合后的结果字典，格式：
            {
                "descriptive_statistics": {...},
                "inferential_statistics": {...},
                "individual_data": [...],
                "raw_responses": [...]
            }
        """
        return raw_results
    
    def custom_scoring(
        self, 
        results: Dict[str, Any], 
        ground_truth: Dict[str, Any]
    ) -> Optional[Dict[str, float]]:
        """
        自定义评分逻辑（可选）
        
        如果 study 需要特殊的评分逻辑，重写此方法。
        
        Args:
            results: aggregate_results() 返回的结果
            ground_truth: ground_truth.json 内容
        
        Returns:
            None（使用默认 Scorer）或自定义分数字典：
            {
                "test_name_1": 0.8,
                "test_name_2": 0.6,
                ...
            }
        """
        return None
    
    def get_n_participants(self) -> int:
        """从 specification 获取参与者数量"""
        return self.specification["participants"]["n"]
    
    def get_study_type(self) -> str:
        """获取研究类型"""
        return self.specification.get("study_type", self.study_id)
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(study_id='{self.study_id}')"


class StudyConfigRegistry:
    """
    Study 配置注册表
    
    自动发现和加载 study 配置类
    """
    
    _configs: Dict[str, type] = {}
    
    @classmethod
    def register(cls, study_id: str):
        """
        装饰器：注册 study 配置类
        
        Usage:
            @StudyConfigRegistry.register("study_003")
            class Study003Config(BaseStudyConfig):
                ...
        """
        def decorator(config_class):
            cls._configs[study_id] = config_class
            return config_class
        return decorator
    
    @classmethod
    def get_config_class(cls, study_id: str) -> Optional[type]:
        """获取配置类"""
        return cls._configs.get(study_id)
    
    @classmethod
    def create_config(
        cls, 
        study_id: str, 
        study_path: Path, 
        specification: Dict[str, Any]
    ) -> Optional[BaseStudyConfig]:
        """
        创建配置实例
        
        Args:
            study_id: 研究 ID
            study_path: 研究目录
            specification: specification.json 内容
        
        Returns:
            配置实例，如果未找到配置类则返回 None
        """
        config_class = cls.get_config_class(study_id)
        if config_class:
            return config_class(study_path, specification)
        return None
    
    @classmethod
    def list_registered_studies(cls) -> List[str]:
        """列出所有已注册的 study IDs"""
        return list(cls._configs.keys())


def get_study_config(
    study_id: str, 
    study_path: Path, 
    specification: Dict[str, Any]
) -> BaseStudyConfig:
    """
    工厂函数：根据 study_id 创建对应的配置实例
    
    Args:
        study_id: 研究 ID (e.g., "study_003")
        study_path: 研究目录
        specification: specification.json 内容
    
    Returns:
        Study 配置实例
    
    Raises:
        ValueError: 如果找不到对应的配置类
    
    Example:
        >>> config = get_study_config("study_003", Path("data/studies/study_003"), spec)
        >>> trials = config.create_trials()
        >>> builder = config.get_prompt_builder()
    """
    # Lazy import to avoid circular dependency
    # 新增 study 时在这里添加 import
    if study_id == "study_001":
        from src.studies.study_001_config import Study001Config
    elif study_id == "study_002":
        from src.studies.study_002_config import Study002Config
    elif study_id == "study_003":
        from src.studies.study_003_config import Study003Config
    elif study_id == "study_004":
        from src.studies.study_004_config import Study004Config
    elif study_id == "study_005":
        from src.studies.study_005_config import Study005Config
    elif study_id == "study_006":
        from src.studies.study_006_config import Study006Config
    
    config = StudyConfigRegistry.create_config(study_id, study_path, specification)
    
    if config is None:
        raise ValueError(
            f"No configuration found for {study_id}. "
            f"Available: {StudyConfigRegistry.list_registered_studies()}"
        )
    
    return config
