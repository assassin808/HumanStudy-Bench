"""
Experiment Consistency Agent

Verifies that experimental setup matches the original paper, and identifies
any inconsistencies with special markings and validation methods.
"""

from typing import Dict, Any
from validation_pipeline.agents.base_agent import BaseValidationAgent


class ExperimentConsistencyAgent(BaseValidationAgent):
    """Agent that verifies experimental setup consistency"""
    
    def validate(self, documents: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify experimental setup consistency.
        
        Args:
            documents: Dictionary containing PDF, README, and config files
            
        Returns:
            Validation results with consistency analysis
        """
        pdf_text = self._extract_pdf_text(documents)
        study_info = documents.get("study_info", "")
        specification = documents.get("json", {}).get("specification.json", {})
        metadata = documents.get("json", {}).get("metadata.json", {})
        config_code = documents.get("config_code", "")
        
        system_instruction = """You are an expert in experimental design and methodology. 
Your task is to compare the experimental setup in the original paper with the benchmark 
implementation and identify any inconsistencies. Be precise and note both exact matches 
and intentional modifications."""
        
        prompt = f"""Compare the experimental setup between the original paper and the benchmark implementation.

ORIGINAL PAPER:
{pdf_text[:50000]}

STUDY INFORMATION:
{study_info}

BENCHMARK METADATA:
{metadata}

BENCHMARK SPECIFICATION:
{specification}

IMPLEMENTATION CODE:
{config_code[:20000] if config_code else "Not provided"}

For each aspect of the experimental design, compare:
1. Participant characteristics (N, demographics, recruitment)
2. Experimental procedure and steps
3. Materials and stimuli
4. Dependent variables and measures
5. Statistical analyses
6. Conditions and manipulations

For each inconsistency found:
- Mark whether it's an intentional modification or an error
- Provide the original paper's description
- Provide the benchmark's implementation
- Suggest validation methods to verify the modification is acceptable
- Note if the modification affects replicability

Provide your analysis in JSON format:
{{
    "comparison_by_aspect": {{
        "participants": {{
            "original": "Description from paper",
            "benchmark": "Description from implementation",
            "consistent": true/false,
            "modification_type": "exact_match|intentional_modification|error|unclear",
            "validation_method": "How to validate this aspect",
            "notes": "Additional notes"
        }},
        "procedure": {{...}},
        "materials": {{...}},
        "measures": {{...}},
        "analyses": {{...}},
        "conditions": {{...}}
    }},
    "consistency_summary": {{
        "total_aspects_checked": 0,
        "consistent_aspects": 0,
        "intentional_modifications": [],
        "potential_errors": [],
        "unclear_aspects": [],
        "consistency_score": 0.0,
        "overall_assessment": "Overall assessment of consistency"
    }},
    "validation_plan": [
        {{
            "aspect": "Name of aspect",
            "validation_method": "How to validate",
            "priority": "high|medium|low",
            "description": "Detailed validation steps"
        }}
    ],
    "recommendations": [
        "Recommendations for improving consistency or documenting modifications"
    ]
}}
"""
        
        result = self._generate_response(prompt, system_instruction, structured=True)
        
        return {
            "agent": "ExperimentConsistencyAgent",
            "status": "completed",
            "results": result,
        }
    
    def _extract_pdf_text(self, documents: Dict[str, Any]) -> str:
        """Extract PDF text from documents"""
        pdfs = documents.get("pdfs", {})
        if not pdfs:
            return "No PDF files found"
        
        all_text = []
        for pdf_name, pdf_content in pdfs.items():
            all_text.append(f"=== {pdf_name} ===\n{pdf_content}")
        
        return "\n\n".join(all_text)

