"""
Google Gemini API Client for Validation Pipeline
"""

import os
from typing import Optional, Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv

try:
    import google.generativeai as genai
except ImportError:
    try:
        from google import genai
    except ImportError:
        raise ImportError(
            "Google Gemini SDK not installed. Install with: pip install google-generativeai"
        )

# Load environment variables
load_dotenv()


class GeminiClient:
    """Client for interacting with Google Gemini API"""
    
    def __init__(self, model: str = "models/gemini-3-flash-preview", api_key: Optional[str] = None):
        """
        Initialize Gemini client.
        
        Args:
            model: Model name (e.g., "models/gemini-3-flash-preview")
            api_key: API key (if None, reads from GOOGLE_API_KEY env var)
        """
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError(
                "GOOGLE_API_KEY not found in environment variables. "
                "Please set it in .env file or as environment variable."
            )
        
        # Configure the API
        genai.configure(api_key=api_key)
        self.api_key = api_key
        self.model = model
    
    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate content using Gemini API.
        
        Args:
            prompt: User prompt
            system_instruction: Optional system instruction
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        try:
            # Create generation config
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
            )
            if max_tokens:
                generation_config.max_output_tokens = max_tokens
            
            # Create model instance
            model = genai.GenerativeModel(
                model_name=self.model,
                system_instruction=system_instruction,
            )
            
            # Generate content
            response = model.generate_content(
                prompt,
                generation_config=generation_config,
            )
            return response.text
        except AttributeError:
            # Fallback for different API versions
            try:
                model = genai.GenerativeModel(
                    model_name=self.model,
                )
                response = model.generate_content(
                    prompt,
                    generation_config={
                        "temperature": temperature,
                        "max_output_tokens": max_tokens,
                    } if max_tokens else {"temperature": temperature},
                )
                return response.text
            except Exception as e:
                raise RuntimeError(f"Error generating content with Gemini API: {e}")
        except Exception as e:
            raise RuntimeError(f"Error generating content with Gemini API: {e}")
    
    def generate_structured(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        response_format: str = "json",
        temperature: float = 0.3,
    ) -> Dict[str, Any]:
        """
        Generate structured response (JSON).
        
        Args:
            prompt: User prompt
            system_instruction: Optional system instruction
            response_format: Response format (default: "json")
            temperature: Sampling temperature (lower for more deterministic)
            
        Returns:
            Parsed JSON response as dictionary
        """
        import json
        
        format_instruction = ""
        if response_format == "json":
            format_instruction = "\n\nPlease respond in valid JSON format only, without markdown code blocks."
        
        full_prompt = f"{prompt}{format_instruction}"
        
        response_text = self.generate_content(
            prompt=full_prompt,
            system_instruction=system_instruction,
            temperature=temperature,
        )
        
        # Try to extract JSON from response
        response_text = response_text.strip()
        
        # Remove markdown code blocks if present
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        
        response_text = response_text.strip()
        
        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(
                f"Failed to parse JSON response: {e}\n"
                f"Response text: {response_text[:500]}"
            )

