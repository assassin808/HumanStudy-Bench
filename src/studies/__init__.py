"""
Study-specific configurations.

This module imports all study configurations to ensure they are registered.
"""

from src.studies.study_001_config import Study001Config
from src.studies.study_002_config import Study002Config
from src.studies.study_003_config import Study003Config
from src.studies.study_004_config import Study004Config
from src.studies.study_005_config import Study005Config
from src.studies.study_006_config import Study006Config

__all__ = [
    'Study001Config',
    'Study002Config',
    'Study003Config',
    'Study004Config',
    'Study005Config',
    'Study006Config',
]
