"""
Base Agent Class for Validation Pipeline
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path

from validation_pipeline.utils.gemini_client import GeminiClient


class BaseValidationAgent(ABC):
    """Base class for all validation agents"""
    
    def __init__(self, gemini_client: Optional[GeminiClient] = None, model: str = "models/gemini-3-flash-preview"):
        """
        Initialize agent.
        
        Args:   
            gemini_client: Optional pre-initialized Gemini client
            model: Model name to use
        """
        self.client = gemini_client or GeminiClient(model=model)
        self.model = model
    
    @abstractmethod
    def validate(self, documents: Dict[str, Any]) -> Dict[str, Any]:
        """
        Perform validation task.
        
        Args:
            documents: Dictionary containing loaded documents (PDFs, JSON, etc.)
            
        Returns:
            Validation results dictionary
        """
        pass
    
    def _generate_response(self, prompt: str, system_instruction: Optional[str] = None, structured: bool = False) -> Any:
        """
        Generate response using Gemini API.
        
        Args:
            prompt: User prompt
            system_instruction: Optional system instruction
            structured: Whether to return structured JSON response
            
        Returns:
            Response text or parsed JSON
        """
        if structured:
            return self.client.generate_structured(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.3,
            )
        else:
            return self.client.generate_content(
                prompt=prompt,
                system_instruction=system_instruction,
                temperature=0.7,
            )

