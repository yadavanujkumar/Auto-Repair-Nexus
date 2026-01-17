"""
Agents module for the self-healing knowledge graph.
"""

from .conflict_detection import (
    SemanticConflict,
    ConflictDetectionAgent,
)
from .self_correction import (
    DeepResearchTask,
    SelfCorrectionAgent,
)

__all__ = [
    'SemanticConflict',
    'ConflictDetectionAgent',
    'DeepResearchTask',
    'SelfCorrectionAgent',
]
