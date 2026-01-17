"""
Observability and Metrics Tracking Module
Tracks cost-to-verify, data accuracy, and unstable nodes.
"""
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

from ..utils.neo4j_connection import Neo4jConnection
from ..utils.config import load_config


class ObservabilityMetrics(BaseModel):
    """Container for observability metrics."""
    timestamp: datetime
    total_entities: int
    total_relationships: int
    entities_with_conflicts: int
    resolved_conflicts: int
    unresolved_conflicts: int
    unstable_nodes: int
    total_tokens_used: int
    total_healing_cost: float
    average_confidence: float
    data_accuracy_score: float


class NodeHealth(BaseModel):
    """Health information for a specific node."""
    entity_id: str
    entity_name: str
    change_count: int
    healing_count: int
    last_healed_at: Optional[str]
    is_unstable: bool
    has_conflict: bool
    confidence_score: float


class ObservabilityTracker:
    """
    Tracks metrics for the self-healing knowledge graph.
    Monitors cost-to-verify and data accuracy.
    """
    
    def __init__(self, neo4j_conn: Neo4jConnection):
        """Initialize the observability tracker."""
        self.conn = neo4j_conn
        self.config = load_config()
        
    def calculate_healing_cost(self, tokens_used: int) -> float:
        """Calculate the cost in USD based on tokens used."""
        cost_per_1k = self.config.observability.token_cost_per_1k
        return (tokens_used / 1000.0) * cost_per_1k
        
    def get_current_metrics(self) -> ObservabilityMetrics:
        """Get current system metrics."""
        # Count total entities and relationships
        count_query = """
        MATCH (e:Entity)
        OPTIONAL MATCH (e)-[r:RELATED_TO]->()
        RETURN count(DISTINCT e) as entity_count,
               count(r) as relationship_count,
               sum(CASE WHEN e.has_conflict = true THEN 1 ELSE 0 END) as conflict_count,
               sum(CASE WHEN e.is_unstable = true THEN 1 ELSE 0 END) as unstable_count,
               avg(e.change_count) as avg_change_count
        """
        
        counts = self.conn.execute_query(count_query)[0]
        
        # Count resolved and unresolved conflicts
        conflict_query = """
        MATCH (c:ConflictLog)
        RETURN sum(CASE WHEN c.resolved = true THEN 1 ELSE 0 END) as resolved,
               sum(CASE WHEN c.resolved = false THEN 1 ELSE 0 END) as unresolved
        """
        
        conflict_stats = self.conn.execute_query(conflict_query)
        conflict_data = conflict_stats[0] if conflict_stats else {"resolved": 0, "unresolved": 0}
        
        # Calculate average confidence from relationships
        confidence_query = """
        MATCH ()-[r:RELATED_TO]->()
        WHERE r.is_current = true
        RETURN avg(r.confidence) as avg_confidence
        """
        
        confidence_result = self.conn.execute_query(confidence_query)
        avg_confidence = confidence_result[0].get("avg_confidence", 0.0) if confidence_result else 0.0
        
        # Get token usage from healing events
        token_query = """
        MATCH (e:Entity)
        WHERE e.healing_count > 0
        RETURN sum(e.healing_count) as total_healings
        """
        
        token_result = self.conn.execute_query(token_query)
        # Estimate tokens (rough estimate: 1000 tokens per healing)
        estimated_tokens = (token_result[0].get("total_healings", 0) if token_result else 0) * 1000
        
        # Calculate data accuracy score
        total_entities = counts.get("entity_count", 0)
        entities_with_conflicts = counts.get("conflict_count", 0)
        
        if total_entities > 0:
            data_accuracy_score = 1.0 - (entities_with_conflicts / total_entities)
        else:
            data_accuracy_score = 1.0
            
        return ObservabilityMetrics(
            timestamp=datetime.utcnow(),
            total_entities=total_entities,
            total_relationships=counts.get("relationship_count", 0),
            entities_with_conflicts=entities_with_conflicts,
            resolved_conflicts=conflict_data.get("resolved", 0),
            unresolved_conflicts=conflict_data.get("unresolved", 0),
            unstable_nodes=counts.get("unstable_count", 0),
            total_tokens_used=estimated_tokens,
            total_healing_cost=self.calculate_healing_cost(estimated_tokens),
            average_confidence=avg_confidence or 0.0,
            data_accuracy_score=data_accuracy_score,
        )
        
    def mark_unstable_nodes(self) -> int:
        """
        Mark nodes as unstable if they exceed the change threshold.
        Returns the count of nodes marked as unstable.
        """
        threshold = self.config.observability.unstable_node_threshold
        
        query = """
        MATCH (e:Entity)
        WHERE e.change_count >= $threshold
        SET e.is_unstable = true,
            e.marked_unstable_at = $timestamp
        RETURN count(e) as unstable_count
        """
        
        result = self.conn.execute_write(query, {
            "threshold": threshold,
            "timestamp": datetime.utcnow().isoformat(),
        })
        
        count = result[0].get("unstable_count", 0) if result else 0
        return count
        
    def get_unstable_nodes(self, limit: int = 50) -> List[NodeHealth]:
        """Get a list of unstable nodes with their health information."""
        query = """
        MATCH (e:Entity)
        WHERE e.is_unstable = true
        OPTIONAL MATCH (e)-[r:RELATED_TO]->()
        WHERE r.is_current = true
        WITH e, avg(r.confidence) as avg_confidence
        RETURN e.id as entity_id,
               e.name as entity_name,
               e.change_count as change_count,
               COALESCE(e.healing_count, 0) as healing_count,
               e.last_healed_at as last_healed_at,
               e.is_unstable as is_unstable,
               COALESCE(e.has_conflict, false) as has_conflict,
               COALESCE(avg_confidence, 0.0) as confidence_score
        ORDER BY e.change_count DESC
        LIMIT $limit
        """
        
        results = self.conn.execute_query(query, {"limit": limit})
        
        nodes = []
        for result in results:
            node = NodeHealth(
                entity_id=result["entity_id"],
                entity_name=result["entity_name"],
                change_count=result["change_count"],
                healing_count=result["healing_count"],
                last_healed_at=result.get("last_healed_at"),
                is_unstable=result["is_unstable"],
                has_conflict=result["has_conflict"],
                confidence_score=result["confidence_score"],
            )
            nodes.append(node)
            
        return nodes
        
    def get_high_risk_nodes(self, limit: int = 20) -> List[NodeHealth]:
        """
        Get nodes that are high-risk (have conflicts and are unstable).
        """
        query = """
        MATCH (e:Entity)
        WHERE e.is_unstable = true AND e.has_conflict = true
        OPTIONAL MATCH (e)-[r:RELATED_TO]->()
        WHERE r.is_current = true
        WITH e, avg(r.confidence) as avg_confidence
        RETURN e.id as entity_id,
               e.name as entity_name,
               e.change_count as change_count,
               COALESCE(e.healing_count, 0) as healing_count,
               e.last_healed_at as last_healed_at,
               e.is_unstable as is_unstable,
               e.has_conflict as has_conflict,
               COALESCE(avg_confidence, 0.0) as confidence_score
        ORDER BY e.change_count DESC, avg_confidence ASC
        LIMIT $limit
        """
        
        results = self.conn.execute_query(query, {"limit": limit})
        
        nodes = []
        for result in results:
            node = NodeHealth(
                entity_id=result["entity_id"],
                entity_name=result["entity_name"],
                change_count=result["change_count"],
                healing_count=result["healing_count"],
                last_healed_at=result.get("last_healed_at"),
                is_unstable=result["is_unstable"],
                has_conflict=result["has_conflict"],
                confidence_score=result["confidence_score"],
            )
            nodes.append(node)
            
        return nodes
        
    def store_metrics_snapshot(self, metrics: ObservabilityMetrics):
        """Store a snapshot of metrics in the database."""
        query = """
        CREATE (m:MetricsSnapshot {
            timestamp: $timestamp,
            total_entities: $total_entities,
            total_relationships: $total_relationships,
            entities_with_conflicts: $entities_with_conflicts,
            resolved_conflicts: $resolved_conflicts,
            unresolved_conflicts: $unresolved_conflicts,
            unstable_nodes: $unstable_nodes,
            total_tokens_used: $total_tokens_used,
            total_healing_cost: $total_healing_cost,
            average_confidence: $average_confidence,
            data_accuracy_score: $data_accuracy_score
        })
        RETURN m.timestamp
        """
        
        self.conn.execute_write(query, {
            "timestamp": metrics.timestamp.isoformat(),
            "total_entities": metrics.total_entities,
            "total_relationships": metrics.total_relationships,
            "entities_with_conflicts": metrics.entities_with_conflicts,
            "resolved_conflicts": metrics.resolved_conflicts,
            "unresolved_conflicts": metrics.unresolved_conflicts,
            "unstable_nodes": metrics.unstable_nodes,
            "total_tokens_used": metrics.total_tokens_used,
            "total_healing_cost": metrics.total_healing_cost,
            "average_confidence": metrics.average_confidence,
            "data_accuracy_score": metrics.data_accuracy_score,
        })
        
    def get_metrics_history(self, days: int = 7) -> List[ObservabilityMetrics]:
        """Get historical metrics for the specified number of days."""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = """
        MATCH (m:MetricsSnapshot)
        WHERE m.timestamp >= $cutoff_date
        RETURN m
        ORDER BY m.timestamp DESC
        """
        
        results = self.conn.execute_query(query, {
            "cutoff_date": cutoff_date.isoformat()
        })
        
        metrics_list = []
        for result in results:
            m = result.get("m", {})
            metrics = ObservabilityMetrics(
                timestamp=datetime.fromisoformat(m.get("timestamp")),
                total_entities=m.get("total_entities", 0),
                total_relationships=m.get("total_relationships", 0),
                entities_with_conflicts=m.get("entities_with_conflicts", 0),
                resolved_conflicts=m.get("resolved_conflicts", 0),
                unresolved_conflicts=m.get("unresolved_conflicts", 0),
                unstable_nodes=m.get("unstable_nodes", 0),
                total_tokens_used=m.get("total_tokens_used", 0),
                total_healing_cost=m.get("total_healing_cost", 0.0),
                average_confidence=m.get("average_confidence", 0.0),
                data_accuracy_score=m.get("data_accuracy_score", 0.0),
            )
            metrics_list.append(metrics)
            
        return metrics_list
