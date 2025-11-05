"""
Study-specific configurations.

This module imports all study configurations to ensure they are registered.
"""

from src.studies.study_003_config import Study003Config
from src.studies.study_004_config import Study004Config

__all__ = [
    'Study003Config',
    'Study004Config',
]
