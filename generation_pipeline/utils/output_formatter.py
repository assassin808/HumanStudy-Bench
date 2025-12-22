"""
Output Formatter - Formats extraction results as markdown review files and JSON
"""

import json
from pathlib import Path
from typing import Dict, Any
from datetime import datetime


class OutputFormatter:
    """Format extraction results for review"""
    
    @staticmethod
    def format_stage1_review(filter_result: Dict[str, Any]) -> str:
        """Format stage1 filter results as markdown"""
        md = f"""# Stage 1: Replicability Filter Review

## Paper Information
- **Title**: {filter_result.get('paper_title', 'N/A')}
- **Authors**: {', '.join(filter_result.get('paper_authors', []))}
- **Abstract**: {filter_result.get('paper_abstract', 'N/A')}

## Experiments Overview

"""
        
        experiments = filter_result.get('experiments', [])
        for i, exp in enumerate(experiments, 1):
            md += f"""### Experiment {i}: {exp.get('experiment_name', exp.get('experiment_id', 'Unknown'))}
- **Input**: {exp.get('input', 'N/A')}
- **Participants**: {exp.get('participants', 'N/A')}
- **Output**: {exp.get('output', 'N/A')}
- **Replicable**: {exp.get('replicable', 'UNCERTAIN')}
- **Exclusion Reasons**: {', '.join(exp.get('exclusion_reasons', [])) or 'None'}

#### Checklist:
- [ ] No visual input required
- [ ] No time perception/measurement required
- [ ] Participant profile can be constructed
- [ ] Has quantitative/statistical data
- [ ] Can be replicated with LLM agents

#### Comments:
[填写]

---

"""
        
        md += f"""## Overall Assessment
- **Overall Replicable**: {'YES' if filter_result.get('overall_replicable', False) else 'NO'}
- **Confidence**: {filter_result.get('confidence', 0.0):.2f}
- **Notes**: {filter_result.get('notes', 'N/A')}

## Review Status
- **Reviewed By**: [填写]
- **Review Status**: [pending/approved/needs_refinement]
- **Review Comments**: [填写]
- **Action**: [continue_to_stage2/refine_stage1/exclude]
"""
        
        return md
    
    @staticmethod
    def format_stage2_review(extraction_result: Dict[str, Any]) -> str:
        """Format stage2 extraction results as markdown"""
        md = f"""# Stage 2: Study & Data Extraction Review

"""
        
        studies = extraction_result.get('studies', [])
        for study in studies:
            study_id = study.get('study_id', 'Unknown')
            study_name = study.get('study_name', '')
            
            md += f"""## {study_id}: {study_name}

### Phenomenon
{study.get('phenomenon', 'N/A')}

### Research Questions with Statistical Data

"""
            
            rqs = study.get('research_questions', [])
            for rq in rqs:
                rq_id = rq.get('rq_id', 'Unknown')
                md += f"""#### {rq_id}: {rq.get('description', 'N/A')}
- **Has Quantitative Data**: {'YES' if rq.get('has_quantitative_data', False) else 'NO'}
- **Has Statistical Analysis**: {'YES' if rq.get('has_statistical_analysis', False) else 'NO'}
- **Statistical Method**: {rq.get('statistical_method', 'N/A')}
- **Statistical Results**:
  - Test type: {rq.get('statistical_results', {}).get('test_type', 'N/A')}
  - Statistic value: {rq.get('statistical_results', {}).get('statistic', 'N/A')}
  - p-value: {rq.get('statistical_results', {}).get('p_value', 'N/A')}
  - df: {rq.get('statistical_results', {}).get('df', 'N/A')}
  - Effect size: {rq.get('statistical_results', {}).get('effect_size', {}).get('value', 'N/A')}
- **Descriptive Statistics**: {json.dumps(rq.get('descriptive_statistics', {}), indent=2)}

#### Checklist:
- [ ] Phenomenon correctly identified
- [ ] All RQs with statistical data identified
- [ ] Statistical methods correctly extracted
- [ ] Statistical results correctly extracted
- [ ] Descriptive statistics correctly extracted

#### Comments:
[填写]

"""
            
            participants = study.get('participants', {})
            md += f"""### Participant Profile
- **N**: {participants.get('n', 'N/A')}
- **Population**: {participants.get('population', 'N/A')}
- **Recruitment Source**: {participants.get('recruitment_source', 'N/A')}
- **Demographics**: {json.dumps(participants.get('demographics', {}), indent=2)}
- **Completeness**: {participants.get('completeness', 'unknown')}
- **Missing Fields**: {', '.join(participants.get('missing_fields', [])) or 'None'}

#### Checklist:
- [ ] N correctly extracted
- [ ] Demographics correctly extracted
- [ ] All available information captured

#### Comments:
[填写]

---

"""
        
        md += """## Review Status
- **Reviewed By**: [填写]
- **Review Status**: [pending/approved/needs_refinement]
- **Review Comments**: [填写]
- **Action**: [continue_to_final/refine_stage2/back_to_stage1]
"""
        
        return md

