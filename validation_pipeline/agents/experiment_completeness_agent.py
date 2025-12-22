"""
Experiment Completeness Agent

Verifies that all replicable experiments from the original paper are included
in the benchmark implementation.
"""

from typing import Dict, Any
from validation_pipeline.agents.base_agent import BaseValidationAgent


class ExperimentCompletenessAgent(BaseValidationAgent):
    """Agent that verifies all experiments are included"""
    
    def validate(self, documents: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify that all replicable experiments are included.
        
        Args:
            documents: Dictionary containing PDF, README, and config files
            
        Returns:
            Validation results with completeness analysis
        """
        # Extract relevant content
        pdf_text = self._extract_pdf_text(documents)
        study_info = documents.get("study_info", "")
        specification = documents.get("json", {}).get("specification.json", {})
        config_code = documents.get("config_code", "")
        
        system_instruction = """You are an expert in experimental psychology and research methodology. 
Your task is to analyze whether all replicable experiments from a research paper have been 
correctly included in a benchmark implementation. Be thorough and precise in your analysis."""
        
        prompt = f"""Analyze the completeness of experiment transfer from the original paper to the benchmark implementation.

ORIGINAL PAPER CONTENT:
{pdf_text[:50000]}  # Limit to avoid token limits

STUDY INFORMATION:
{study_info}

BENCHMARK SPECIFICATION:
{specification}

IMPLEMENTATION CODE (if available):
{config_code[:20000] if config_code else "Not provided"}

Please analyze:
1. List ALL experiments/studies mentioned in the original paper
2. For each experiment, determine if it is replicable (has sufficient detail, measurable outcomes, etc.)
3. Check if each replicable experiment is included in the benchmark implementation
4. Identify any missing experiments
5. Note any experiments that were intentionally excluded and why (if stated)

Provide your analysis in the following JSON format:
{{
    "experiments_in_paper": [
        {{
            "experiment_id": "Study 1",
            "description": "Brief description",
            "replicable": true/false,
            "replicable_reason": "Why it is or isn't replicable",
            "included_in_benchmark": true/false,
            "implementation_details": "How it's implemented or why excluded",
            "notes": "Additional notes"
        }}
    ],
    "completeness_summary": {{
        "total_experiments": 0,
        "replicable_experiments": 0,
        "included_experiments": 0,
        "missing_experiments": [],
        "intentionally_excluded": [],
        "completeness_score": 0.0,
        "completeness_notes": "Overall assessment"
    }},
    "recommendations": [
        "List of recommendations for improving completeness"
    ]
}}
"""
        
        result = self._generate_response(prompt, system_instruction, structured=True)
        
        return {
            "agent": "ExperimentCompletenessAgent",
            "status": "completed",
            "results": result,
        }
    
    def _extract_pdf_text(self, documents: Dict[str, Any]) -> str:
        """Extract PDF text from documents"""
        pdfs = documents.get("pdfs", {})
        if not pdfs:
            return "No PDF files found"
        
        # Combine all PDFs
        all_text = []
        for pdf_name, pdf_content in pdfs.items():
            all_text.append(f"=== {pdf_name} ===\n{pdf_content}")
        
        return "\n\n".join(all_text)

