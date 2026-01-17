"""
Self-Healing Agentic Knowledge Graph System
A high-reliability enterprise data retrieval system using Neo4j and LlamaIndex.
"""

__version__ = "1.0.0"
__author__ = "Auto-Repair-Nexus Team"

from src.utils import Neo4jConnection, get_connection, load_config
from src.ingestion import Entity, Relationship, TemporalGraphIngestion
from src.agents import (
    SemanticConflict,
    ConflictDetectionAgent,
    DeepResearchTask,
    SelfCorrectionAgent,
)
from src.observability import (
    ObservabilityMetrics,
    NodeHealth,
    ObservabilityTracker,
)

__all__ = [
    # Utils
    'Neo4jConnection',
    'get_connection',
    'load_config',
    # Ingestion
    'Entity',
    'Relationship',
    'TemporalGraphIngestion',
    # Agents
    'SemanticConflict',
    'ConflictDetectionAgent',
    'DeepResearchTask',
    'SelfCorrectionAgent',
    # Observability
    'ObservabilityMetrics',
    'NodeHealth',
    'ObservabilityTracker',
]
