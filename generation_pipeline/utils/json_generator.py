"""
JSON Generator - Generates compatible JSON files (metadata.json, specification.json, ground_truth.json)
and materials files
"""

import json
from pathlib import Path
from typing import Dict, Any, List


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
        
        # Collect all scenarios from all sub-studies
        scenarios = []
        for study in studies:
            sub_studies = study.get('sub_studies', [])
            for sub_study in sub_studies:
                sub_id = sub_study.get('sub_study_id', '')
                if sub_id:
                    scenarios.append(sub_id)
        
        # Extract domain/subdomain from paper (try to infer from phenomenon)
        study = studies[0]
        phenomenon = study.get('phenomenon', '').lower()
        
        domain = None
        subdomain = None
        if 'consensus' in phenomenon or 'social' in phenomenon:
            domain = "social_psychology"
            subdomain = "social_cognition"
        elif 'anchoring' in phenomenon or 'framing' in phenomenon:
            domain = "cognitive_psychology"
            subdomain = "judgment_and_decision_making"
        elif 'representativeness' in phenomenon:
            domain = "cognitive_psychology"
            subdomain = "judgment_and_decision_making"
        
        # Extract keywords from phenomenon
        keywords = [phenomenon.replace(' ', '_')] if phenomenon else []
        
        return {
            "id": study_id,
            "title": extraction_result.get('paper_title', ''),
            "authors": extraction_result.get('paper_authors', []),
            "year": extraction_result.get('paper_year'),  # Should be extracted in stage2
            "domain": domain,
            "subdomain": subdomain,
            "keywords": keywords,
            "difficulty": "medium",  # TODO: Determine from study complexity
            "description": extraction_result.get('paper_abstract', '')[:200] + "...",
            "scenarios": scenarios
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
        
        # Aggregate participants across all studies
        total_n = 0
        all_demographics = {}
        population = None
        recruitment_source = None
        
        # Collect design factors from sub-studies
        factors = []
        factor_names = set()
        
        for study in studies:
            overall_participants = study.get('overall_participants', {})
            if overall_participants:
                total_n += overall_participants.get('total_n', 0)
                if not population:
                    population = overall_participants.get('population', '')
                if not recruitment_source:
                    recruitment_source = overall_participants.get('recruitment_source', '')
                demos = overall_participants.get('demographics', {})
                if demos:
                    all_demographics.update(demos)
            
            # Extract design factors
            sub_studies = study.get('sub_studies', [])
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
        
        return {
            "study_id": study_id,
            "title": extraction_result.get('paper_title', ''),
            "participants": {
                "n": total_n,
                "population": population or "Not specified",
                "recruitment_source": recruitment_source or "Not specified",
                "demographics": all_demographics
            },
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
    
    @staticmethod
    def generate_materials(extraction_result: Dict[str, Any], study_dir: Path) -> List[Path]:
        """
        Generate materials files for each sub-study.
        
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
