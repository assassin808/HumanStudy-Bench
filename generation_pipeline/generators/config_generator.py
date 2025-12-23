"""
Config Generator - Generates StudyConfig classes from extraction results using LLM
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from validation_pipeline.utils.gemini_client import GeminiClient


class ConfigGenerator:
    """Generate StudyConfig classes from extraction results using LLM"""
    
    def __init__(
        self,
        model: str = "models/gemini-3-flash-preview",
        api_key: Optional[str] = None
    ):
        """
        Initialize config generator.
        
        Args:
            model: Gemini model to use
            api_key: Optional API key
        """
        self.client = GeminiClient(model=model, api_key=api_key)
    
    def generate(
        self,
        extraction_result: Dict[str, Any],
        study_id: str,
        output_path: Path,
        pdf_path: Optional[Path] = None,
        study_dir: Optional[Path] = None
    ) -> Path:
        """
        Generate StudyConfig class file using LLM.
        
        Args:
            extraction_result: Results from stage2 extraction
            study_id: Study ID (e.g., "study_005")
            output_path: Path to save the config file
            pdf_path: Optional path to PDF file
            study_dir: Optional study directory (for finding PDF and materials)
            
        Returns:
            Path to generated config file
        """
        studies = extraction_result.get('studies', [])
        if not studies:
            raise ValueError("No studies found in extraction result")
        
        # Auto-find PDF if not provided
        if pdf_path is None and study_dir:
            pdf_files = list(study_dir.glob("*.pdf"))
            if pdf_files:
                pdf_path = pdf_files[0]
        
        # Load all study data for context
        study_context = {}
        if study_dir:
            for json_file in ["metadata.json", "specification.json", "ground_truth.json"]:
                p = study_dir / json_file
                if p.exists():
                    try:
                        study_context[json_file] = json.loads(p.read_text(encoding='utf-8'))
                    except:
                        pass
        
        # Load example config for reference
        example_config = self._load_example_config()
        
        # Generate Python code using LLM
        code = self._generate_code_with_llm(
            extraction_result,
            study_id,
            pdf_path,
            example_config,
            study_dir,
            study_context
        )
        
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(code, encoding='utf-8')
        
        return output_path

    def _generate_code_with_llm(
        self,
        extraction_result: Dict[str, Any],
        study_id: str,
        pdf_path: Optional[Path],
        example_config: str,
        study_dir: Optional[Path],
        study_context: Dict[str, Any] = None
    ) -> str:
        """Generate Python code using LLM"""
        # Prepare extraction data summary
        extraction_summary = json.dumps(extraction_result, indent=2, ensure_ascii=False)
        context_summary = json.dumps(study_context or {}, indent=2, ensure_ascii=False)
        
        # Build prompt
        prompt = self._build_prompt(
            extraction_summary,
            study_id,
            example_config,
            study_dir,
            context_summary
        )
        
        # Call LLM (with PDF if available)
        try:
            if pdf_path and pdf_path.exists():
                uploaded_file = self.client.upload_file(pdf_path)
                response = self.client.generate_content(
                    prompt=[uploaded_file, prompt]
                )
            else:
                response = self.client.generate_content(prompt=prompt)
        except Exception as e:
            raise RuntimeError(f"Error calling LLM API: {e}. Please check your GOOGLE_API_KEY environment variable.")
        
        if response is None:
            raise ValueError("LLM returned None response. Check API key and network connection.")
        
        # Extract code from response
        code = self._extract_code_from_response(response)
        
        return code

    def _build_prompt(
        self,
        extraction_summary: str,
        study_id: str,
        example_config: str,
        study_dir: Optional[Path],
        context_summary: str = ""
    ) -> str:
        """Build prompt for LLM"""
        materials_info = ""
        if study_dir:
            materials_dir = study_dir / "materials"
            if materials_dir.exists():
                materials = list(materials_dir.glob("*"))
                materials_info = f"""
MATERIALS AVAILABLE IN {materials_dir}:
{chr(10).join(f"  - {m.name}" for m in materials)}
"""
        
        return f"""You are a Python code generator for HumanStudyBench. Your task is to generate a complete `{study_id}_config.py` file that encapsulates all logic for running and evaluating a psychological study.

STUDY ID: {study_id}

STUDY CONTEXT (metadata, specification, ground_truth):
{context_summary}

EXTRACTION RESULTS (detailed extraction from paper):
{extraction_summary}

{materials_info}

EXAMPLE CONFIG (for reference structure):
```python
{example_config[:3000]}...
```

TASK:
Generate a complete, production-ready Python file `{study_id}_config.py`.

CORE REQUIREMENTS:
1. **Inherit from `BaseStudyConfig`**:
   - Import it from `src.core.study_config` (or use relative import if preferred).
   - Implement `create_trials(self, n_trials=None)`.
   - Implement `aggregate_results(self, raw_results)`.
   - Implement `custom_scoring(self, results, ground_truth)`.

2. **Unified Interaction Interface**:
   - The config must act as the primary interface between the simulator and the study data.
   - It should know exactly which Research Questions (RQs) and sub-studies are being tested.

3. **Sub-studies & Statistical Tests**:
   - Identify the specific Research Questions (RQs) or sub-studies from the extraction results.
   - Each sub-study should have corresponding statistical tests (e.g., t-test, ANOVA) that match what was reported in the paper.
   - Use `scipy.stats` or the provided `MetricsCalculator` for calculations.

4. **Trials & Items**:
   - `create_trials` must generate specific trials based on the items found in the `materials/` directory (e.g., from `_items.json` or `_instructions.txt`).
   - Each trial should include all necessary fields for the LLM participant to respond (e.g., question text, anchors, options).

5. **Prompt Building**:
   - If the study requires custom prompt logic (e.g., specific system messages for different conditions), implement a `PromptBuilder` subclass inside this file.
   - Override `get_prompt_builder(self)` in your config class to return this custom builder.

6. **Results Aggregation & Evaluation**:
   - `aggregate_results` must parse the raw LLM responses, extract numerical or categorical data, and perform the EXACT statistical tests mentioned in the ground truth.
   - `custom_scoring` should compare the calculated statistics against the `ground_truth` and return a dictionary of scores (0.0 to 1.0) for each test.

7. **Conciseness & Encapsulation**:
   - Follow the "Occam's Razor" principle: keep it simple but complete.
   - All study-specific logic must be contained within this file.

OUTPUT FORMAT:
Provide ONLY the complete Python code. No markdown code blocks, no explanations. The file must start with imports and end with the class definition and registration.

Generate the complete `{study_id}_config.py` now:
"""
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract Python code from LLM response"""
        response_text = response.strip()
        
        # Remove markdown code blocks if present
        if '```python' in response_text:
            response_text = response_text.split('```python')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        # Remove any leading/trailing text that's not code
        lines = response_text.split('\n')
        
        # Find first line that looks like Python (import, class, def, or docstring)
        start_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (stripped.startswith('"""') or 
                stripped.startswith("'''") or
                stripped.startswith('import ') or
                stripped.startswith('from ') or
                stripped.startswith('class ') or
                stripped.startswith('def ') or
                stripped.startswith('@')):
                start_idx = i
                break
        
        # Find last line that's part of the code
        end_idx = len(lines)
        for i in range(len(lines) - 1, -1, -1):
            stripped = lines[i].strip()
            if stripped and not stripped.startswith('#'):
                end_idx = i + 1
                break
        
        code = '\n'.join(lines[start_idx:end_idx])
        
        return code
