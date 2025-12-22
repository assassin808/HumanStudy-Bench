"""
Document Loader - Reuses validation_pipeline's DocumentLoader
"""

import sys
from pathlib import Path

# Add validation_pipeline to path to reuse its DocumentLoader
validation_pipeline_path = Path(__file__).parent.parent.parent / "validation_pipeline"
sys.path.insert(0, str(validation_pipeline_path.parent))

from validation_pipeline.utils.document_loader import DocumentLoader

__all__ = ["DocumentLoader"]

