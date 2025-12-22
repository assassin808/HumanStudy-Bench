"""
Google Gemini API Client for Validation Pipeline
"""

import os
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
from dotenv import load_dotenv

# Try new API first, fallback to old API
try:
    import google.genai as genai
    USE_NEW_API = True
except ImportError:
    try:
        # Fallback to old API for backward compatibility
        import google.generativeai as genai
        USE_NEW_API = False
    except ImportError:
        raise ImportError(
            "Google Gemini SDK not installed. Install with: pip install google-genai"
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
        
        self.api_key = api_key
        self.model = model
        self._uploaded_files: Dict[str, Any] = {}  # Cache for uploaded files
        
        # Initialize based on API version
        if USE_NEW_API:
            # New API: use Client
            try:
                self.client = genai.Client(api_key=api_key)
            except Exception as e:
                raise RuntimeError(f"Failed to initialize Gemini Client: {e}")
        else:
            # Old API: use configure
            try:
                genai.configure(api_key=api_key)
                self.client = None  # Old API doesn't use client
            except Exception as e:
                raise RuntimeError(f"Failed to configure Gemini API: {e}")
    
    def upload_file(self, file_path: Path) -> Any:
        """
        Upload a file (PDF, image, etc.) to Gemini API.
        
        Args:
            file_path: Path to file to upload
            
        Returns:
            Uploaded file object
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Check cache
        cache_key = str(file_path.absolute())
        if cache_key in self._uploaded_files:
            return self._uploaded_files[cache_key]
        
        # Upload file
        try:
            if USE_NEW_API:
                # New API: use client.files.upload(file=...)
                uploaded_file = self.client.files.upload(file=str(file_path))
            else:
                # Old API: use genai.upload_file()
                uploaded_file = genai.upload_file(path=str(file_path))
            
            self._uploaded_files[cache_key] = uploaded_file
            return uploaded_file
        except Exception as e:
            raise RuntimeError(f"Error uploading file {file_path}: {e}")
    
    def generate_content(
        self,
        prompt: Union[str, List[Union[str, Any]]],
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Generate content using Gemini API.
        
        Args:
            prompt: User prompt (str) or list of content parts (can include uploaded files)
            system_instruction: Optional system instruction
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated text response
        """
        try:
            if USE_NEW_API:
                # New API: use client.models.generate_content()
                # Build generation config
                config_dict = {}
                if temperature is not None:
                    config_dict['temperature'] = temperature
                if max_tokens is not None:
                    config_dict['max_output_tokens'] = max_tokens
                if system_instruction is not None:
                    config_dict['system_instruction'] = system_instruction
                
                config = genai.types.GenerateContentConfig(**config_dict) if config_dict else None
                
                # Prepare content
                contents = prompt
                
                # Generate content
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=contents,
                    config=config,
                )
                return response.text
            else:
                # Old API: use GenerativeModel
                generation_config = genai.types.GenerationConfig(
                    temperature=temperature,
                )
                if max_tokens:
                    generation_config.max_output_tokens = max_tokens
                
                model = genai.GenerativeModel(
                    model_name=self.model,
                    system_instruction=system_instruction,
                )
                
                response = model.generate_content(
                    prompt,
                    generation_config=generation_config,
                )
                return response.text
        except Exception as e:
            raise RuntimeError(f"Error generating content with Gemini API: {e}")
    
    def generate_structured(
        self,
        prompt: Union[str, List[Union[str, Any]]],
        system_instruction: Optional[str] = None,
        response_format: str = "json",
        temperature: float = 0.3,
    ) -> Dict[str, Any]:
        """
        Generate structured response (JSON).
        
        Args:
            prompt: User prompt (str) or list of content parts (can include uploaded files)
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
        
        # Handle both string and list prompts
        if isinstance(prompt, str):
            full_prompt = f"{prompt}{format_instruction}"
        else:
            # For list prompts, append format instruction as text
            full_prompt = prompt + [format_instruction]
        
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
