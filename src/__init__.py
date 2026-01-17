"""
Self-Healing Agentic Knowledge Graph System
A high-reliability enterprise data retrieval system using Neo4j and LlamaIndex.
"""

__version__ = "1.0.0"
__author__ = "Auto-Repair-Nexus Team"

# Note: Avoid importing from submodules here to prevent circular imports
# Instead, import directly from the specific module when needed:
#
#   from src.utils.neo4j_connection import Neo4jConnection, get_connection
#   from src.utils.config import load_config
#   from src.ingestion.temporal_ingestion import Entity, Relationship, TemporalGraphIngestion
#   from src.agents.conflict_detection import SemanticConflict, ConflictDetectionAgent
#   from src.agents.self_correction import DeepResearchTask, SelfCorrectionAgent
#   from src.observability.metrics import ObservabilityMetrics, NodeHealth, ObservabilityTracker

__all__ = [
    '__version__',
    '__author__',
]
