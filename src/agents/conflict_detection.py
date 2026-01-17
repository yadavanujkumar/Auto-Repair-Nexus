"""
Conflict Detection Agent using Reflexion pattern.
Detects semantic collisions where the same relationship has conflicting values.
"""
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from ..utils.neo4j_connection import Neo4jConnection


class SemanticConflict(BaseModel):
    """Represents a detected semantic conflict in the graph."""
    conflict_id: str
    entity_id: str
    entity_name: str
    relationship_type: str
    conflicting_relationships: List[Dict[str, Any]]
    detected_at: datetime
    severity: str  # "high", "medium", "low"
    description: str


class ConflictDetectionAgent:
    """
    Reflexion agent that detects semantic collisions in the knowledge graph.
    Periodically queries for conflicts where the same relationship type has multiple values.
    """
    
    def __init__(self, neo4j_conn: Neo4jConnection):
        """Initialize the conflict detection agent."""
        self.conn = neo4j_conn
        
    def detect_duplicate_relationships(self) -> List[SemanticConflict]:
        """
        Detect entities that have multiple outgoing relationships of the same type.
        Example: Person A is CEO of both Company X and Company Y simultaneously.
        """
        query = """
        MATCH (e:Entity)-[r:RELATED_TO]->(target:Entity)
        WITH e, r.type as rel_type, collect({
            id: r.id,
            target: target.name,
            target_id: target.id,
            timestamp: r.timestamp,
            source_document: r.source_document,
            confidence: r.confidence,
            properties: properties(r)
        }) as relationships
        WHERE size(relationships) > 1
        RETURN e.id as entity_id,
               e.name as entity_name,
               rel_type,
               relationships
        """
        
        results = self.conn.execute_query(query)
        conflicts = []
        
        for result in results:
            # Check if timestamps indicate a conflict (overlapping time periods)
            relationships = result["relationships"]
            
            # Sort by timestamp
            relationships.sort(key=lambda x: x.get("timestamp", ""))
            
            # For simplicity, consider multiple same-type relationships as potential conflicts
            conflict = SemanticConflict(
                conflict_id=f"dup_{result['entity_id']}_{result['rel_type']}",
                entity_id=result["entity_id"],
                entity_name=result["entity_name"],
                relationship_type=result["rel_type"],
                conflicting_relationships=relationships,
                detected_at=datetime.utcnow(),
                severity=self._assess_severity(relationships),
                description=(
                    f"Entity '{result['entity_name']}' has {len(relationships)} "
                    f"relationships of type '{result['rel_type']}'"
                ),
            )
            conflicts.append(conflict)
            
        return conflicts
        
    def detect_contradictory_facts(self) -> List[SemanticConflict]:
        """
        Detect contradictory facts based on confidence scores and timestamps.
        Looks for relationships with low confidence or conflicting temporal information.
        """
        query = """
        MATCH (e:Entity)-[r:RELATED_TO]->(target:Entity)
        WHERE r.confidence < 0.7 OR r.is_current = false
        WITH e, r.type as rel_type, collect({
            id: r.id,
            target: target.name,
            target_id: target.id,
            timestamp: r.timestamp,
            source_document: r.source_document,
            confidence: r.confidence,
            is_current: r.is_current
        }) as relationships
        WHERE size(relationships) > 0
        RETURN e.id as entity_id,
               e.name as entity_name,
               rel_type,
               relationships
        """
        
        results = self.conn.execute_query(query)
        conflicts = []
        
        for result in results:
            relationships = result["relationships"]
            
            conflict = SemanticConflict(
                conflict_id=f"contra_{result['entity_id']}_{result['rel_type']}",
                entity_id=result["entity_id"],
                entity_name=result["entity_name"],
                relationship_type=result["rel_type"],
                conflicting_relationships=relationships,
                detected_at=datetime.utcnow(),
                severity="medium",
                description=(
                    f"Entity '{result['entity_name']}' has low-confidence or "
                    f"outdated relationships of type '{result['rel_type']}'"
                ),
            )
            conflicts.append(conflict)
            
        return conflicts
        
    def detect_all_conflicts(self) -> List[SemanticConflict]:
        """Run all conflict detection methods and return combined results."""
        conflicts = []
        
        # Detect duplicate relationships
        dup_conflicts = self.detect_duplicate_relationships()
        conflicts.extend(dup_conflicts)
        
        # Detect contradictory facts
        contra_conflicts = self.detect_contradictory_facts()
        conflicts.extend(contra_conflicts)
        
        return conflicts
        
    def mark_conflict_in_graph(self, conflict: SemanticConflict):
        """Mark the entity in the graph as having a conflict."""
        query = """
        MATCH (e:Entity {id: $entity_id})
        SET e.has_conflict = true,
            e.conflict_detected_at = $timestamp,
            e.conflict_description = $description
        RETURN e.id
        """
        
        parameters = {
            "entity_id": conflict.entity_id,
            "timestamp": conflict.detected_at.isoformat(),
            "description": conflict.description,
        }
        
        self.conn.execute_write(query, parameters)
        
    def store_conflict_log(self, conflict: SemanticConflict):
        """Store conflict information in a separate conflict log node."""
        query = """
        CREATE (c:ConflictLog {
            id: $conflict_id,
            entity_id: $entity_id,
            entity_name: $entity_name,
            relationship_type: $relationship_type,
            detected_at: $detected_at,
            severity: $severity,
            description: $description,
            conflicting_relationships: $conflicting_relationships,
            resolved: false
        })
        RETURN c.id
        """
        
        parameters = {
            "conflict_id": conflict.conflict_id,
            "entity_id": conflict.entity_id,
            "entity_name": conflict.entity_name,
            "relationship_type": conflict.relationship_type,
            "detected_at": conflict.detected_at.isoformat(),
            "severity": conflict.severity,
            "description": conflict.description,
            "conflicting_relationships": json.dumps(conflict.conflicting_relationships),
        }
        
        self.conn.execute_write(query, parameters)
        
    def run_detection_cycle(self) -> List[SemanticConflict]:
        """
        Run a complete detection cycle:
        1. Detect all conflicts
        2. Mark conflicts in graph
        3. Store conflict logs
        """
        print(f"[{datetime.utcnow().isoformat()}] Starting conflict detection cycle...")
        
        conflicts = self.detect_all_conflicts()
        
        print(f"✓ Detected {len(conflicts)} conflicts")
        
        for conflict in conflicts:
            self.mark_conflict_in_graph(conflict)
            self.store_conflict_log(conflict)
            
        print(f"✓ Marked and logged {len(conflicts)} conflicts")
        
        return conflicts
        
    def _assess_severity(self, relationships: List[Dict[str, Any]]) -> str:
        """Assess the severity of a conflict based on relationship properties."""
        # High severity if multiple recent relationships
        recent_count = sum(
            1 for r in relationships
            if r.get("timestamp", "") and 
            (datetime.utcnow() - datetime.fromisoformat(r["timestamp"])).days < 30
        )
        
        if recent_count > 1:
            return "high"
        elif len(relationships) > 2:
            return "medium"
        else:
            return "low"
