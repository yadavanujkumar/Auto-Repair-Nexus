"""
Ingestion module for the self-healing knowledge graph.
"""

from .temporal_ingestion import (
    Entity,
    Relationship,
    TemporalGraphIngestion,
)

__all__ = [
    'Entity',
    'Relationship',
    'TemporalGraphIngestion',
]
