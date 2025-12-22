"""
Main Validation Pipeline Orchestrator

Coordinates all validation agents to perform comprehensive study validation.
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from validation_pipeline.utils.document_loader import DocumentLoader
from validation_pipeline.utils.gemini_client import GeminiClient
from validation_pipeline.agents import (
    ExperimentCompletenessAgent,
    ExperimentConsistencyAgent,
    DataValidationAgent,
    ChecklistGeneratorAgent,
)


class ValidationPipeline:
    """Main pipeline orchestrator for study validation"""
    
    def __init__(
        self,
        model: str = "models/gemini-3-flash-preview",
        api_key: Optional[str] = None,
        output_dir: Optional[Path] = None,
    ):
        """
        Initialize validation pipeline.
        
        Args:
            model: Gemini model to use
            api_key: Optional API key (if None, reads from env)
            output_dir: Directory to save validation results
        """
        self.model = model
        self.client = GeminiClient(model=model, api_key=api_key)
        self.output_dir = Path(output_dir) if output_dir else Path("validation_pipeline/outputs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize agents
        self.completeness_agent = ExperimentCompletenessAgent(gemini_client=self.client)
        self.consistency_agent = ExperimentConsistencyAgent(gemini_client=self.client)
        self.data_agent = DataValidationAgent(gemini_client=self.client)
        self.checklist_agent = ChecklistGeneratorAgent(gemini_client=self.client)
    
    def validate_study(
        self,
        study_id: str,
        study_path: Optional[Path] = None,
        config_path: Optional[Path] = None,
        save_results: bool = True,
    ) -> Dict[str, Any]:
        """
        Validate a study.
        
        Args:
            study_id: Study ID (e.g., "study_001")
            study_path: Path to study directory (if None, constructs from study_id)
            config_path: Path to study config Python file
            save_results: Whether to save results to file
            
        Returns:
            Complete validation results
        """
        print(f"\n{'='*80}")
        print(f"Starting validation for {study_id}")
        print(f"{'='*80}\n")
        
        # Determine study path
        if study_path is None:
            study_path = Path("data/studies") / study_id
        else:
            study_path = Path(study_path)
        
        if not study_path.exists():
            raise FileNotFoundError(f"Study path not found: {study_path}")
        
        # Load documents
        print("Loading documents...")
        loader = DocumentLoader()
        documents = loader.load_study_files(study_path)
        
        # Load config code if available
        if config_path is None:
            config_path = Path(f"src/studies/{study_id}_config.py")
        
        if config_path.exists():
            print(f"Loading config code from {config_path}...")
            documents["config_code"] = loader.load_python_file(config_path)
        else:
            print(f"Warning: Config file not found at {config_path}")
            documents["config_code"] = ""
        
        # Run validation agents
        results = {
            "study_id": study_id,
            "validation_timestamp": datetime.now().isoformat(),
            "study_path": str(study_path),
        }
        
        # 1. Experiment Completeness
        print("\n[1/4] Running Experiment Completeness Agent...")
        try:
            completeness_result = self.completeness_agent.validate(documents)
            results["completeness"] = completeness_result
            print("✓ Completeness validation completed")
        except Exception as e:
            print(f"✗ Error in completeness validation: {e}")
            results["completeness"] = {"error": str(e)}
        
        # 2. Experiment Consistency
        print("\n[2/4] Running Experiment Consistency Agent...")
        try:
            consistency_result = self.consistency_agent.validate(documents)
            results["consistency"] = consistency_result
            print("✓ Consistency validation completed")
        except Exception as e:
            print(f"✗ Error in consistency validation: {e}")
            results["consistency"] = {"error": str(e)}
        
        # 3. Data Validation
        print("\n[3/4] Running Data Validation Agent...")
        try:
            data_result = self.data_agent.validate(documents)
            results["data_validation"] = data_result
            print("✓ Data validation completed")
        except Exception as e:
            print(f"✗ Error in data validation: {e}")
            results["data_validation"] = {"error": str(e)}
        
        # 4. Generate Checklist
        print("\n[4/4] Generating Validation Checklist...")
        try:
            checklist_result = self.checklist_agent.validate(
                documents,
                previous_results={
                    "completeness": results.get("completeness", {}),
                    "consistency": results.get("consistency", {}),
                    "data_validation": results.get("data_validation", {}),
                }
            )
            results["checklist"] = checklist_result
            print("✓ Checklist generation completed")
        except Exception as e:
            print(f"✗ Error in checklist generation: {e}")
            results["checklist"] = {"error": str(e)}
        
        # Save results
        if save_results:
            output_file = self.output_dir / f"{study_id}_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"\n✓ Results saved to: {output_file}")
            
            # Also save a human-readable summary
            summary_file = self.output_dir / f"{study_id}_validation_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            self._save_summary(results, summary_file)
            print(f"✓ Summary saved to: {summary_file}")
        
        print(f"\n{'='*80}")
        print(f"Validation completed for {study_id}")
        print(f"{'='*80}\n")
        
        return results
    
    def _save_summary(self, results: Dict[str, Any], output_file: Path):
        """Save human-readable summary"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# Validation Summary for {results['study_id']}\n\n")
            f.write(f"**Validation Date:** {results['validation_timestamp']}\n\n")
            f.write(f"**Study Path:** {results['study_path']}\n\n")
            
            # Completeness summary
            if "completeness" in results and "results" in results["completeness"]:
                comp = results["completeness"]["results"]
                if "completeness_summary" in comp:
                    f.write("## Experiment Completeness\n\n")
                    f.write(f"- **Completeness Score:** {comp['completeness_summary'].get('completeness_score', 'N/A')}\n")
                    f.write(f"- **Total Experiments:** {comp['completeness_summary'].get('total_experiments', 'N/A')}\n")
                    f.write(f"- **Included Experiments:** {comp['completeness_summary'].get('included_experiments', 'N/A')}\n")
                    f.write(f"\n{comp['completeness_summary'].get('completeness_notes', '')}\n\n")
            
            # Consistency summary
            if "consistency" in results and "results" in results["consistency"]:
                cons = results["consistency"]["results"]
                if "consistency_summary" in cons:
                    f.write("## Experimental Setup Consistency\n\n")
                    f.write(f"- **Consistency Score:** {cons['consistency_summary'].get('consistency_score', 'N/A')}\n")
                    f.write(f"- **Consistent Aspects:** {cons['consistency_summary'].get('consistent_aspects', 'N/A')}\n")
                    f.write(f"- **Total Aspects Checked:** {cons['consistency_summary'].get('total_aspects_checked', 'N/A')}\n")
                    f.write(f"\n{cons['consistency_summary'].get('overall_assessment', '')}\n\n")
            
            # Data validation summary
            if "data_validation" in results and "results" in results["data_validation"]:
                data = results["data_validation"]["results"]
                if "validation_summary" in data:
                    f.write("## Human Data Validation\n\n")
                    f.write(f"- **Data Accuracy Score:** {data['validation_summary'].get('data_accuracy_score', 'N/A')}\n")
                    f.write(f"- **Matching Data Points:** {data['validation_summary'].get('matching_data_points', 'N/A')}\n")
                    f.write(f"- **Total Data Points Checked:** {data['validation_summary'].get('total_data_points_checked', 'N/A')}\n")
                    f.write(f"\n{data['validation_summary'].get('overall_assessment', '')}\n\n")
            
            # Checklist summary
            if "checklist" in results and "results" in results["checklist"]:
                checklist = results["checklist"]["results"]
                if "checklist_summary" in checklist:
                    f.write("## Validation Checklist\n\n")
                    f.write(f"- **Total Items:** {checklist['checklist_summary'].get('total_items', 'N/A')}\n")
                    f.write(f"- **Critical Items:** {checklist['checklist_summary'].get('critical_items', 'N/A')}\n")
                    f.write(f"- **Estimated Validation Time:** {checklist['checklist_summary'].get('estimated_validation_time', 'N/A')}\n\n")

