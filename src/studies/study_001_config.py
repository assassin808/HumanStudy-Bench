"""
Study 001 Configuration - Asch Conformity Experiment (1952)

完整封装 Asch 实验的所有逻辑：
- Trials 生成：18 trials (2 practice + 12 critical + 4 neutral)
- Prompt 构建：使用 AschPromptBuilder
- 结果聚合：计算 conformity rate、个体差异等
- 自定义统计：效应量计算、分布分析
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np

from src.core.study_config import BaseStudyConfig, StudyConfigRegistry


@StudyConfigRegistry.register("study_001")
class Study001Config(BaseStudyConfig):
    """
    Asch Conformity Experiment (1952) 配置
    
    经典从众实验：参与者判断线段长度，6个confederates 故意给错误答案。
    """
    
    def __init__(self, study_path: Path, specification: Dict[str, Any]):
        super().__init__(study_path, specification)
        
        # Asch 实验特定参数
        self.n_confederates = 6  # 标准 Asch 实验有 6 个confederates
        self.n_practice_trials = 2
        self.n_critical_trials = 12
        self.n_neutral_trials = 4
        self.total_trials = self.n_practice_trials + self.n_critical_trials + self.n_neutral_trials
    
    def create_trials(self, n_trials: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        生成 Asch 实验的 18 个 trials
        
        结构：
        - Trials 1-2: Practice (neutral, no confederates)
        - Trials 3-18: 12 critical + 4 neutral mixed
        
        Args:
            n_trials: 忽略，Asch 实验固定 18 trials
        
        Returns:
            18 个 trial dictionaries
        """
        trials = []
        
        # Practice trials (1-2): Neutral, correct judgment, no confederates
        for i in range(1, self.n_practice_trials + 1):
            standard = 8 + i  # 9, 10 inches
            trials.append({
                "trial_number": i,
                "study_type": "asch_conformity",
                "trial_type": "practice",
                "standard_line_length": standard,
                "comparison_lines": {
                    "A": standard - 2,
                    "B": standard,      # Correct
                    "C": standard + 3
                },
                "correct_answer": "B",
                "confederate_responses": []  # No confederates in practice
            })
        
        # Main trials (3-18): Mix of critical and neutral
        # Pattern: [N, N, C, C, N, C, C, N, C, C, N, C, C, N, C, C]
        # N = neutral (no confederates), C = critical (confederates give wrong answer)
        critical_pattern = [
            False, False,  # 3-4: neutral
            True, True,    # 5-6: critical
            False,         # 7: neutral
            True, True,    # 8-9: critical
            False,         # 10: neutral
            True, True,    # 11-12: critical
            False,         # 13: neutral
            True,          # 14: critical
            True, False,   # 15-16: critical, neutral
            True, True     # 17-18: critical
        ]
        
        for idx, is_critical in enumerate(critical_pattern):
            trial_num = idx + self.n_practice_trials + 1
            
            # Vary line lengths
            standard = 8 + (idx % 4)  # Cycles through 8, 9, 10, 11
            
            if is_critical:
                # Critical trial: confederates unanimously give wrong answer
                # Alternate between "too short" (A) and "too long" (C)
                wrong_answer = "A" if idx % 2 == 0 else "C"
                confederates = [wrong_answer] * self.n_confederates
            else:
                # Neutral trial: no confederate responses
                confederates = []
            
            trials.append({
                "trial_number": trial_num,
                "study_type": "asch_conformity",
                "trial_type": "critical" if is_critical else "neutral",
                "standard_line_length": standard,
                "comparison_lines": {
                    "A": standard - 2,   # Too short
                    "B": standard,       # Correct
                    "C": standard + 3    # Too long
                },
                "correct_answer": "B",
                "confederate_responses": confederates
            })
        
        return trials
    
    def aggregate_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Asch 特定的结果聚合
        
        计算：
        1. Conformity rate (critical trials 的错误率)
        2. 个体差异（never/always conformed）
        3. Trial-by-trial conformity pattern
        4. Accuracy on neutral trials
        
        Args:
            raw_results: ParticipantPool.run_experiment() 返回的原始结果
        
        Returns:
            增强的结果字典，包含 Asch 特定的分析
        """
        # 从原始结果获取个体数据
        individual_data = raw_results.get("individual_data", [])
        raw_responses = raw_results.get("raw_responses", [])
        
        if not individual_data:
            return raw_results
        
        n_participants = len(individual_data)
        
        # 计算 conformity statistics
        conformity_rates = []
        never_conformed_count = 0
        always_conformed_count = 0
        
        for participant in individual_data:
            conf_rate = participant.get("conformity_rate")
            if conf_rate is not None:
                conformity_rates.append(conf_rate)
                if conf_rate == 0.0:
                    never_conformed_count += 1
                elif conf_rate == 1.0:
                    always_conformed_count += 1
        
        # 描述性统计
        if conformity_rates:
            conformity_stats = {
                "n": len(conformity_rates),
                "mean": float(np.mean(conformity_rates)),
                "sd": float(np.std(conformity_rates, ddof=1) if len(conformity_rates) > 1 else 0),
                "median": float(np.median(conformity_rates)),
                "min": float(np.min(conformity_rates)),
                "max": float(np.max(conformity_rates)),
                "never_conformed": never_conformed_count,
                "always_conformed": always_conformed_count,
                "at_least_once": len([r for r in conformity_rates if r > 0])
            }
        else:
            conformity_stats = {}
        
        # Trial-by-trial analysis（可选）
        trial_conformity = self._analyze_trial_patterns(raw_responses)
        
        # 构建增强的结果
        enhanced_results = {
            "descriptive_statistics": {
                "conformity_rate": {
                    "experimental": conformity_stats
                },
                "trial_patterns": trial_conformity
            },
            "inferential_statistics": raw_results.get("inferential_statistics", {}),
            "individual_data": individual_data,
            "raw_responses": raw_responses,
            "study_specific": {
                "n_critical_trials": self.n_critical_trials,
                "n_neutral_trials": self.n_neutral_trials,
                "n_confederates": self.n_confederates
            }
        }
        
        return enhanced_results
    
    def _analyze_trial_patterns(self, raw_responses: List[List[Dict]]) -> Dict[str, Any]:
        """
        分析 trial-by-trial 的从众模式
        
        Args:
            raw_responses: 每个参与者的所有 trial 响应
        
        Returns:
            Trial pattern 分析结果
        """
        if not raw_responses:
            return {}
        
        # 统计每个 trial 的从众率
        trial_conformity_rates = {}
        
        for trial_num in range(1, self.total_trials + 1):
            trial_responses = []
            
            for participant_responses in raw_responses:
                for response in participant_responses:
                    if response.get("trial_number") == trial_num:
                        # Critical trial 上的错误 = 从众
                        trial_info = response.get("trial_info", {})
                        if trial_info.get("trial_type") == "critical":
                            is_correct = response.get("is_correct", True)
                            trial_responses.append(0 if is_correct else 1)  # 1 = conformed
            
            if trial_responses:
                trial_conformity_rates[f"trial_{trial_num}"] = {
                    "conformity_rate": float(np.mean(trial_responses)),
                    "n": len(trial_responses)
                }
        
        return trial_conformity_rates
    
    def custom_scoring(
        self, 
        results: Dict[str, Any], 
        ground_truth: Dict[str, Any]
    ) -> Optional[Dict[str, float]]:
        """
        Asch 自定义评分（可选）
        
        这里可以实现比默认 Scorer 更复杂的评分逻辑。
        目前返回 None 使用默认 Scorer。
        
        Future: 可以添加：
        - Effect size 计算 (Cohen's d)
        - Distribution similarity (Kolmogorov-Smirnov test)
        - Pattern matching (trial-by-trial correlation)
        """
        return None
    
    def get_expected_conformity_rate(self) -> float:
        """从 ground truth 获取预期从众率"""
        return self.specification.get(
            "expected_results", {}
        ).get(
            "conformity_rate_mean", 0.37
        )
    
    def get_critical_trials_indices(self) -> List[int]:
        """获取 critical trials 的索引（1-based）"""
        trials = self.create_trials()
        return [
            t["trial_number"] 
            for t in trials 
            if t["trial_type"] == "critical"
        ]
    
    def __repr__(self) -> str:
        return (
            f"Study001Config(Asch Conformity, "
            f"{self.total_trials} trials: "
            f"{self.n_practice_trials}P + {self.n_critical_trials}C + {self.n_neutral_trials}N)"
        )
