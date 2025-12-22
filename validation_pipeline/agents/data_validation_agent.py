"""
Data Validation Agent

Verifies that human data (profile data and experimental data) in ground_truth.json
matches the original paper's reported results.
"""

from typing import Dict, Any, List
from pathlib import Path
from validation_pipeline.agents.base_agent import BaseValidationAgent


class DataValidationAgent(BaseValidationAgent):
    """Agent that validates human data correctness"""
    
    def validate(self, documents: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify human data correctness.
        Processes PDF by pages to avoid truncation, matching each page with corresponding data.
        
        Args:
            documents: Dictionary containing PDF, ground_truth, etc.
            
        Returns:
            Validation results with data accuracy analysis
        """
        pdf_info = documents.get("pdfs", {})
        ground_truth = documents.get("json", {}).get("ground_truth.json", {})
        metadata = documents.get("json", {}).get("metadata.json", {})
        
        if not pdf_info:
            raise ValueError("No PDF files found in documents")
        
        system_instruction = """You are an expert in statistical analysis and data validation. 
Your task is to verify that the human data reported in the benchmark's ground_truth.json 
matches the data reported in the original research paper. Pay attention to:
- Sample sizes
- Descriptive statistics (means, standard deviations, proportions)
- Effect sizes
- Statistical test results
- Participant demographics"""
        
        # Process each PDF file by pages
        all_validation_results = []
        
        for pdf_name, pdf_data in pdf_info.items():
            pdf_path = Path(pdf_data["path"])
            total_pages = pdf_data["page_count"]
            
            # Upload the full PDF file
            uploaded_file = self.client.upload_file(pdf_path)
            
            # Process the entire PDF with all data
            # We'll use the full PDF and match it with the corresponding data sections
            text_prompt = f"""Validate that the human data in the benchmark matches the original paper.

You are analyzing the PDF file: {pdf_name} (total {total_pages} pages)

BENCHMARK GROUND TRUTH DATA:
{ground_truth}

BENCHMARK METADATA:
{metadata}

Please verify by going through the PDF systematically:
1. Participant profile data (N, demographics, recruitment)
2. Descriptive statistics for each experiment/condition
3. Effect sizes and statistical test results
4. Any reported percentages, means, standard deviations
5. Validation criteria and thresholds

For each data point found in the paper:
- Extract the value from the original paper (note which page/section)
- Extract the corresponding value from ground_truth.json
- Compare and note any discrepancies
- Assess if discrepancies are acceptable (rounding, reporting differences) or errors

IMPORTANT: Process ALL pages of the PDF. Do not skip any data. Match each statistical result 
in the paper with the corresponding entry in ground_truth.json.

Provide your analysis in JSON format:
{{
    "participant_data_validation": {{
        "sample_size": {{
            "paper": "Value from paper",
            "paper_location": "Page/section reference",
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
            "paper_location": "Page/section reference",
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
            
            # Use the uploaded PDF file with the prompt
            prompt_parts = [uploaded_file, text_prompt]
            result = self._generate_response(prompt_parts, system_instruction, structured=True)
            all_validation_results.append({
                "pdf_name": pdf_name,
                "validation": result
            })
        
        # Combine results from all PDFs
        if len(all_validation_results) == 1:
            combined_result = all_validation_results[0]["validation"]
        else:
            # Merge results from multiple PDFs
            combined_result = self._merge_validation_results(all_validation_results)
        
        return {
            "agent": "DataValidationAgent",
            "status": "completed",
            "results": combined_result,
        }
    
    def _merge_validation_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge validation results from multiple PDFs"""
        merged = {
            "participant_data_validation": {},
            "experimental_data_validation": [],
            "validation_summary": {
                "total_data_points_checked": 0,
                "matching_data_points": 0,
                "acceptable_discrepancies": [],
                "potential_errors": [],
                "data_accuracy_score": 0.0,
                "overall_assessment": ""
            },
            "critical_issues": [],
            "recommendations": []
        }
        
        for result_item in results:
            validation = result_item["validation"]
            
            # Merge participant data
            if "participant_data_validation" in validation:
                merged["participant_data_validation"].update(validation["participant_data_validation"])
            
            # Merge experimental data
            if "experimental_data_validation" in validation:
                merged["experimental_data_validation"].extend(validation["experimental_data_validation"])
            
            # Merge summary
            if "validation_summary" in validation:
                summary = validation["validation_summary"]
                merged["validation_summary"]["total_data_points_checked"] += summary.get("total_data_points_checked", 0)
                merged["validation_summary"]["matching_data_points"] += summary.get("matching_data_points", 0)
                merged["validation_summary"]["acceptable_discrepancies"].extend(summary.get("acceptable_discrepancies", []))
                merged["validation_summary"]["potential_errors"].extend(summary.get("potential_errors", []))
            
            # Merge critical issues and recommendations
            if "critical_issues" in validation:
                merged["critical_issues"].extend(validation["critical_issues"])
            if "recommendations" in validation:
                merged["recommendations"].extend(validation["recommendations"])
        
        # Calculate overall score
        total = merged["validation_summary"]["total_data_points_checked"]
        matching = merged["validation_summary"]["matching_data_points"]
        if total > 0:
            merged["validation_summary"]["data_accuracy_score"] = matching / total
        
        return merged

