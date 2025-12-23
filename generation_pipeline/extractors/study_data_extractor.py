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

For EACH replicable study/experiment, extract:

1. STUDY STRUCTURE:
   - Study ID (e.g., "Study 1", "Study 2")
   - Study name/description
   - Core psychological phenomenon
   - List ALL sub-studies/scenarios/conditions within this study (e.g., Study 1 has 4 scenarios: supermarket, term_paper, traffic_ticket, space_program)

2. MATERIALS/QUESTIONS FOR EACH SUB-STUDY:
   For each sub-study/scenario:
   - Sub-study ID (e.g., "study_1_supermarket", "study_2_items")
   - Type: "scenario" (story/text), "questionnaire" (items/questions), or "task" (specific task)
   - Content: Extract the actual text/content of scenarios, questions, or items
   - For questionnaires: List all items/questions with their options

3. PARTICIPANT INFORMATION (FOR EACH SUB-STUDY):
   - N for each sub-study/scenario
   - Population description
   - Recruitment source
   - Demographics (age range, gender distribution, etc.)
   - Note: If different sub-studies have different N, list them separately

4. HUMAN DATA (ORIGINAL RESULTS):
   For each sub-study/scenario, extract:
   - All reported means, percentages, proportions
   - Standard deviations (if reported)
   - Sample sizes
   - Any calculated metrics (e.g., FCE = False Consensus Effect magnitude)
   - Organize by condition/group (e.g., "signers" vs "refusers", "choosers" vs "non-choosers")

5. STATISTICAL TESTS:
   For each statistical test reported:
   - Test type (t-test, ANOVA, chi-square, etc.)
   - Test statistic value
   - p-value
   - Degrees of freedom
   - Effect size (if reported)
   - Which sub-study/scenario it applies to

IMPORTANT:
- Extract ALL sub-studies/scenarios mentioned in the paper
- Extract the ACTUAL TEXT of scenarios/questions (not just descriptions)
- Extract ALL human data values (means, percentages, etc.) for each sub-study
- Organize data by sub-study, not just by overall study
- Include page numbers/table references for all data

Provide your analysis in JSON format:
{{
    "studies": [
        {{
            "study_id": "Study 1",
            "study_name": "Hypothetical Scenarios",
            "phenomenon": "False Consensus Effect",
            "sub_studies": [
                {{
                    "sub_study_id": "study_1_supermarket",
                    "type": "scenario",
                    "content": "Full text of the scenario/story...",
                    "participants": {{
                        "n": 80,
                        "population": "Stanford University Undergraduates",
                        "recruitment_source": "...",
                        "demographics": {{...}}
                    }},
                    "human_data": {{
                        "sign_estimate_by_signers": 75.6,
                        "sign_estimate_by_refusers": 57.3,
                        "fce": 18.3
                    }},
                    "statistical_tests": [
                        {{
                            "test_type": "t_test",
                            "statistic": 2.5,
                            "p_value": 0.01,
                            "df": 78,
                            "paper_location": "Page X, Table Y"
                        }}
                    ]
                }}
            ],
            "overall_participants": {{
                "total_n": 320,
                "population": "Stanford University Undergraduates",
                "recruitment_source": "...",
                "demographics": {{...}}
            }}
        }},
        {{
            "study_id": "Study 2",
            "study_name": "Questionnaire",
            "phenomenon": "False Consensus Effect",
            "sub_studies": [
                {{
                    "sub_study_id": "study_2_items",
                    "type": "questionnaire",
                    "content": "List of all 35 items with options",
                    "items": [
                        {{
                            "id": "shy",
                            "category": "Shy/Outgoing",
                            "option_a": "...",
                            "option_b": "..."
                        }}
                    ],
                    "participants": {{
                        "n": 80,
                        ...
                    }},
                    "human_data": {{
                        "overall_fce": 10.5
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

