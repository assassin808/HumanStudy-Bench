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
            study_path: Path to study directory (e.g., data/studies/study_003/)
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
                       May include 'participant_profile' for frame-specific prompts
            
        Returns:
            Complete trial prompt string
        """
        # Check if this is a framing study (Study 003)
        participant_profile = trial_data.get('participant_profile', {})
        framing_condition = participant_profile.get('framing_condition')
        
        if framing_condition:
            # Load frame-specific material
            frame_file = self.materials_path / f"{framing_condition}.txt"
            if frame_file.exists():
                with open(frame_file, 'r') as f:
                    frame_text = f.read().strip()
                # Add frame text to trial data for template
                trial_data = {**trial_data, 'scenario': frame_text, 'frame': framing_condition}
        
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


def create_prompt_builder(study_path: Path) -> PromptBuilder:
    """
    Factory function to create PromptBuilder for a study.
    
    Args:
        study_path: Path to study directory
        
    Returns:
        PromptBuilder instance
    """
    return PromptBuilder(study_path)

# Convenience function for users
def get_prompt_builder(study_id: str, data_dir: str = "data") -> PromptBuilder:
    """
    Get prompt builder for a study by ID.
    
    Args:
        study_id: Study identifier (e.g., "study_003")
        data_dir: Path to data directory
        
    Returns:
        PromptBuilder instance
        
    Example:
        >>> builder = get_prompt_builder("study_003")
        >>> system_prompt = builder.build_system_prompt({"age": 20, "education": "university_student"})
        >>> trial_prompt = builder.build_trial_prompt({"trial_number": 1, ...})
    """
    study_path = Path(data_dir) / "studies" / study_id
    return create_prompt_builder(study_path)
