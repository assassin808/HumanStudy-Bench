"""
Generation Pipeline Orchestrator

Coordinates filters, extractors, and generators to create study configurations.
"""

import json
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

from generation_pipeline.filters.replicability_filter import ReplicabilityFilter
from generation_pipeline.extractors.study_data_extractor import StudyDataExtractor
from generation_pipeline.generators.config_generator import ConfigGenerator
from generation_pipeline.generators.json_generator import JSONGenerator
from generation_pipeline.utils.gemini_client import GeminiClient
from generation_pipeline.utils.review_parser import ReviewParser
from generation_pipeline.utils.output_formatter import OutputFormatter


class GenerationPipeline:
    """Main pipeline orchestrator"""
    
    def __init__(
        self,
        model: str = "models/gemini-3-flash-preview",
        api_key: Optional[str] = None,
        output_dir: Optional[Path] = None
    ):
        """
        Initialize pipeline.
        
        Args:
            model: Gemini model to use
            api_key: Optional API key
            output_dir: Directory for output files
        """
        self.client = GeminiClient(model=model, api_key=api_key)
        self.output_dir = Path(output_dir) if output_dir else Path("generation_pipeline/outputs")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.filter = ReplicabilityFilter(self.client)
        self.extractor = StudyDataExtractor(self.client)
        self.config_generator = ConfigGenerator()
        self.json_generator = JSONGenerator()
    
    def run_stage1(self, pdf_path: Path) -> Tuple[Path, Path, Dict[str, Any]]:
        """
        Run stage 1 (filter).
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (markdown_path, json_path, result_dict)
        """
        print(f"Running Stage 1: Replicability Filter for {pdf_path.name}")
        
        # Run filter
        result = self.filter.process(pdf_path)
        
        # Generate paper_id from filename
        paper_id = pdf_path.stem.replace(' ', '_').replace('-', '_').lower()
        result['paper_id'] = paper_id
        
        # Format as markdown
        md_content = OutputFormatter.format_stage1_review(result)
        
        # Save files
        md_path = self.output_dir / f"{paper_id}_stage1_filter.md"
        json_path = self.output_dir / f"{paper_id}_stage1_filter.json"
        
        md_path.write_text(md_content, encoding='utf-8')
        json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        
        print(f"Stage 1 complete. Review file: {md_path}")
        print(f"JSON file: {json_path}")
        
        return md_path, json_path, result
    
    def check_stage1_review(self, review_file: Path) -> Dict[str, Any]:
        """
        Check stage1 review status.
        
        Args:
            review_file: Path to review markdown file
            
        Returns:
            Dictionary with review status and action
        """
        parsed = ReviewParser.parse(review_file)
        action = ReviewParser.get_action(parsed['review_status'])
        
        return {
            "action": action,
            "review_status": parsed['review_status'],
            "comments": parsed['comments'],
            "checklists": parsed['checklists']
        }
    
    def run_stage2(self, stage1_json_path: Path, pdf_path: Path) -> Tuple[Path, Path, Dict[str, Any]]:
        """
        Run stage 2 (extraction).
        
        Args:
            stage1_json_path: Path to stage1 JSON result
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (markdown_path, json_path, result_dict)
        """
        print(f"Running Stage 2: Study & Data Extraction")
        
        # Load stage1 results
        stage1_result = json.loads(stage1_json_path.read_text(encoding='utf-8'))
        
        # Run extractor
        result = self.extractor.process(stage1_result, pdf_path)
        
        # Format as markdown
        md_content = OutputFormatter.format_stage2_review(result)
        
        # Save files
        paper_id = stage1_result.get('paper_id', 'unknown')
        md_path = self.output_dir / f"{paper_id}_stage2_extraction.md"
        json_path = self.output_dir / f"{paper_id}_stage2_extraction.json"
        
        md_path.write_text(md_content, encoding='utf-8')
        json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
        
        print(f"Stage 2 complete. Review file: {md_path}")
        print(f"JSON file: {json_path}")
        
        return md_path, json_path, result
    
    def check_stage2_review(self, review_file: Path) -> Dict[str, Any]:
        """Check stage2 review status"""
        parsed = ReviewParser.parse(review_file)
        action = ReviewParser.get_action(parsed['review_status'])
        
        return {
            "action": action,
            "review_status": parsed['review_status'],
            "comments": parsed['comments'],
            "checklists": parsed['checklists']
        }
    
    def generate_study(
        self,
        stage2_json_path: Path,
        study_id: str,
        study_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Generate study files (JSON + Config class).
        
        Args:
            stage2_json_path: Path to stage2 JSON result
            study_id: Study ID (e.g., "study_005")
            study_dir: Directory to save study files (default: data/studies/{study_id})
            
        Returns:
            Dictionary with paths to generated files
        """
        print(f"Generating study: {study_id}")
        
        # Load stage2 results
        extraction_result = json.loads(stage2_json_path.read_text(encoding='utf-8'))
        
        # Determine study directory
        if study_dir is None:
            study_dir = Path("data/studies") / study_id
        study_dir = Path(study_dir)
        study_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate JSON files
        metadata = self.json_generator.generate_metadata(extraction_result, study_id)
        specification = self.json_generator.generate_specification(extraction_result, study_id)
        ground_truth = self.json_generator.generate_ground_truth(extraction_result, study_id)
        
        # Save JSON files
        (study_dir / "metadata.json").write_text(
            json.dumps(metadata, indent=2, ensure_ascii=False), encoding='utf-8'
        )
        (study_dir / "specification.json").write_text(
            json.dumps(specification, indent=2, ensure_ascii=False), encoding='utf-8'
        )
        (study_dir / "ground_truth.json").write_text(
            json.dumps(ground_truth, indent=2, ensure_ascii=False), encoding='utf-8'
        )
        
        # Generate Config class
        config_path = Path("src/studies") / f"{study_id}_config.py"
        self.config_generator.generate(extraction_result, study_id, config_path)
        
        print(f"Study generated:")
        print(f"  - {study_dir / 'metadata.json'}")
        print(f"  - {study_dir / 'specification.json'}")
        print(f"  - {study_dir / 'ground_truth.json'}")
        print(f"  - {config_path}")
        print("\nNOTE: Config class needs manual refinement. Update get_study_config() factory function.")
        
        return {
            "study_dir": study_dir,
            "metadata": study_dir / "metadata.json",
            "specification": study_dir / "specification.json",
            "ground_truth": study_dir / "ground_truth.json",
            "config": config_path
        }

