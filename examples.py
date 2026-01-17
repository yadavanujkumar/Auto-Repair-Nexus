"""
Example script demonstrating the Self-Healing Knowledge Graph system.
This script shows how to use all major components.
"""
from datetime import datetime
from src.utils import get_connection
from src.ingestion import TemporalGraphIngestion, Entity, Relationship
from src.agents import ConflictDetectionAgent, SelfCorrectionAgent
from src.observability import ObservabilityTracker


def example_basic_ingestion():
    """Example: Basic entity and relationship ingestion."""
    print("\n" + "="*60)
    print("Example 1: Basic Ingestion")
    print("="*60)
    
    conn = get_connection()
    ingestion = TemporalGraphIngestion(conn)
    
    # Create entities
    amit = Entity(
        name="Amit Kumar",
        type="Person",
        properties={"title": "CEO", "age": 45}
    )
    company = Entity(
        name="TechCorp",
        type="Organization",
        properties={"industry": "Technology", "founded": 2020}
    )
    
    amit_id = ingestion.ingest_entity(amit)
    company_id = ingestion.ingest_entity(company)
    
    # Create relationship
    rel = Relationship(
        source_entity_id=amit_id,
        target_entity_id=company_id,
        type="CEO_OF",
        properties={"since": "2024"},
        source_document="company_records.pdf"
    )
    
    rel_id = ingestion.ingest_relationship(rel)
    
    print(f"✓ Created entity: {amit.name} (ID: {amit_id})")
    print(f"✓ Created entity: {company.name} (ID: {company_id})")
    print(f"✓ Created relationship: {rel.type} (ID: {rel_id})")
    
    conn.close()


def example_batch_ingestion():
    """Example: Batch ingestion of facts."""
    print("\n" + "="*60)
    print("Example 2: Batch Ingestion")
    print("="*60)
    
    conn = get_connection()
    ingestion = TemporalGraphIngestion(conn)
    
    facts = [
        {
            "subject": "Alice Smith",
            "predicate": "WORKS_AT",
            "object": "DataCorp",
            "metadata": {"department": "Engineering", "role": "Senior Engineer"},
            "source_document": "hr_records.pdf"
        },
        {
            "subject": "Bob Johnson",
            "predicate": "MANAGES",
            "object": "Alice Smith",
            "metadata": {"since": "2023"},
            "source_document": "org_chart.pdf"
        },
        {
            "subject": "DataCorp",
            "predicate": "HEADQUARTERED_IN",
            "object": "New York",
            "metadata": {"address": "123 Main St"},
            "source_document": "company_info.pdf"
        },
    ]
    
    results = ingestion.batch_ingest_facts(facts)
    print(f"✓ Ingested {len(results)} facts successfully")
    
    conn.close()


def example_conflict_detection():
    """Example: Detecting conflicts in the graph."""
    print("\n" + "="*60)
    print("Example 3: Conflict Detection")
    print("="*60)
    
    conn = get_connection()
    
    # First, create some conflicting data
    ingestion = TemporalGraphIngestion(conn)
    
    # Same person as CEO of two different companies
    ingestion.ingest_fact(
        "John Doe", "CEO_OF", "CompanyA",
        metadata={"since": "2022"},
        source_document="announcement_2022.pdf"
    )
    
    ingestion.ingest_fact(
        "John Doe", "CEO_OF", "CompanyB",
        metadata={"since": "2024"},
        source_document="press_release_2024.pdf"
    )
    
    print("✓ Created conflicting facts")
    
    # Now detect conflicts
    detector = ConflictDetectionAgent(conn)
    conflicts = detector.detect_all_conflicts()
    
    print(f"\n✓ Detected {len(conflicts)} conflicts")
    
    for conflict in conflicts:
        print(f"\nConflict: {conflict.description}")
        print(f"  Entity: {conflict.entity_name}")
        print(f"  Type: {conflict.relationship_type}")
        print(f"  Severity: {conflict.severity}")
        print(f"  Conflicting relationships: {len(conflict.conflicting_relationships)}")
    
    conn.close()


def example_observability():
    """Example: Tracking system metrics and observability."""
    print("\n" + "="*60)
    print("Example 4: Observability & Metrics")
    print("="*60)
    
    conn = get_connection()
    tracker = ObservabilityTracker(conn)
    
    # Get current metrics
    metrics = tracker.get_current_metrics()
    
    print("\nCurrent System Metrics:")
    print(f"  Total Entities: {metrics.total_entities}")
    print(f"  Total Relationships: {metrics.total_relationships}")
    print(f"  Entities with Conflicts: {metrics.entities_with_conflicts}")
    print(f"  Data Accuracy Score: {metrics.data_accuracy_score:.2%}")
    print(f"  Average Confidence: {metrics.average_confidence:.2%}")
    print(f"  Unstable Nodes: {metrics.unstable_nodes}")
    print(f"  Total Healing Cost: ${metrics.total_healing_cost:.4f}")
    
    # Mark unstable nodes
    unstable_count = tracker.mark_unstable_nodes()
    print(f"\n✓ Marked {unstable_count} nodes as unstable")
    
    # Get high-risk nodes
    high_risk = tracker.get_high_risk_nodes(limit=5)
    
    if high_risk:
        print("\nHigh-Risk Nodes:")
        for node in high_risk:
            print(f"  • {node.entity_name}")
            print(f"    - Change Count: {node.change_count}")
            print(f"    - Confidence: {node.confidence_score:.2%}")
    else:
        print("\n✓ No high-risk nodes found")
    
    # Store metrics snapshot
    tracker.store_metrics_snapshot(metrics)
    print("\n✓ Metrics snapshot stored")
    
    conn.close()


def example_self_healing():
    """Example: Self-healing process (requires OpenAI API key)."""
    print("\n" + "="*60)
    print("Example 5: Self-Healing (Demo - requires API key)")
    print("="*60)
    
    print("\nNote: This example demonstrates the self-healing flow.")
    print("In production, it would use GPT-4 to resolve conflicts.")
    
    conn = get_connection()
    
    # Detect conflicts first
    detector = ConflictDetectionAgent(conn)
    conflicts = detector.detect_all_conflicts()
    
    if conflicts:
        print(f"\n✓ Found {len(conflicts)} conflicts to heal")
        
        # In a real scenario with OpenAI API key:
        # healer = SelfCorrectionAgent(conn)
        # summary = healer.heal_all_conflicts(conflicts)
        # print(f"✓ Healed {summary['successful_corrections']} conflicts")
        
        print("\nTo enable self-healing:")
        print("1. Set OPENAI_API_KEY in your .env file")
        print("2. Run: python main.py --mode heal")
    else:
        print("\n✓ No conflicts found - system is healthy!")
    
    conn.close()


def example_temporal_queries():
    """Example: Querying temporal data from the graph."""
    print("\n" + "="*60)
    print("Example 6: Temporal Queries")
    print("="*60)
    
    conn = get_connection()
    
    # Query current relationships
    query = """
    MATCH (e:Entity)-[r:RELATED_TO]->(t:Entity)
    WHERE r.is_current = true
    RETURN e.name as source, r.type as relationship, t.name as target,
           r.timestamp as since
    ORDER BY r.timestamp DESC
    LIMIT 10
    """
    
    results = conn.execute_query(query)
    
    print("\nCurrent Relationships:")
    for result in results:
        print(f"  {result['source']} --[{result['relationship']}]--> {result['target']}")
        print(f"    Since: {result.get('since', 'Unknown')}")
    
    # Query entities by change frequency
    query_changes = """
    MATCH (e:Entity)
    WHERE e.change_count > 0
    RETURN e.name as entity, e.type as type, e.change_count as changes,
           e.is_unstable as unstable
    ORDER BY e.change_count DESC
    LIMIT 5
    """
    
    change_results = conn.execute_query(query_changes)
    
    print("\nMost Frequently Changed Entities:")
    for result in change_results:
        status = "⚠️ UNSTABLE" if result.get('unstable') else "✓ Stable"
        print(f"  {result['entity']} ({result['type']}): {result['changes']} changes - {status}")
    
    conn.close()


def main():
    """Run all examples."""
    print("\n" + "="*70)
    print("Self-Healing Knowledge Graph - Example Usage")
    print("="*70)
    
    try:
        # Run examples
        example_basic_ingestion()
        example_batch_ingestion()
        example_conflict_detection()
        example_observability()
        example_temporal_queries()
        example_self_healing()
        
        print("\n" + "="*70)
        print("All examples completed successfully!")
        print("="*70)
        print("\nNext Steps:")
        print("1. Run the dashboard: streamlit run dashboard.py")
        print("2. Run full system: python main.py --mode full")
        print("3. Enable continuous monitoring: python main.py --continuous")
        print("\n")
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        print("\nMake sure:")
        print("1. Neo4j is running")
        print("2. Environment variables are set in .env file")
        print("3. Dependencies are installed: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
