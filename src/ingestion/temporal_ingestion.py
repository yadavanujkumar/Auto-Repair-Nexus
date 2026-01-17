"""
Temporal Graph Ingestion Pipeline
Stores entities with timestamps and tracks source documents.
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

from ..utils.neo4j_connection import Neo4jConnection


class Entity(BaseModel):
    """Represents an entity in the knowledge graph."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_document: Optional[str] = None


class Relationship(BaseModel):
    """Represents a relationship between entities."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_entity_id: str
    target_entity_id: str
    type: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_document: Optional[str] = None
    confidence: float = 1.0


class TemporalGraphIngestion:
    """Handles ingestion of entities and relationships into Neo4j with temporal tracking."""
    
    def __init__(self, neo4j_conn: Neo4jConnection):
        """Initialize the ingestion pipeline."""
        self.conn = neo4j_conn
        
    def ingest_entity(self, entity: Entity) -> str:
        """
        Ingest an entity into the knowledge graph.
        Returns the entity ID.
        """
        query = """
        MERGE (e:Entity {id: $id})
        SET e.name = $name,
            e.type = $type,
            e.last_updated = $timestamp,
            e.source_document = $source_document,
            e.has_conflict = COALESCE(e.has_conflict, false),
            e.is_unstable = COALESCE(e.is_unstable, false),
            e.change_count = COALESCE(e.change_count, 0) + 1
        SET e += $properties
        RETURN e.id as entity_id
        """
        
        parameters = {
            "id": entity.id,
            "name": entity.name,
            "type": entity.type,
            "timestamp": entity.timestamp.isoformat(),
            "source_document": entity.source_document,
            "properties": entity.properties,
        }
        
        result = self.conn.execute_write(query, parameters)
        return result[0]["entity_id"] if result else entity.id
        
    def ingest_relationship(self, relationship: Relationship) -> str:
        """
        Ingest a relationship between entities with temporal tracking.
        Returns the relationship ID.
        """
        # First, verify both entities exist
        query_check = """
        MATCH (source:Entity {id: $source_id})
        MATCH (target:Entity {id: $target_id})
        RETURN source.id, target.id
        """
        
        check_params = {
            "source_id": relationship.source_entity_id,
            "target_id": relationship.target_entity_id,
        }
        
        exists = self.conn.execute_query(query_check, check_params)
        if not exists:
            raise ValueError(
                f"One or both entities do not exist: "
                f"{relationship.source_entity_id}, {relationship.target_entity_id}"
            )
        
        # Create the relationship with temporal properties
        query = """
        MATCH (source:Entity {id: $source_id})
        MATCH (target:Entity {id: $target_id})
        CREATE (source)-[r:RELATED_TO {
            id: $rel_id,
            type: $rel_type,
            timestamp: $timestamp,
            source_document: $source_document,
            confidence: $confidence,
            is_current: true
        }]->(target)
        SET r += $properties
        RETURN r.id as relationship_id
        """
        
        parameters = {
            "source_id": relationship.source_entity_id,
            "target_id": relationship.target_entity_id,
            "rel_id": relationship.id,
            "rel_type": relationship.type,
            "timestamp": relationship.timestamp.isoformat(),
            "source_document": relationship.source_document,
            "confidence": relationship.confidence,
            "properties": relationship.properties,
        }
        
        result = self.conn.execute_write(query, parameters)
        return result[0]["relationship_id"] if result else relationship.id
        
    def ingest_fact(
        self,
        subject: str,
        predicate: str,
        object: str,
        timestamp: Optional[datetime] = None,
        source_document: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """
        Convenience method to ingest a fact as a triple (subject, predicate, object).
        Example: ingest_fact("Amit", "CEO_OF", "CompanyX", metadata={"since": "2024"})
        
        Returns dict with entity IDs and relationship ID.
        """
        timestamp = timestamp or datetime.utcnow()
        metadata = metadata or {}
        
        # Create subject entity
        subject_entity = Entity(
            name=subject,
            type="Person" if predicate.endswith("_OF") else "Entity",
            timestamp=timestamp,
            source_document=source_document,
        )
        subject_id = self.ingest_entity(subject_entity)
        
        # Create object entity
        object_entity = Entity(
            name=object,
            type="Organization" if predicate.startswith("CEO_") else "Entity",
            timestamp=timestamp,
            source_document=source_document,
        )
        object_id = self.ingest_entity(object_entity)
        
        # Create relationship
        relationship = Relationship(
            source_entity_id=subject_id,
            target_entity_id=object_id,
            type=predicate,
            properties=metadata,
            timestamp=timestamp,
            source_document=source_document,
        )
        rel_id = self.ingest_relationship(relationship)
        
        return {
            "subject_id": subject_id,
            "object_id": object_id,
            "relationship_id": rel_id,
        }
        
    def batch_ingest_facts(
        self,
        facts: List[Dict[str, Any]],
    ) -> List[Dict[str, str]]:
        """
        Batch ingest multiple facts.
        Each fact should be a dict with keys: subject, predicate, object, 
        and optional: timestamp, source_document, metadata
        """
        results = []
        for fact in facts:
            try:
                result = self.ingest_fact(
                    subject=fact["subject"],
                    predicate=fact["predicate"],
                    object=fact["object"],
                    timestamp=fact.get("timestamp"),
                    source_document=fact.get("source_document"),
                    metadata=fact.get("metadata"),
                )
                results.append(result)
            except Exception as e:
                print(f"Error ingesting fact {fact}: {e}")
                results.append({"error": str(e)})
        
        return results
