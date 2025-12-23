"""
JSON Generator - Generates compatible JSON files (metadata.json, specification.json, ground_truth.json)
and materials files
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from validation_pipeline.utils.gemini_client import GeminiClient


class JSONGenerator:
    """Generate JSON files compatible with existing study format"""
    
    def __init__(
        self,
        model: str = "models/gemini-3-flash-preview",
        api_key: Optional[str] = None
    ):
        """
        Initialize JSON generator.
        
        Args:
            model: Gemini model to use for LLM-based materials generation
            api_key: Optional API key
        """
        self.client = GeminiClient(model=model, api_key=api_key)
    
    def generate_metadata(
        self,
        extraction_result: Dict[str, Any],
        study_id: str,
        pdf_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        Generate metadata.json using LLM to infer domain/subdomain and structure.
        
        Args:
            extraction_result: Results from stage2 extraction
            study_id: Study ID (e.g., "study_005")
            pdf_path: Optional path to PDF file for context
            
        Returns:
            Dictionary matching metadata.json format
        """
        studies = extraction_result.get('studies', [])
        if not studies:
            raise ValueError("No studies found")
        
        # Collect all scenarios from all sub-studies
        scenarios = []
        for study in studies:
            sub_studies = study.get('sub_studies', [])
            for sub_study in sub_studies:
                sub_id = sub_study.get('sub_study_id', '')
                if sub_id:
                    scenarios.append(sub_id)
        
        # Use LLM to infer domain/subdomain and keywords
        extraction_summary = json.dumps(extraction_result, indent=2, ensure_ascii=False)
        
        prompt = f"""You are a metadata generator. Based on the extraction results, generate the domain, subdomain, and keywords for this study.

EXTRACTION RESULTS:
{extraction_summary[:10000]}...

TASK:
Generate a JSON object with:
- domain: The psychological domain (e.g., "social_psychology", "cognitive_psychology", "developmental_psychology")
- subdomain: The specific subdomain (e.g., "social_cognition", "judgment_and_decision_making", "memory")
- keywords: List of relevant keywords (3-5 keywords)

OUTPUT FORMAT (JSON only):
{{
    "domain": "domain_name",
    "subdomain": "subdomain_name",
    "keywords": ["keyword1", "keyword2", "keyword3"]
}}

Generate the JSON:
"""
        
        try:
            if pdf_path and pdf_path.exists():
                uploaded_file = self.client.upload_file(pdf_path)
                response = self.client.generate_content(
                    prompt=[uploaded_file, prompt],
                    temperature=0.3
                )
            else:
                response = self.client.generate_content(prompt=prompt, temperature=0.3)
            
            if response:
                # Parse LLM response
                llm_metadata = self._parse_json_response(response)
                domain = llm_metadata.get('domain')
                subdomain = llm_metadata.get('subdomain')
                keywords = llm_metadata.get('keywords', [])
            else:
                domain = None
                subdomain = None
                keywords = []
        except Exception as e:
            print(f"Warning: Error generating metadata with LLM: {e}")
            domain = None
            subdomain = None
            keywords = []
        
        # Extract keywords from phenomenon if LLM didn't provide
        if not keywords:
            study = studies[0]
            phenomenon = study.get('phenomenon', '')
            if phenomenon:
                keywords = [phenomenon.replace(' ', '_')]
        
        return {
            "id": study_id,
            "title": extraction_result.get('paper_title', ''),
            "authors": extraction_result.get('paper_authors', []),
            "year": extraction_result.get('paper_year'),
            "domain": domain,
            "subdomain": subdomain,
            "keywords": keywords,
            "difficulty": "medium",  # TODO: Determine from study complexity
            "description": extraction_result.get('paper_abstract', '')[:200] + "...",
            "scenarios": scenarios
        }
    
    def _parse_json_response(self, response: str) -> Dict[str, Any]:
        """Parse JSON from LLM response"""
        response_text = response.strip()
        
        # Remove markdown code blocks if present
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON object
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {}
    
    @staticmethod
    def generate_specification(extraction_result: Dict[str, Any], study_id: str) -> Dict[str, Any]:
        """
        Generate specification.json compatible with study001-004 format.
        
        Args:
            extraction_result: Results from stage2 extraction
            study_id: Study ID
            
        Returns:
            Dictionary matching specification.json format
        """
        studies = extraction_result.get('studies', [])
        if not studies:
            raise ValueError("No studies found")
        
        # Aggregate participants across all studies and sub-studies
        total_n = 0
        all_demographics = {}
        population = None
        recruitment_source = None
        
        # Collect participant info from each sub-study
        sub_study_participants = {}
        
        # Collect design factors from sub-studies
        factors = []
        factor_names = set()
        
        for study in studies:
            # First try overall_participants
            overall_participants = study.get('overall_participants', {})
            if overall_participants:
                total_n += overall_participants.get('total_n', 0)
                if not population:
                    population = overall_participants.get('population', '')
                if not recruitment_source:
                    recruitment_source = overall_participants.get('recruitment_source', '')
                demos = overall_participants.get('demographics', {})
                if demos and isinstance(demos, dict):
                    all_demographics.update(demos)
            
            # Extract from sub-studies (more accurate)
            sub_studies = study.get('sub_studies', [])
            for sub_study in sub_studies:
                sub_id = sub_study.get('sub_study_id', '')
                sub_participants = sub_study.get('participants', {})
                
                if sub_participants:
                    sub_n = sub_participants.get('n', 0)
                    # Handle string 'n' (e.g. "20", "approx 20")
                    if isinstance(sub_n, str):
                        import re
                        # Extract first number found
                        match = re.search(r'\d+', sub_n)
                        if match:
                            sub_n = int(match.group())
                        else:
                            sub_n = 0
                            
                    if sub_n:
                        total_n += sub_n
                        sub_study_participants[sub_id] = {
                            "n": sub_n,
                            "population": sub_participants.get('population', ''),
                            "recruitment_source": sub_participants.get('recruitment_source', '')
                        }
                    
                    if not population:
                        population = sub_participants.get('population', '')
                    if not recruitment_source:
                        recruitment_source = sub_participants.get('recruitment_source', '')
                    
                    # Parse demographics (could be string or dict)
                    sub_demos = sub_participants.get('demographics', {})
                    if isinstance(sub_demos, str):
                        # Try to extract structured info from string
                        if 'age' in sub_demos.lower() or 'gender' in sub_demos.lower():
                            # Keep as note for now
                            pass
                    elif isinstance(sub_demos, dict) and sub_demos:
                        all_demographics.update(sub_demos)
            
            # Extract design factors
            if sub_studies:
                # Create a factor for scenarios/conditions
                scenario_levels = [ss.get('sub_study_id', '') for ss in sub_studies if ss.get('sub_study_id')]
                if scenario_levels and 'scenario' not in factor_names:
                    factors.append({
                        "name": "Scenario",
                        "levels": scenario_levels,
                        "type": "Between-Subjects"
                    })
                    factor_names.add('scenario')
        
        # If no demographics extracted, try to infer from paper or use defaults
        if not all_demographics:
            # Common defaults for psychology studies
            all_demographics = {}
        
        # Build participants section
        participants_section = {
            "n": total_n,
            "population": population or "Not specified",
            "recruitment_source": recruitment_source or "Not specified",
            "demographics": all_demographics
        }
        
        # Add sub-study participant breakdown if available
        if sub_study_participants:
            participants_section["by_sub_study"] = sub_study_participants
        
        return {
            "study_id": study_id,
            "title": extraction_result.get('paper_title', ''),
            "participants": participants_section,
            "design": {
                "type": "Mixed",  # TODO: Extract from study design
                "factors": factors
            },
            "procedure": {
                "steps": [
                    "Read scenario/questionnaire description",
                    "Make choice or provide response",
                    "Estimate peer consensus/percentage"
                ]
            }
        }
    
    @staticmethod
    def generate_ground_truth(extraction_result: Dict[str, Any], study_id: str) -> Dict[str, Any]:
        """
        Generate ground_truth.json compatible with study001-004 format.
        
        Args:
            extraction_result: Results from stage2 extraction
            study_id: Study ID
            
        Returns:
            Dictionary matching ground_truth.json format
        """
        studies = extraction_result.get('studies', [])
        if not studies:
            raise ValueError("No studies found")
        
        # Generate validation criteria from sub-studies
        required_tests = []
        original_results = {}
        
        test_counter = 1
        for study in studies:
            study_id_key = study.get('study_id', '').lower().replace(' ', '_')
            sub_studies = study.get('sub_studies', [])
            
            # Organize original_results by study
            study_results = {}
            
            for sub_study in sub_studies:
                sub_id = sub_study.get('sub_study_id', '')
                human_data = sub_study.get('human_data', {})
                
                if human_data:
                    study_results[sub_id] = human_data
                
                # Generate validation test for each sub-study with statistical data
                stat_tests = sub_study.get('statistical_tests', [])
                for stat_test in stat_tests:
                    test_type = stat_test.get('test_type', 'unknown')
                    # Normalize test type
                    if 't_test' in test_type.lower() or 't-test' in test_type.lower():
                        normalized_test = "independent_t_test"
                    elif 'anova' in test_type.lower() or 'f-test' in test_type.lower():
                        normalized_test = "anova"
                    elif 'chi' in test_type.lower():
                        normalized_test = "chi_square_test"
                    else:
                        normalized_test = "unknown"
                    
                    test = {
                        "test_id": f"P{test_counter}",
                        "test_name": f"{study_id_key} {sub_id} Significance",
                        "test_type": "phenomenon_level",
                        "difficulty": "medium",
                        "description": f"Tests if the effect in {sub_id} is statistically significant (p < 0.05)",
                        "method": {
                            "test": normalized_test,
                            "source_field": f"{sub_id}_effect",
                            "threshold": 0.05,
                            "expected_direction": "positive"
                        },
                        "critical": True,
                        "weight": 1.5
                    }
                    required_tests.append(test)
                    test_counter += 1
            
            if study_results:
                original_results[study_id_key] = study_results
        
        return {
            "study_id": study_id,
            "title": extraction_result.get('paper_title', ''),
            "authors": extraction_result.get('paper_authors', []),
            "year": extraction_result.get('paper_year'),
            "validation_criteria": {
                "required_tests": required_tests,
                "scoring": {
                    "total_weight": sum(t.get('weight', 1.0) for t in required_tests),
                    "critical_requirement": f"All critical tests must pass",
                    "passing_threshold": 0.6
                }
            },
            "original_results": original_results
        }
    
    def generate_materials(
        self,
        extraction_result: Dict[str, Any],
        study_dir: Path,
        pdf_path: Optional[Path] = None
    ) -> List[Path]:
        """
        Generate materials files using LLM-based dynamic function generation.
        
        This method uses LLM to generate a study-specific generate_materials function
        that knows how to extract complete materials from the extraction_result.
        
        Args:
            extraction_result: Results from stage2 extraction
            study_dir: Study directory path
            pdf_path: Optional path to PDF file for context
            
        Returns:
            List of generated material file paths
        """
        # Use LLM to generate a study-specific materials generation function
        materials_generator_code = self._generate_materials_function_with_llm(
            extraction_result,
            pdf_path
        )
        
        # Execute the generated function
        materials_dir = study_dir / "materials"
        materials_dir.mkdir(parents=True, exist_ok=True)
        
        # Create a namespace for executing the generated code
        namespace = {
            'json': json,
            'Path': Path,
            'materials_dir': materials_dir,
            'extraction_result': extraction_result,
            'study_dir': study_dir
        }
        
        try:
            exec(materials_generator_code, namespace)
            # Call the generated function
            if 'generate_materials' in namespace:
                generated_files = namespace['generate_materials'](extraction_result, materials_dir)
            else:
                generated_files = namespace.get('generated_files', [])
            
            # Ensure all items are Path objects
            generated_files = [Path(f) if not isinstance(f, Path) else f for f in generated_files]
            
            if not generated_files:
                print(f"Warning: Generated function returned no files, falling back to basic generation")
                generated_files = self._generate_materials_basic(extraction_result, study_dir)
        except Exception as e:
            print(f"Warning: Error executing generated materials function: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to basic generation
            generated_files = self._generate_materials_basic(extraction_result, study_dir)
        
        return generated_files
    
    def _generate_materials_function_with_llm(
        self,
        extraction_result: Dict[str, Any],
        pdf_path: Optional[Path]
    ) -> str:
        """
        Use LLM to generate a study-specific generate_materials function.
        
        Args:
            extraction_result: Results from stage2 extraction
            pdf_path: Optional path to PDF file
            
        Returns:
            Python code string for the generated function
        """
        extraction_summary = json.dumps(extraction_result, indent=2, ensure_ascii=False)
        
        # Build prompt
        prompt = f"""You are a Python code generator. Generate a complete `generate_materials` function that extracts materials for a SIMULATION AGENT.

EXTRACTION RESULTS:
{extraction_summary[:50000]}...

TASK:
Generate a Python function that creates the necessary files for a simulator to run this study.
1. Analyze the structure of the study (is it a survey? a scenario choice? an estimation task?).
2. Generate `items.json` files for structured data (lists of questions, stimuli, etc.).
3. Generate `instructions.txt` files for the prompt/instructions given to the agent.
4. Return a list of generated file paths.

REQUIREMENTS:
- IF the study involves iterating over items (e.g. 15 estimation questions), generate a SINGLE `[sub_study]_items.json` file containing the list.
  - DO NOT generate 15 separate text files unless the format explicitly requires it. JSON is better for simulators.
- IF the study is a simple scenario (read and react), generate `[sub_study]_scenario.txt`.
- ALWAYS include the specific questions/text in the files.
- Organize files into `materials_dir`.
- Ensure file names are consistent with the `sub_study_id`s in the extraction result.

EXAMPLE STRUCTURE:
```python
def generate_materials(extraction_result, materials_dir):
    from pathlib import Path
    import json
    
    generated_files = []
    studies = extraction_result.get('studies', [])
    
    for study in studies:
        for sub in study.get('sub_studies', []):
            sub_id = sub.get('sub_study_id', 'unknown')
            
            # 1. Generate Instructions/Procedure
            content = sub.get('content', '')
            if content:
                path = materials_dir / f"{{sub_id}}_instructions.txt"
                path.write_text(content, encoding='utf-8')
                generated_files.append(path)
            
            # 2. Generate Items (if any)
            items = sub.get('items', [])
            if items:
                path = materials_dir / f"{{sub_id}}_items.json"
                path.write_text(json.dumps(items, indent=2), encoding='utf-8')
                generated_files.append(path)
                
    return generated_files
```

OUTPUT:
Provide ONLY the complete Python function code. The function should be production-ready.
"""
        
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
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract Python code from LLM response"""
        response_text = response.strip()
        
        # Remove markdown code blocks if present
        if '```python' in response_text:
            response_text = response_text.split('```python')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        return response_text
    
    def _generate_materials_basic(
        self,
        extraction_result: Dict[str, Any],
        study_dir: Path
    ) -> List[Path]:
        """
        Basic fallback materials generation (original implementation).
        
        Args:
            extraction_result: Results from stage2 extraction
            study_dir: Study directory path
            
        Returns:
            List of generated material file paths
        """
        materials_dir = study_dir / "materials"
        materials_dir.mkdir(parents=True, exist_ok=True)
        
        generated_files = []
        studies = extraction_result.get('studies', [])
        
        for study in studies:
            sub_studies = study.get('sub_studies', [])
            
            for sub_study in sub_studies:
                sub_id = sub_study.get('sub_study_id', '')
                content = sub_study.get('content', '')
                sub_type = sub_study.get('type', 'scenario')
                
                if not sub_id or not content:
                    continue
                
                # Generate file based on type
                if sub_type == 'questionnaire':
                    # Generate JSON file for questionnaire items
                    items = sub_study.get('items', [])
                    if items:
                        items_data = {
                            "description": f"Items from {sub_id}",
                            "items": items
                        }
                        file_path = materials_dir / f"{sub_id}.json"
                        file_path.write_text(
                            json.dumps(items_data, indent=2, ensure_ascii=False),
                            encoding='utf-8'
                        )
                        generated_files.append(file_path)
                else:
                    # Generate text file for scenarios
                    file_path = materials_dir / f"{sub_id}.txt"
                    file_path.write_text(content, encoding='utf-8')
                    generated_files.append(file_path)
        
        return generated_files
