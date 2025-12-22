"""
Data Validation Agent

Verifies that human data (profile data and experimental data) in ground_truth.json
matches the original paper's reported results.
"""

from typing import Dict, Any
from validation_pipeline.agents.base_agent import BaseValidationAgent


class DataValidationAgent(BaseValidationAgent):
    """Agent that validates human data correctness"""
    
    def validate(self, documents: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify human data correctness.
        
        Args:
            documents: Dictionary containing PDF, ground_truth, etc.
            
        Returns:
            Validation results with data accuracy analysis
        """
        pdf_text = self._extract_pdf_text(documents)
        ground_truth = documents.get("json", {}).get("ground_truth.json", {})
        metadata = documents.get("json", {}).get("metadata.json", {})
        
        system_instruction = """You are an expert in statistical analysis and data validation. 
Your task is to verify that the human data reported in the benchmark's ground_truth.json 
matches the data reported in the original research paper. Pay attention to:
- Sample sizes
- Descriptive statistics (means, standard deviations, proportions)
- Effect sizes
- Statistical test results
- Participant demographics"""
        
        prompt = f"""Validate that the human data in the benchmark matches the original paper.

ORIGINAL PAPER:
{pdf_text[:50000]}

BENCHMARK GROUND TRUTH DATA:
{ground_truth}

BENCHMARK METADATA:
{metadata}

Please verify:
1. Participant profile data (N, demographics, recruitment)
2. Descriptive statistics for each experiment/condition
3. Effect sizes and statistical test results
4. Any reported percentages, means, standard deviations
5. Validation criteria and thresholds

For each data point:
- Extract the value from the original paper
- Extract the corresponding value from ground_truth.json
- Compare and note any discrepancies
- Assess if discrepancies are acceptable (rounding, reporting differences) or errors

Provide your analysis in JSON format:
{{
    "participant_data_validation": {{
        "sample_size": {{
            "paper": "Value from paper",
            "benchmark": "Value from ground_truth",
            "match": true/false,
            "notes": "Notes on comparison"
        }},
        "demographics": {{...}},
        "recruitment": {{...}}
    }},
    "experimental_data_validation": [
        {{
            "experiment_id": "Study 1",
            "data_type": "descriptive_stats|effect_size|test_results",
            "metric_name": "e.g., mean_choice_A",
            "paper_value": "Value from paper",
            "benchmark_value": "Value from ground_truth",
            "match": true/false,
            "discrepancy": "Description of any difference",
            "acceptable": true/false,
            "notes": "Assessment notes"
        }}
    ],
    "validation_summary": {{
        "total_data_points_checked": 0,
        "matching_data_points": 0,
        "acceptable_discrepancies": [],
        "potential_errors": [],
        "data_accuracy_score": 0.0,
        "overall_assessment": "Overall assessment of data accuracy"
    }},
    "critical_issues": [
        {{
            "issue": "Description of critical data issue",
            "severity": "critical|high|medium|low",
            "recommendation": "How to fix"
        }}
    ],
    "recommendations": [
        "Recommendations for improving data accuracy"
    ]
}}
"""
        
        result = self._generate_response(prompt, system_instruction, structured=True)
        
        return {
            "agent": "DataValidationAgent",
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

