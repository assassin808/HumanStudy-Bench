"""
Prompt Builder - Convert study specifications into LLM prompts.

This module handles the critical translation from experimental design (specification.json)
to actual prompts that LLM agents receive as participants.
"""

import json
import re
from pathlib import Path
from typing import Dict, Any, List, Optional


class PromptBuilder:
    """
    Base class for building prompts from study specifications.
    
    Key responsibility: Transform technical specification.json
    into natural language prompts for LLM participants.
    """
    
    def __init__(self, study_path: Path):
        """
        Initialize prompt builder with study materials.
        
        Args:
            study_path: Path to study directory (e.g., data/studies/study_001/)
        """
        self.study_path = Path(study_path)
        self.materials_path = self.study_path / "materials"
        self.prompts_path = self.materials_path / "prompts"
        
        # Load specification
        with open(self.study_path / "specification.json", "r") as f:
            self.specification = json.load(f)
        
        # Load instructions
        instructions_file = self.materials_path / "instructions.txt"
        if instructions_file.exists():
            with open(instructions_file, "r") as f:
                self.instructions = f.read()
        else:
            self.instructions = None
        
        # Load prompt templates if they exist
        self.system_template = self._load_template("system_prompt_template.txt")
        self.trial_template = self._load_template("trial_prompt_template.txt")
    
    def _load_template(self, filename: str) -> Optional[str]:
        """Load a prompt template file."""
        template_path = self.prompts_path / filename
        if template_path.exists():
            with open(template_path, "r") as f:
                return f.read()
        return None
    
    def build_system_prompt(self, participant_profile: Dict[str, Any]) -> str:
        """
        Build the system prompt that defines the participant's identity.
        
        Args:
            participant_profile: Dictionary with age, gender, personality traits, etc.
            
        Returns:
            Complete system prompt string
        """
        if self.system_template:
            return self._fill_template(self.system_template, participant_profile)
        else:
            # Fallback to generic system prompt
            return self._build_generic_system_prompt(participant_profile)
    
    def build_trial_prompt(self, trial_data: Dict[str, Any]) -> str:
        """
        Build the prompt for a single trial.
        
        Args:
            trial_data: Trial-specific information (stimuli, confederate responses, etc.)
            
        Returns:
            Complete trial prompt string
        """
        if self.trial_template:
            return self._fill_template(self.trial_template, trial_data)
        else:
            # Fallback to generic trial prompt
            return self._build_generic_trial_prompt(trial_data)
    
    def get_instructions(self) -> str:
        """
        Get the experimental instructions.
        
        Returns:
            Instructions text (from materials/instructions.txt)
        """
        return self.instructions if self.instructions else "No instructions provided."
    
    def _fill_template(self, template: str, data: Dict[str, Any]) -> str:
        """
        Fill template with data using simple {{variable}} syntax.
        
        Supports:
        - {{variable}}: Simple substitution
        - {{object.key}}: Nested property access
        - {{#if variable}}...{{/if}}: Conditional blocks
        - {{#each array}}{{this}}{{/each}}: Loops (simplified)
        """
        result = template
        
        # Handle nested property access (e.g., {{comparison_lines.A}})
        nested_pattern = r'\{\{([\w.]+)\}\}'
        
        def replace_nested(match):
            path = match.group(1)
            parts = path.split('.')
            
            value = data
            for part in parts:
                if isinstance(value, dict) and part in value:
                    value = value[part]
                else:
                    return match.group(0)  # Keep original if not found
            
            return str(value)
        
        result = re.sub(nested_pattern, replace_nested, result)
        
        # Handle conditional blocks (simplified)
        # {{#if variable}}...{{/if}}
        if_pattern = r'\{\{#if\s+(\w+)\}\}(.*?)\{\{/if\}\}'
        
        def replace_if(match):
            var_name = match.group(1)
            content = match.group(2)
            # Check if variable exists and is truthy
            if var_name in data and data[var_name]:
                return content
            return ""
        
        result = re.sub(if_pattern, replace_if, result, flags=re.DOTALL)
        
        # Handle each loops (simplified)
        # {{#each array}}{{this}}{{/each}}
        each_pattern = r'\{\{#each\s+(\w+)\}\}(.*?)\{\{/each\}\}'
        
        def replace_each(match):
            var_name = match.group(1)
            content = match.group(2)
            
            if var_name not in data:
                return ""
            
            items = data[var_name]
            if isinstance(items, dict):
                # Dictionary: replace {{@key}} and {{this}}
                parts = []
                for key, value in items.items():
                    item_content = content.replace("{{@key}}", str(key))
                    item_content = item_content.replace("{{this}}", str(value))
                    parts.append(item_content)
                return "\n".join(parts)
            elif isinstance(items, list):
                # List: replace {{this}} and {{@index}}
                parts = []
                for idx, item in enumerate(items):
                    item_content = content.replace("{{@index}}", str(idx + 1))
                    item_content = item_content.replace("{{this}}", str(item))
                    parts.append(item_content)
                return "\n".join(parts)
            return ""
        
        result = re.sub(each_pattern, replace_each, result, flags=re.DOTALL)
        
        # Clean up any remaining unfilled placeholders
        result = re.sub(r'\{\{[^}]+\}\}', '', result)
        
        return result
    
    def _build_generic_system_prompt(self, profile: Dict[str, Any]) -> str:
        """Fallback generic system prompt."""
        age = profile.get('age', 'unknown age')
        gender = profile.get('gender', 'unspecified gender')
        
        return f"""You are participating in a psychology experiment as a real human participant.

Your identity: {age} years old, {gender}

Respond naturally as this person would. Do not explain your reasoning - just give direct responses as a real participant would."""
    
    def _build_generic_trial_prompt(self, trial_data: Dict[str, Any]) -> str:
        """Fallback generic trial prompt."""
        return f"Trial {trial_data.get('trial_number', '?')}: Please respond to the following stimulus."


class AschPromptBuilder(PromptBuilder):
    """
    Specialized prompt builder for Asch Conformity experiments.
    
    Handles:
    - Visual line comparison stimuli
    - Confederate responses  
    - Social pressure context
    """
    
    def build_system_prompt(self, participant_profile: Dict[str, Any]) -> str:
        """Build Asch-specific system prompt."""
        # Enhance profile with personality descriptions
        enhanced_profile = participant_profile.copy()
        
        # Generate personality description
        traits = participant_profile.get('personality_traits', {})
        conformity = traits.get('conformity_tendency', 0.5)
        
        if conformity > 0.7:
            enhanced_profile['personality_description'] = (
                "You tend to value group harmony and often agree with others' opinions. "
                "You feel uncomfortable standing out or disagreeing with the majority."
            )
        elif conformity < 0.3:
            enhanced_profile['personality_description'] = (
                "You are independent-minded and confident in your own judgment. "
                "You're not easily swayed by others' opinions when you're sure you're right."
            )
        else:
            enhanced_profile['personality_description'] = (
                "You balance your own judgment with others' opinions. "
                "Sometimes you trust your own perception, sometimes you wonder if others see something you don't."
            )
        
        return super().build_system_prompt(enhanced_profile)
    
    def build_trial_prompt(self, trial_data: Dict[str, Any]) -> str:
        """
        Build Asch trial prompt with visual line representation.
        
        Expected trial_data:
        {
            "trial_number": 1,
            "standard_length": 10,
            "comparison_lines": {"A": 8, "B": 10, "C": 12},
            "correct_answer": "B",
            "confederate_responses": ["A", "A", "A", "A", "A", "A"]  # optional
        }
        """
        # Enhance trial data with visual representation flag
        enhanced_data = trial_data.copy()
        enhanced_data['show_visual'] = True
        enhanced_data['standard_length'] = trial_data.get('standard_line_length', 
                                                          trial_data.get('standard_length', 10))
        
        # Ensure comparison_lines is in the right format
        if 'comparison_lines' in trial_data:
            comp_lines = trial_data['comparison_lines']
            if isinstance(comp_lines, dict):
                enhanced_data['comparison_lines'] = comp_lines
            else:
                # Convert list to dict
                enhanced_data['comparison_lines'] = {
                    'A': comp_lines[0] if len(comp_lines) > 0 else 8,
                    'B': comp_lines[1] if len(comp_lines) > 1 else 10,
                    'C': comp_lines[2] if len(comp_lines) > 2 else 12
                }
        
        # Add first confederate response for easy access
        if 'confederate_responses' in trial_data and trial_data['confederate_responses']:
            enhanced_data['confederate_first'] = trial_data['confederate_responses'][0]
        
        return super().build_trial_prompt(enhanced_data)


class MilgramPromptBuilder(PromptBuilder):
    """
    Specialized prompt builder for Milgram Obedience experiments.
    
    Handles:
    - Shock generator context
    - Learner responses (screams, silence)
    - Experimenter prods
    - Moral conflict framing
    """
    
    def build_system_prompt(self, participant_profile: Dict[str, Any]) -> str:
        """Build Milgram-specific system prompt."""
        # Enhance profile with occupation and personality
        enhanced_profile = participant_profile.copy()
        
        # Generate personality description
        traits = participant_profile.get('personality_traits', {})
        obedience = traits.get('authority_obedience', 0.65)
        empathy = traits.get('empathy', 0.5)
        
        if obedience > 0.7 and empathy < 0.5:
            enhanced_profile['personality_description'] = (
                "You respect authority and believe in following instructions from experts. "
                "You tend to trust that scientists know what they're doing."
            )
        elif obedience < 0.4 or empathy > 0.7:
            enhanced_profile['personality_description'] = (
                "You have a strong moral compass and empathy for others. "
                "You question authority when you believe something is wrong."
            )
        else:
            enhanced_profile['personality_description'] = (
                "You try to balance respect for authority with concern for others. "
                "You feel torn when these values conflict."
            )
        
        # Add occupation if not present
        if 'occupation' not in enhanced_profile:
            enhanced_profile['occupation'] = "worker"
        
        return super().build_system_prompt(enhanced_profile)
    
    def build_trial_prompt(self, trial_data: Dict[str, Any]) -> str:
        """
        Build Milgram trial prompt with shock context.
        
        Expected trial_data:
        {
            "shock_level": 15,
            "voltage": 300,
            "label": "Intense Shock",
            "learner_response_correctness": "Wrong",
            "learner_gave_error": true,
            "learner_verbal_response": "Ugh! Get me out of here!",
            "learner_is_silent": false,
            "experimenter_prod": "Please continue.",
            "previous_hesitation": true
        }
        """
        # Get learner response from specification
        shock_level = trial_data.get('voltage', trial_data.get('shock_level', 0))
        
        # Find learner response from specification
        learner_schedule = self.specification.get('procedure', {}).get('learner_responses', {}).get('schedule', [])
        learner_verbal = ""
        learner_is_silent = False
        
        for response_entry in learner_schedule:
            if response_entry['shock_level'] == shock_level:
                learner_verbal = response_entry['response']
                if learner_verbal == "(silence)":
                    learner_is_silent = True
                    learner_verbal = ""
                break
        
        # Get shock label
        labels = self.specification.get('procedure', {}).get('shock_generator', {}).get('verbal_labels', {})
        label = "Shock"
        for voltage_range, range_label in labels.items():
            # Parse range like "15-60"
            if '-' in voltage_range:
                low, high = map(int, voltage_range.split('-'))
                if low <= shock_level <= high:
                    label = range_label
                    break
        
        # Enhance trial data
        enhanced_data = trial_data.copy()
        enhanced_data.update({
            'shock_level': shock_level // 15,  # Shock number (1-30)
            'voltage': shock_level,
            'label': label,
            'learner_verbal_response': learner_verbal,
            'learner_is_silent': learner_is_silent,
            'learner_gave_error': True  # Always true in Milgram
        })
        
        return super().build_trial_prompt(enhanced_data)


def create_prompt_builder(study_path: Path) -> PromptBuilder:
    """
    Factory function to create appropriate PromptBuilder for a study.
    
    Args:
        study_path: Path to study directory
        
    Returns:
        PromptBuilder instance (specialized or generic)
    """
    study_path = Path(study_path)
    
    # Load specification to determine study type
    with open(study_path / "specification.json", "r") as f:
        spec = json.load(f)
    
    study_type = spec.get('study_type', spec.get('study_id', ''))
    
    # Return specialized builder based on study type
    if 'asch' in study_type.lower() or 'conformity' in study_type.lower():
        return AschPromptBuilder(study_path)
    elif 'milgram' in study_type.lower() or 'obedience' in study_type.lower():
        return MilgramPromptBuilder(study_path)
    else:
        # Generic builder for other studies
        return PromptBuilder(study_path)


# Convenience function for users
def get_prompt_builder(study_id: str, data_dir: str = "data") -> PromptBuilder:
    """
    Get prompt builder for a study by ID.
    
    Args:
        study_id: Study identifier (e.g., "study_001")
        data_dir: Path to data directory
        
    Returns:
        PromptBuilder instance
        
    Example:
        >>> builder = get_prompt_builder("study_001")
        >>> system_prompt = builder.build_system_prompt({"age": 20, "gender": "male"})
        >>> trial_prompt = builder.build_trial_prompt({"trial_number": 1, ...})
    """
    study_path = Path(data_dir) / "studies" / study_id
    return create_prompt_builder(study_path)
