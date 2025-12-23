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
        
        # Load example config for reference
        example_config = self._load_example_config()
        
        # Generate Python code using LLM
        code = self._generate_code_with_llm(
            extraction_result,
            study_id,
            pdf_path,
            example_config,
            study_dir
        )
        
        # Write to file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(code, encoding='utf-8')
        
        return output_path
    
    def _load_example_config(self) -> str:
        """Load example config for reference"""
        example_path = Path("src/studies/study_001_config.py")
        if example_path.exists():
            return example_path.read_text(encoding='utf-8')
        return ""
    
    def _generate_code_with_llm(
        self,
        extraction_result: Dict[str, Any],
        study_id: str,
        pdf_path: Optional[Path],
        example_config: str,
        study_dir: Optional[Path]
    ) -> str:
        """Generate Python code using LLM"""
        # Prepare extraction data summary
        extraction_summary = json.dumps(extraction_result, indent=2, ensure_ascii=False)
        
        # Build prompt
        prompt = self._build_prompt(
            extraction_summary,
            study_id,
            example_config,
            study_dir
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
        study_dir: Optional[Path]
    ) -> str:
        """Build prompt for LLM"""
        materials_info = ""
        if study_dir:
            materials_dir = study_dir / "materials"
            if materials_dir.exists():
                materials = list(materials_dir.glob("*"))
                materials_info = f"""
MATERIALS AVAILABLE:
{chr(10).join(f"  - {m.name}" for m in materials)}
"""
        
        return f"""You are a Python code generator. Generate a complete StudyConfig class based on the extraction results.

STUDY ID: {study_id}

EXTRACTION RESULTS (from paper):
{extraction_summary}
{materials_info}
EXAMPLE CONFIG (study_001_config.py - for reference):
```python
{example_config[:3000]}...
```

TASK:
Generate a complete Python file for {study_id}_config.py that:

1. **Implements BaseStudyConfig** with all required methods:
   - `create_trials()`: Generate trial data based on study design
   - `aggregate_results()`: Aggregate and calculate statistics from raw results
   - `get_prompt_builder()`: Return a PromptBuilder subclass (if needed)
   - `custom_scoring()`: Optional custom scoring logic

2. **Based on extraction results**:
   - Use the sub-studies/scenarios from extraction
   - Implement trial generation matching the study design
   - Implement result aggregation matching the statistical methods
   - Extract data correctly from participant responses

3. **Follow the example structure**:
   - Similar to study_001_config.py
   - Include PromptBuilder subclass if needed
   - Include helper methods for parsing responses
   - Include statistical calculations

4. **Key requirements**:
   - Must be complete, runnable Python code
   - Must correctly extract data from responses
   - Must calculate statistics matching the paper's methods
   - Must handle all sub-studies/scenarios from extraction

OUTPUT:
Provide ONLY the complete Python code, starting with the docstring and imports.
Do not include markdown code blocks or explanations outside the code.
The code should be production-ready and complete.

Generate the complete {study_id}_config.py file:
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
