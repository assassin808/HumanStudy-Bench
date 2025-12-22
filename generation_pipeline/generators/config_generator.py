"""
Config Generator - Generates StudyConfig classes from extraction results
"""

from pathlib import Path
from typing import Dict, Any


class ConfigGenerator:
    """Generate StudyConfig classes from extraction results"""
    
    @staticmethod
    def generate(extraction_result: Dict[str, Any], study_id: str, output_path: Path) -> Path:
        """
        Generate StudyConfig class file.
        
        Args:
            extraction_result: Results from stage2 extraction
            study_id: Study ID (e.g., "study_005")
            output_path: Path to save the config file
            
        Returns:
            Path to generated config file
        """
        studies = extraction_result.get('studies', [])
        if not studies:
            raise ValueError("No studies found in extraction result")
        
        # For now, generate config for first study
        # TODO: Support multiple studies
        study = studies[0]
        
        # Generate Python code
        code = ConfigGenerator._generate_code(study, study_id)
        
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(code, encoding='utf-8')
        
        return output_path
    
    @staticmethod
    def _generate_code(study: Dict[str, Any], study_id: str) -> str:
        """Generate Python code for StudyConfig class"""
        class_name = study_id.replace('_', '').title() + "Config"
        study_id_lower = study_id.lower()
        
        # Extract basic info
        phenomenon = study.get('phenomenon', 'Unknown Phenomenon')
        participants_n = study.get('participants', {}).get('n', 100)
        
        code = f'''"""
{study_id} Configuration - Auto-generated from paper extraction

Phenomenon: {phenomenon}
"""

from typing import Dict, Any, List, Optional
from pathlib import Path

from src.core.study_config import BaseStudyConfig, StudyConfigRegistry
from src.agents.prompt_builder import PromptBuilder


@StudyConfigRegistry.register("{study_id_lower}")
class {class_name}(BaseStudyConfig):
    """
    Auto-generated study configuration.
    
    Phenomenon: {phenomenon}
    """
    
    def create_trials(self, n_trials: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Generate experiment trials.
        
        Args:
            n_trials: Number of trials (None = use default from specification)
            
        Returns:
            List of trial dictionaries
        """
        # TODO: Implement trial generation based on extracted design
        # This is a template - needs manual refinement based on study design
        
        trials = []
        n = n_trials or self.get_n_participants()
        
        for i in range(n):
            trials.append({{
                "trial_number": i + 1,
                "study_type": "{study_id_lower}",
                "trial_type": "critical"
            }})
        
        return trials
    
    def aggregate_results(self, raw_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aggregate experiment results.
        
        Args:
            raw_results: Raw results from ParticipantPool.run_experiment()
            
        Returns:
            Aggregated results with descriptive and inferential statistics
        """
        # TODO: Implement result aggregation based on extracted statistical methods
        # This is a template - needs manual refinement based on study design
        
        # Default: return raw results
        return raw_results
'''
        
        return code

