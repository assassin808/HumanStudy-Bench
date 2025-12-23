"""
Study & Data Extractor - Stage 2

Extracts study information, phenomena, research questions, statistical data,
and participant profiles from papers.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from generation_pipeline.extractors.base_extractor import BaseExtractor
from generation_pipeline.utils.document_loader import DocumentLoader


class StudyDataExtractor(BaseExtractor):
    """Extract study and statistical data from papers"""
    
    def process(self, stage1_json: Dict[str, Any], pdf_path: Path) -> Dict[str, Any]:
        """
        Extract study data from PDF.
        
        Args:
            stage1_json: Results from stage1 filter
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted data:
            {
                "paper_id": str,
                "studies": [
                    {
                        "study_id": "Study 1",
                        "study_name": "...",
                        "phenomenon": "...",
                        "research_questions": [...],
                        "participants": {...}
                    }
                ]
            }
        """
        # Load PDF
        loader = DocumentLoader()
        pdf_info = loader.get_pdf_pages(pdf_path)
        
        # Upload PDF to Gemini
        uploaded_file = self.client.upload_file(pdf_path)
        
        # Generate prompt
        prompt = self._build_prompt(stage1_json, pdf_path.name, len(pdf_info))
        
        # Call LLM (file first, then text prompt)
        try:
            response = self.client.generate_content(
                prompt=[uploaded_file, prompt]
            )
        except Exception as e:
            raise RuntimeError(f"Error calling LLM API: {e}. Please check your GOOGLE_API_KEY environment variable.")
        
        if response is None:
            raise ValueError("LLM returned None response. Check API key and network connection.")
        
        # Parse response
        result = self._parse_response(response, stage1_json)
        
        if result is None:
            raise ValueError("Parsed result is None")
        
        return result
    
    def _build_prompt(self, stage1_json: Dict[str, Any], pdf_name: str, num_pages: int) -> str:
        """Build prompt for LLM"""
        experiments_info = json.dumps(stage1_json.get("experiments", []), indent=2)
        
        return f"""Analyze the research paper in the attached PDF file: {pdf_name} ({num_pages} pages)

STAGE 1 FILTER RESULTS:
{experiments_info}

Your task is to extract COMPLETE information for each REPLICABLE experiment/study identified in Stage 1.
The goal is to enable a simulation agent to REPLICATE the study.

For EACH replicable study/experiment, extract:

1. STUDY STRUCTURE:
   - Study ID (e.g., "Study 1", "Experiment 2")
   - Study name/description
   - Core psychological phenomenon
   - List ALL sub-studies/scenarios/conditions within this study.
   - NOTE: A "sub-study" or "condition" is the level at which data is collected (e.g., "High Anchor Group", "Low Anchor Group", or "Estimation Task").

2. MATERIALS/QUESTIONS (CRITICAL):
   For each sub-study/scenario/task:
   - Sub-study ID (e.g., "experiment_1_estimation_tasks")
   - Type: "scenario" (story), "questionnaire" (items), or "task" (procedure)
   - Content: The FULL TEXT of the instructions given to participants.
   - Items: If it's a questionnaire or estimation task, LIST ALL SPECIFIC QUESTIONS/ITEMS.
     - Example: If there are 15 estimation questions, list ALL 15 with their specific content (e.g., "Length of Mississippi River").
     - If there are experimental conditions (e.g., Low Anchor vs High Anchor), list the specific parameters for EACH item.

3. PARTICIPANT INFORMATION:
   - N for each sub-study/condition
   - Population description
   - Recruitment source
   - Demographics (age, gender, etc.)

4. HUMAN DATA (GROUND TRUTH):
   For each sub-study/scenario/item:
   - Report the actual results found in the paper.
   - If available, report ITEM-LEVEL results (e.g., the mean estimate for "Mississippi River" in Low vs High anchor).
   - Report statistical test results (t-test, F-test, etc.) with values (t, p, df).

IMPORTANT:
- Extract ALL sub-studies/scenarios mentioned in the paper.
- Extract the ACTUAL TEXT of questions/items (not just "Participants answered 15 questions").
- Extract ITEM-LEVEL data if available (this is crucial for ground truth).
- Organize data by sub-study.

Provide your analysis in JSON format:
{{
    "studies": [
        {{
            "study_id": "Experiment 1",
            "study_name": "Anchoring Estimation",
            "phenomenon": "Anchoring Effect",
            "sub_studies": [
                {{
                    "sub_study_id": "experiment_1_estimation_tasks",
                    "type": "task",
                    "content": "Participants were asked...",
                    "items": [
                        {{
                            "id": "1",
                            "question": "Length of Mississippi River",
                            "low_anchor": 70,
                            "high_anchor": 2000
                        }}
                    ],
                    "participants": {{ "n": 100, ... }},
                    "human_data": {{
                        "item_level_results": [
                            {{
                                "question": "Length of Mississippi River",
                                "low_anchor_mean": 500,
                                "high_anchor_mean": 1500
                            }}
                        ]
                    }}
                }}
            ]
        }}
    ]
}}"""
    
    def _parse_response(self, response: str, stage1_json: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response"""
        if response is None:
            raise ValueError("LLM response is None")
        
        # Extract JSON from response
        response_text = response.strip() if isinstance(response, str) else str(response).strip()
        
        # Remove markdown code blocks if present
        if '```json' in response_text:
            response_text = response_text.split('```json')[1].split('```')[0].strip()
        elif '```' in response_text:
            response_text = response_text.split('```')[1].split('```')[0].strip()
        
        try:
            result = json.loads(response_text)
        except json.JSONDecodeError:
            # Try to extract JSON object
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                raise ValueError(f"Could not parse JSON from response: {response_text[:200]}")
        
        # Ensure result is a dict
        if not isinstance(result, dict):
            result = {}
        
        # Add paper_id from stage1
        result['paper_id'] = stage1_json.get('paper_id', 'unknown')
        result['paper_title'] = stage1_json.get('paper_title', '')
        result['paper_authors'] = stage1_json.get('paper_authors', [])
        result['paper_abstract'] = stage1_json.get('paper_abstract', '')
        
        return result

