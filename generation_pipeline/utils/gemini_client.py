"""
Gemini Client - Reuses validation_pipeline's GeminiClient
"""

import sys
from pathlib import Path

# Add validation_pipeline to path to reuse its GeminiClient
validation_pipeline_path = Path(__file__).parent.parent.parent / "validation_pipeline"
sys.path.insert(0, str(validation_pipeline_path.parent))

from validation_pipeline.utils.gemini_client import GeminiClient

__all__ = ["GeminiClient"]

