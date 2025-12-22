"""
Study & Data Extractor - Stage 2

Extracts study information, phenomena, research questions, statistical data,
and participant profiles from papers.
"""

import json
from pathlib import Path
from typing import Dict, Any

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
        response = self.client.generate_content(
            prompt=[uploaded_file, prompt]
        )
        
        # Parse response
        result = self._parse_response(response, stage1_json)
        
        return result
    
    def _build_prompt(self, stage1_json: Dict[str, Any], pdf_name: str, num_pages: int) -> str:
        """Build prompt for LLM"""
        experiments_info = json.dumps(stage1_json.get("experiments", []), indent=2)
        
        return f"""Analyze the research paper in the attached PDF file: {pdf_name} ({num_pages} pages)

STAGE 1 FILTER RESULTS:
{experiments_info}

Your task is to extract detailed information for each REPLICABLE experiment identified in Stage 1:

For each replicable experiment/study, extract:

1. STUDY INFORMATION:
   - Study ID/Number (e.g., "Study 1", "Experiment 1")
   - Study name/description
   - Core psychological phenomenon (e.g., "False Consensus Effect", "Anchoring Effect")

2. RESEARCH QUESTIONS WITH STATISTICAL DATA:
   For each research question that has quantitative/statistical data:
   - RQ ID and description
   - Statistical method used (t-test, chi-square, ANOVA, etc.)
   - Statistical results:
     * Test type
     * Statistic value (t, F, chi-square, etc.)
     * p-value
     * Degrees of freedom
     * Effect size (Cohen's d, eta-squared, etc.)
   - Descriptive statistics (means, standard deviations, proportions, etc.)

3. PARTICIPANT PROFILE:
   - Sample size (N)
   - Population description
   - Recruitment source
   - Demographics (age range, gender distribution, etc.)
   - Any other relevant participant information

IMPORTANT:
- Extract ALL statistical data from the paper (phenomenon-level)
- Include exact values from tables and text
- Note page numbers/sections where data is found
- If information is missing, mark as "missing" or "not reported"

Provide your analysis in JSON format:
{{
    "studies": [
        {{
            "study_id": "Study 1",
            "study_name": "Name or description",
            "phenomenon": "Core psychological phenomenon",
            "research_questions": [
                {{
                    "rq_id": "RQ1",
                    "description": "Research question description",
                    "has_quantitative_data": true,
                    "has_statistical_analysis": true,
                    "statistical_method": "t_test",
                    "statistical_results": {{
                        "test_type": "independent_t_test",
                        "statistic": 2.5,
                        "p_value": 0.01,
                        "df": 100,
                        "effect_size": {{
                            "type": "cohens_d",
                            "value": 0.5
                        }}
                    }},
                    "descriptive_statistics": {{
                        "condition_1": {{"mean": 75.0, "sd": 12.5, "n": 50}},
                        "condition_2": {{"mean": 65.0, "sd": 10.0, "n": 50}}
                    }},
                    "paper_location": "Page 5, Table 1"
                }}
            ],
            "participants": {{
                "n": 504,
                "population": "Stanford University Undergraduates",
                "recruitment_source": "Introductory Psychology Course",
                "demographics": {{
                    "age_range": [18, 22],
                    "gender_distribution": {{"male": 50, "female": 50}}
                }},
                "completeness": "complete",
                "missing_fields": []
            }}
        }}
    ]
}}"""
    
    def _parse_response(self, response: str, stage1_json: Dict[str, Any]) -> Dict[str, Any]:
        """Parse LLM response"""
        # Extract JSON from response
        response_text = response.strip()
        
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
        
        # Add paper_id from stage1
        result['paper_id'] = stage1_json.get('paper_id', 'unknown')
        result['paper_title'] = stage1_json.get('paper_title', '')
        result['paper_authors'] = stage1_json.get('paper_authors', [])
        result['paper_abstract'] = stage1_json.get('paper_abstract', '')
        
        return result

