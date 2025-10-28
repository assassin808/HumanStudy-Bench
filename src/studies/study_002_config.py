"""
Study 002 Configuration - Milgram Obedience Experiment (1963)

完整封装 Milgram 实验的所有逻辑：
- Trials 生成：30 shock levels (15V to 450V)
- Prompt 构建：使用 MilgramPromptBuilder
- 结果聚合：计算 obedience rate、停止点统计等
- 自定义评分：Shock level 分布比较
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
import numpy as np

from src.core.study_config import BaseStudyConfig, StudyConfigRegistry


@StudyConfigRegistry.register("study_002")
class Study002Config(BaseStudyConfig):
    """
    Milgram Obedience Experiment (1963) 配置
    
    经典服从权威实验：参与者作为"老师"，实验者要求对"学习者"施加递增电击。
    """
    
    def __init__(self, study_path: Path, specification: Dict[str, Any]):
        super().__init__(study_path, specification)
        
        # Milgram 实验特定参数
        self.start_voltage = 15
        self.max_voltage = 450
        self.voltage_increment = 15
        self.n_shock_levels = 30  # (450 - 15) / 15 + 1 = 30
        
        # Shock level labels (从 specification 读取)
        self.shock_labels = self._get_shock_labels()
    
    def _get_shock_labels(self) -> Dict[int, str]:
        """从 specification 读取 shock level 标签"""
        labels = {}
        
        # 从 specification 的 shock_generator 读取
        shock_gen = self.specification.get("materials", {}).get("shock_generator", {})
        levels = shock_gen.get("levels", [])
        
        for level_info in levels:
            voltage = level_info.get("voltage")
            label = level_info.get("label", "")
            if voltage:
                labels[voltage] = label
        
        # 如果没有从 spec 读取到，使用默认标签
        if not labels:
            labels = {
                15: "Slight Shock", 30: "Slight Shock",
                45: "Slight Shock", 60: "Slight Shock",
                75: "Moderate Shock", 90: "Moderate Shock",
                105: "Moderate Shock", 120: "Moderate Shock",
                135: "Strong Shock", 150: "Strong Shock",
                165: "Strong Shock", 180: "Strong Shock",
                195: "Very Strong Shock", 210: "Very Strong Shock",
                225: "Very Strong Shock", 240: "Very Strong Shock",
                255: "Intense Shock", 270: "Intense Shock",
                285: "Intense Shock", 300: "Intense Shock",
                315: "Extreme Intensity Shock", 330: "Extreme Intensity Shock",
                345: "Extreme Intensity Shock", 360: "Extreme Intensity Shock",
                375: "Danger: Severe Shock", 390: "Danger: Severe Shock",
                405: "Danger: Severe Shock", 420: "Danger: Severe Shock",
                435: "XXX", 450: "XXX"
            }
        
        return labels
    
    def create_trials(self, n_trials: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        生成 Milgram 实验的 30 个 trials (shock levels)
        
        每个 trial = 一个 shock level，参与者可以选择 continue 或 stop。
        
        Args:
            n_trials: 可选，限制 trial 数量（用于快速测试）
        
        Returns:
            30 个（或 n_trials 个）trial dictionaries
        """
        trials = []
        
        total_trials = n_trials if n_trials else self.n_shock_levels
        
        for i in range(total_trials):
            voltage = self.start_voltage + (i * self.voltage_increment)
            label = self.shock_labels.get(voltage, "")
            
            trials.append({
                "trial_number": i + 1,
                "study_type": "milgram_obedience",
                "shock_level": i + 1,
                "voltage": voltage,
                "label": label,
                "experimenter_instruction": self._get_experimenter_prod(i + 1),
                "learner_response": self._get_learner_response(voltage)
            })
        
        return trials
    
    def _get_experimenter_prod(self, trial_number: int) -> str:
        """
        获取实验者的 prod（催促语句）
        
        Milgram 使用 4 个递进的 prods：
        1. "Please continue."
        2. "The experiment requires that you continue."
        3. "It is absolutely essential that you continue."
        4. "You have no other choice, you must go on."
        
        Args:
            trial_number: Trial 编号（用于决定 prod 强度）
        
        Returns:
            Experimenter prod 文本
        """
        # 简化：根据 trial 阶段选择 prod
        if trial_number <= 10:
            return "Please continue."
        elif trial_number <= 20:
            return "The experiment requires that you continue."
        elif trial_number <= 25:
            return "It is absolutely essential that you continue."
        else:
            return "You have no other choice, you must go on."
    
    def _get_learner_response(self, voltage: int) -> str:
        """
        获取 learner 的反应（从 specification 读取或使用默认）
        
        Args:
            voltage: 电击电压
        
        Returns:
            Learner 反应描述
        """
        # 简化版本，实际应从 materials/learner_responses.txt 读取
        if voltage < 75:
            return "Ugh!"
        elif voltage < 150:
            return "Ugh! That really hurts!"
        elif voltage < 270:
            return "Ugh! I can't stand the pain! Let me out!"
        elif voltage < 330:
            return "Ugh!!! Let me out! My heart's bothering me!"
        elif voltage < 375:
            return "[Agonized scream] I absolutely refuse to answer!"
        else:
            return "[Silence]"
    
    def aggregate_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Milgram 特定的结果聚合
        
        计算：
        1. Obedience rate (完成到 450V 的参与者比例)
        2. Mean maximum shock level
        3. Stop point 分布
        4. Defiance rate (每个 shock level)
        
        Args:
            raw_results: ParticipantPool.run_experiment() 返回的原始结果
        
        Returns:
            增强的结果字典，包含 Milgram 特定的分析
        """
        individual_data = raw_results.get("individual_data", [])
        raw_responses = raw_results.get("raw_responses", [])
        
        if not individual_data:
            return raw_results
        
        n_participants = len(individual_data)
        
        # 提取 maximum shock levels
        max_shocks = []
        obedience_count = 0
        stop_points = []
        
        for participant in individual_data:
            max_shock = participant.get("max_shock_level", 0)
            if max_shock > 0:
                max_shocks.append(max_shock)
                
                # Obedience = reached 450V (level 30)
                if max_shock == 30:
                    obedience_count += 1
                else:
                    stop_points.append(max_shock)
        
        # 计算统计量
        obedience_rate = obedience_count / n_participants if n_participants > 0 else 0
        
        shock_stats = {}
        if max_shocks:
            shock_stats = {
                "n": len(max_shocks),
                "mean": float(np.mean(max_shocks)),
                "sd": float(np.std(max_shocks, ddof=1) if len(max_shocks) > 1 else 0),
                "median": float(np.median(max_shocks)),
                "min": int(np.min(max_shocks)),
                "max": int(np.max(max_shocks)),
                "obedient_count": obedience_count,
                "obedience_rate": obedience_rate,
                "defiant_count": len(stop_points)
            }
        
        # Stop point 分布
        stop_distribution = self._analyze_stop_distribution(stop_points)
        
        # Trial-by-trial defiance rate
        trial_defiance = self._analyze_trial_defiance(raw_responses)
        
        # 构建增强的结果
        enhanced_results = {
            "descriptive_statistics": {
                "obedience_rate": {
                    "experimental": obedience_rate
                },
                "shock_level": {
                    "experimental": shock_stats
                },
                "stop_distribution": stop_distribution,
                "trial_defiance": trial_defiance
            },
            "inferential_statistics": raw_results.get("inferential_statistics", {}),
            "individual_data": individual_data,
            "raw_responses": raw_responses,
            "study_specific": {
                "n_shock_levels": self.n_shock_levels,
                "max_voltage": self.max_voltage,
                "voltage_increment": self.voltage_increment
            }
        }
        
        return enhanced_results
    
    def _analyze_stop_distribution(self, stop_points: List[int]) -> Dict[str, Any]:
        """
        分析 stop point 分布（按电压范围分组）
        
        Args:
            stop_points: 停止的 shock levels
        
        Returns:
            按范围分组的统计
        """
        if not stop_points:
            return {}
        
        # 定义电压范围
        ranges = {
            "slight_moderate": (1, 8),      # 15V - 120V
            "strong": (9, 12),               # 135V - 180V
            "very_strong": (13, 16),         # 195V - 240V
            "intense": (17, 20),             # 255V - 300V
            "extreme": (21, 24),             # 315V - 360V
            "danger": (25, 28),              # 375V - 420V
            "xxx": (29, 30)                  # 435V - 450V
        }
        
        distribution = {}
        for range_name, (min_level, max_level) in ranges.items():
            count = len([sp for sp in stop_points if min_level <= sp <= max_level])
            if count > 0:
                distribution[range_name] = {
                    "count": count,
                    "percentage": count / len(stop_points) * 100
                }
        
        return distribution
    
    def _analyze_trial_defiance(self, raw_responses: List[List[Dict]]) -> Dict[str, Any]:
        """
        分析每个 trial (shock level) 的 defiance rate
        
        Args:
            raw_responses: 每个参与者的所有 trial 响应
        
        Returns:
            Trial-by-trial defiance 统计
        """
        if not raw_responses:
            return {}
        
        trial_defiance = {}
        
        for trial_num in range(1, self.n_shock_levels + 1):
            stopped_count = 0
            continued_count = 0
            
            for participant_responses in raw_responses:
                for response in participant_responses:
                    if response.get("trial_number") == trial_num:
                        decision = response.get("response", "").lower()
                        if "stop" in decision or "refuse" in decision:
                            stopped_count += 1
                        elif "continue" in decision:
                            continued_count += 1
            
            total = stopped_count + continued_count
            if total > 0:
                trial_defiance[f"level_{trial_num}"] = {
                    "stopped": stopped_count,
                    "continued": continued_count,
                    "defiance_rate": stopped_count / total
                }
        
        return trial_defiance
    
    def custom_scoring(
        self, 
        results: Dict[str, Any], 
        ground_truth: Dict[str, Any]
    ) -> Optional[Dict[str, float]]:
        """
        Milgram 自定义评分（可选）
        
        可以实现：
        - Shock level distribution 的 KS test
        - Stop point pattern matching
        - Obedience rate 的置信区间
        
        目前返回 None 使用默认 Scorer
        """
        return None
    
    def get_expected_obedience_rate(self) -> float:
        """从 ground truth 获取预期服从率"""
        return self.specification.get(
            "expected_results", {}
        ).get(
            "obedience_rate", 0.65
        )
    
    def get_shock_label(self, voltage: int) -> str:
        """获取指定电压的标签"""
        return self.shock_labels.get(voltage, "Unknown")
    
    def __repr__(self) -> str:
        return (
            f"Study002Config(Milgram Obedience, "
            f"{self.n_shock_levels} shock levels: "
            f"{self.start_voltage}V - {self.max_voltage}V)"
        )
