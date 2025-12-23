"""
Replicability Filter - Stage 1

Filters papers based on whether they can be replicated using LLM agents.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from generation_pipeline.filters.base_filter import BaseFilter
from generation_pipeline.utils.document_loader import DocumentLoader


class ReplicabilityFilter(BaseFilter):
    """Filter papers for LLM replicability"""
    
    def process(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Process PDF and determine replicability.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with filter results:
            {
                "paper_id": str,
                "paper_title": str,
                "paper_authors": List[str],
                "paper_abstract": str,
                "experiments": [...],
                "overall_replicable": bool,
                "confidence": float,
                "notes": str
            }
        """
        # Load PDF
        loader = DocumentLoader()
        pdf_info = loader.get_pdf_pages(pdf_path)
        
        # Upload PDF to Gemini
        uploaded_file = self.client.upload_file(pdf_path)
        
        # Generate prompt
        prompt = self._build_prompt(pdf_path.name, len(pdf_info))
        
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
        result = self._parse_response(response, pdf_path)
        
        return result
    
    def _build_prompt(self, pdf_name: str, num_pages: int) -> str:
        """Build prompt for LLM"""
        return f"""Analyze the research paper in the attached PDF file: {pdf_name} ({num_pages} pages)

Your task is to:
1. Extract the paper's title, authors, and abstract
2. Identify all experiments/studies in the paper
3. For each experiment, determine if it can be replicated using LLM agents

EXCLUSION CRITERIA (experiment is NOT replicable if):
- Requires visual input (images, videos, visual stimuli)
- Requires time perception/measurement (reaction time, duration judgments)
- Participant profile is too vague to construct (cannot determine demographics, recruitment source, etc.)
- Has no quantitative/statistical data

For each experiment, provide:
- Experiment name/number
- Input: What participants receive/see
- Participants: Brief description of participant characteristics
- Output: What is measured/collected
- Replicable: YES/NO/UNCERTAIN
- Exclusion Reasons: If not replicable, list the reasons

Provide your analysis in JSON format:
{{
    "paper_title": "Title of the paper",
    "paper_authors": ["Author 1", "Author 2", ...],
    "paper_abstract": "Full abstract text",
    "experiments": [
        {{
            "experiment_id": "Experiment 1",
            "experiment_name": "Name or description",
            "input": "What participants receive/see",
            "participants": "Brief description",
            "output": "What is measured/collected",
            "replicable": "YES/NO/UNCERTAIN",
            "exclusion_reasons": ["reason1", "reason2"] or []
        }}
    ],
    "overall_replicable": true/false,
    "confidence": 0.0-1.0,
    "notes": "Additional notes or observations"
}}

IMPORTANT: Only include experiments that have quantitative/statistical data. If an experiment is purely qualitative or lacks statistical analysis, mark it as NOT replicable."""
    
    def _parse_response(self, response: str, pdf_path: Path) -> Dict[str, Any]:
        """Parse LLM response"""
        if response is None:
            raise ValueError("LLM response is None")
        
        # Extract JSON from response (may have markdown code blocks)
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
        
        # Add paper_id (derived from PDF filename)
        paper_id = pdf_path.stem.replace(' ', '_').replace('-', '_').lower()
        result['paper_id'] = paper_id
        
        return result

