"""
Basic tests for the Self-Healing Knowledge Graph system.
Note: These are demonstration tests. Full test coverage would require a test Neo4j instance.
"""
import unittest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.ingestion.temporal_ingestion import Entity, Relationship, TemporalGraphIngestion
from src.agents.conflict_detection import SemanticConflict, ConflictDetectionAgent
from src.observability.metrics import ObservabilityMetrics, NodeHealth


class TestEntity(unittest.TestCase):
    """Test Entity model."""
    
    def test_entity_creation(self):
        """Test creating an entity."""
        entity = Entity(
            name="Test Entity",
            type="Person",
            properties={"age": 30}
        )
        
        self.assertEqual(entity.name, "Test Entity")
        self.assertEqual(entity.type, "Person")
        self.assertEqual(entity.properties["age"], 30)
        self.assertIsInstance(entity.timestamp, datetime)
        self.assertIsNotNone(entity.id)
    
    def test_entity_with_source(self):
        """Test entity with source document."""
        entity = Entity(
            name="John Doe",
            type="Person",
            source_document="records.pdf"
        )
        
        self.assertEqual(entity.source_document, "records.pdf")


class TestRelationship(unittest.TestCase):
    """Test Relationship model."""
    
    def test_relationship_creation(self):
        """Test creating a relationship."""
        rel = Relationship(
            source_entity_id="entity1",
            target_entity_id="entity2",
            type="WORKS_AT",
            properties={"since": "2024"}
        )
        
        self.assertEqual(rel.source_entity_id, "entity1")
        self.assertEqual(rel.target_entity_id, "entity2")
        self.assertEqual(rel.type, "WORKS_AT")
        self.assertEqual(rel.confidence, 1.0)
        self.assertIsNotNone(rel.id)


class TestSemanticConflict(unittest.TestCase):
    """Test SemanticConflict model."""
    
    def test_conflict_creation(self):
        """Test creating a semantic conflict."""
        conflict = SemanticConflict(
            conflict_id="test_conflict",
            entity_id="entity1",
            entity_name="Test Entity",
            relationship_type="CEO_OF",
            conflicting_relationships=[
                {"id": "rel1", "target": "CompanyA"},
                {"id": "rel2", "target": "CompanyB"}
            ],
            detected_at=datetime.utcnow(),
            severity="high",
            description="Test conflict"
        )
        
        self.assertEqual(conflict.entity_name, "Test Entity")
        self.assertEqual(conflict.severity, "high")
        self.assertEqual(len(conflict.conflicting_relationships), 2)


class TestObservabilityMetrics(unittest.TestCase):
    """Test ObservabilityMetrics model."""
    
    def test_metrics_creation(self):
        """Test creating observability metrics."""
        metrics = ObservabilityMetrics(
            timestamp=datetime.utcnow(),
            total_entities=100,
            total_relationships=200,
            entities_with_conflicts=5,
            resolved_conflicts=3,
            unresolved_conflicts=2,
            unstable_nodes=8,
            total_tokens_used=10000,
            total_healing_cost=0.30,
            average_confidence=0.95,
            data_accuracy_score=0.95
        )
        
        self.assertEqual(metrics.total_entities, 100)
        self.assertEqual(metrics.data_accuracy_score, 0.95)
        self.assertEqual(metrics.total_healing_cost, 0.30)
        self.assertAlmostEqual(metrics.average_confidence, 0.95)


class TestNodeHealth(unittest.TestCase):
    """Test NodeHealth model."""
    
    def test_node_health_creation(self):
        """Test creating node health information."""
        node = NodeHealth(
            entity_id="entity1",
            entity_name="Test Node",
            change_count=5,
            healing_count=2,
            last_healed_at="2024-01-01T00:00:00",
            is_unstable=True,
            has_conflict=False,
            confidence_score=0.85
        )
        
        self.assertEqual(node.entity_name, "Test Node")
        self.assertEqual(node.change_count, 5)
        self.assertTrue(node.is_unstable)
        self.assertFalse(node.has_conflict)


class TestTemporalGraphIngestionUnit(unittest.TestCase):
    """Unit tests for TemporalGraphIngestion (mocked)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_conn = Mock()
        self.ingestion = TemporalGraphIngestion(self.mock_conn)
    
    def test_ingest_entity_mock(self):
        """Test ingesting an entity with mocked connection."""
        self.mock_conn.execute_write.return_value = [{"entity_id": "test_id"}]
        
        entity = Entity(name="Test", type="Person")
        entity_id = self.ingestion.ingest_entity(entity)
        
        self.assertEqual(entity_id, "test_id")
        self.mock_conn.execute_write.assert_called_once()
    
    def test_ingest_fact_mock(self):
        """Test ingesting a fact with mocked connection."""
        self.mock_conn.execute_write.return_value = [{"entity_id": "id1"}]
        
        result = self.ingestion.ingest_fact(
            subject="John",
            predicate="WORKS_AT",
            object="CompanyX"
        )
        
        self.assertIn("subject_id", result)
        self.assertIn("object_id", result)
        self.assertIn("relationship_id", result)


class TestConflictDetectionUnit(unittest.TestCase):
    """Unit tests for ConflictDetectionAgent (mocked)."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.mock_conn = Mock()
        self.agent = ConflictDetectionAgent(self.mock_conn)
    
    def test_detect_duplicate_relationships_mock(self):
        """Test detecting duplicate relationships with mock data."""
        mock_results = [
            {
                "entity_id": "entity1",
                "entity_name": "John Doe",
                "rel_type": "CEO_OF",
                "relationships": [
                    {"id": "rel1", "target": "CompanyA", "timestamp": "2024-01-01"},
                    {"id": "rel2", "target": "CompanyB", "timestamp": "2024-02-01"}
                ]
            }
        ]
        
        self.mock_conn.execute_query.return_value = mock_results
        
        conflicts = self.agent.detect_duplicate_relationships()
        
        self.assertEqual(len(conflicts), 1)
        self.assertEqual(conflicts[0].entity_name, "John Doe")
        self.assertEqual(conflicts[0].relationship_type, "CEO_OF")


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == "__main__":
    print("\n" + "="*70)
    print("Running Self-Healing Knowledge Graph Tests")
    print("="*70 + "\n")
    
    run_tests()
    
    print("\n" + "="*70)
    print("Test Suite Complete")
    print("="*70)
    print("\nNote: These are unit tests with mocked dependencies.")
    print("Integration tests require a running Neo4j instance.")
    print("Run 'python examples.py' for integration examples.\n")
