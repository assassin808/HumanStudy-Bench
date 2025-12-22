"""
JSON Generator - Generates compatible JSON files (metadata.json, specification.json, ground_truth.json)
"""

import json
from pathlib import Path
from typing import Dict, Any


class JSONGenerator:
    """Generate JSON files compatible with existing study format"""
    
    @staticmethod
    def generate_metadata(extraction_result: Dict[str, Any], study_id: str) -> Dict[str, Any]:
        """
        Generate metadata.json compatible with study001-004 format.
        
        Args:
            extraction_result: Results from stage2 extraction
            study_id: Study ID (e.g., "study_005")
            
        Returns:
            Dictionary matching metadata.json format
        """
        studies = extraction_result.get('studies', [])
        if not studies:
            raise ValueError("No studies found")
        
        study = studies[0]
        phenomenon = study.get('phenomenon', '')
        
        # Extract keywords from phenomenon
        keywords = [phenomenon.lower().replace(' ', '_')] if phenomenon else []
        
        return {
            "id": study_id,
            "title": extraction_result.get('paper_title', ''),
            "authors": extraction_result.get('paper_authors', []),
            "year": None,  # TODO: Extract from paper
            "domain": None,  # TODO: Extract from paper
            "subdomain": None,  # TODO: Extract from paper
            "keywords": keywords,
            "difficulty": "medium",  # TODO: Determine from study complexity
            "description": extraction_result.get('paper_abstract', '')[:200] + "..."
        }
    
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
        
        study = studies[0]
        participants = study.get('participants', {})
        
        return {
            "study_id": study_id,
            "title": extraction_result.get('paper_title', ''),
            "participants": {
                "n": participants.get('n', 100),
                "population": participants.get('population', ''),
                "recruitment_source": participants.get('recruitment_source', ''),
                "demographics": participants.get('demographics', {})
            },
            "design": {
                "type": "between_subjects",  # TODO: Extract from study design
                "factors": []  # TODO: Extract from study design
            },
            "procedure": {
                "description": "Auto-generated from paper extraction"
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
        
        study = studies[0]
        rqs = study.get('research_questions', [])
        
        # Generate validation criteria from RQs
        required_tests = []
        for i, rq in enumerate(rqs, 1):
            if rq.get('has_statistical_analysis', False):
                stat_results = rq.get('statistical_results', {})
                test_type = stat_results.get('test_type', 'unknown')
                
                test = {
                    "test_id": f"P{i}",
                    "test_name": f"{rq.get('rq_id', f'RQ{i}')} Significance",
                    "test_type": "phenomenon_level",
                    "difficulty": "medium",
                    "description": f"Tests if {rq.get('description', 'effect')} is statistically significant",
                    "method": {
                        "test": test_type,
                        "threshold": 0.05,
                        "expected_direction": "positive"  # TODO: Extract from results
                    },
                    "critical": True,
                    "weight": 1.0
                }
                required_tests.append(test)
        
        return {
            "study_id": study_id,
            "title": extraction_result.get('paper_title', ''),
            "authors": extraction_result.get('paper_authors', []),
            "year": None,  # TODO: Extract from paper
            "validation_criteria": {
                "required_tests": required_tests
            },
            "original_results": {
                # TODO: Extract from research_questions statistical_data
            }
        }

