"""
Main orchestration script for the Self-Healing Knowledge Graph system.
Coordinates ingestion, conflict detection, and self-correction.
"""
import time
import argparse
from datetime import datetime

from src.utils import get_connection, load_config
from src.ingestion import TemporalGraphIngestion
from src.agents import ConflictDetectionAgent, SelfCorrectionAgent
from src.observability import ObservabilityTracker


def setup_system():
    """Set up the Neo4j connection and schema."""
    print("=" * 70)
    print("Self-Healing Agentic Knowledge Graph Setup")
    print("=" * 70)
    
    conn = get_connection()
    conn.setup_schema()
    
    print("\n✓ System setup complete\n")
    return conn


def run_ingestion_demo(conn):
    """Run a demonstration of the ingestion pipeline."""
    print("=" * 70)
    print("Temporal Graph Ingestion Demo")
    print("=" * 70)
    
    ingestion = TemporalGraphIngestion(conn)
    
    # Example facts with temporal information
    facts = [
        {
            "subject": "Amit",
            "predicate": "CEO_OF",
            "object": "CompanyX",
            "metadata": {"since": "2024", "location": "San Francisco"},
            "source_document": "company_records_2024.pdf"
        },
        {
            "subject": "Sarah",
            "predicate": "CTO_OF",
            "object": "CompanyX",
            "metadata": {"since": "2023"},
            "source_document": "company_records_2023.pdf"
        },
        {
            "subject": "CompanyX",
            "predicate": "HEADQUARTERED_IN",
            "object": "San Francisco",
            "metadata": {"moved": "2020"},
            "source_document": "company_info.pdf"
        },
        # Intentional conflict - Amit as CEO of two companies
        {
            "subject": "Amit",
            "predicate": "CEO_OF",
            "object": "CompanyY",
            "metadata": {"since": "2025"},
            "source_document": "press_release_2025.pdf"
        },
    ]
    
    print(f"\nIngesting {len(facts)} facts...\n")
    results = ingestion.batch_ingest_facts(facts)
    
    for i, result in enumerate(results, 1):
        if "error" not in result:
            print(f"✓ Fact {i} ingested successfully")
        else:
            print(f"✗ Fact {i} failed: {result['error']}")
    
    print(f"\n✓ Ingestion complete: {len(results)} facts processed\n")


def run_conflict_detection(conn):
    """Run conflict detection cycle."""
    print("=" * 70)
    print("Conflict Detection Cycle")
    print("=" * 70)
    
    agent = ConflictDetectionAgent(conn)
    conflicts = agent.run_detection_cycle()
    
    if conflicts:
        print("\n📋 Detected Conflicts:\n")
        for i, conflict in enumerate(conflicts, 1):
            print(f"{i}. {conflict.description}")
            print(f"   Severity: {conflict.severity}")
            print(f"   Entity: {conflict.entity_name}")
            print(f"   Relationship Type: {conflict.relationship_type}")
            print(f"   Conflicting Values: {len(conflict.conflicting_relationships)}")
            print()
    else:
        print("\n✓ No conflicts detected\n")
    
    return conflicts


def run_self_healing(conn, conflicts):
    """Run self-healing process on detected conflicts."""
    if not conflicts:
        print("\n⚠ No conflicts to heal\n")
        return
    
    print("=" * 70)
    print("Self-Healing Process")
    print("=" * 70)
    
    config = load_config()
    agent = SelfCorrectionAgent(conn, config.openai.api_key)
    
    summary = agent.heal_all_conflicts(conflicts)
    
    print("\n📊 Healing Summary:")
    print(f"   Total Conflicts: {summary['total_conflicts']}")
    print(f"   Successful: {summary['successful_corrections']}")
    print(f"   Failed: {summary['failed_corrections']}")
    print(f"   Tokens Used: {summary['total_tokens_used']:,}")
    print()


def run_observability_report(conn):
    """Generate and display observability metrics."""
    print("=" * 70)
    print("Observability Report")
    print("=" * 70)
    
    tracker = ObservabilityTracker(conn)
    
    # Mark unstable nodes
    unstable_count = tracker.mark_unstable_nodes()
    print(f"\n✓ Marked {unstable_count} nodes as unstable")
    
    # Get current metrics
    metrics = tracker.get_current_metrics()
    
    print("\n📊 System Metrics:")
    print(f"   Total Entities: {metrics.total_entities}")
    print(f"   Total Relationships: {metrics.total_relationships}")
    print(f"   Entities with Conflicts: {metrics.entities_with_conflicts}")
    print(f"   Resolved Conflicts: {metrics.resolved_conflicts}")
    print(f"   Unresolved Conflicts: {metrics.unresolved_conflicts}")
    print(f"   Unstable Nodes: {metrics.unstable_nodes}")
    print(f"   Data Accuracy Score: {metrics.data_accuracy_score:.2%}")
    print(f"   Average Confidence: {metrics.average_confidence:.2%}")
    print(f"   Total Tokens Used: {metrics.total_tokens_used:,}")
    print(f"   Total Healing Cost: ${metrics.total_healing_cost:.4f}")
    
    # Store snapshot
    tracker.store_metrics_snapshot(metrics)
    print("\n✓ Metrics snapshot stored")
    
    # Get high-risk nodes
    high_risk = tracker.get_high_risk_nodes(limit=5)
    if high_risk:
        print("\n⚠️  Top High-Risk Nodes:")
        for i, node in enumerate(high_risk, 1):
            print(f"   {i}. {node.entity_name}")
            print(f"      - Changes: {node.change_count}")
            print(f"      - Healings: {node.healing_count}")
            print(f"      - Confidence: {node.confidence_score:.2%}")
    else:
        print("\n✓ No high-risk nodes found")
    
    print()


def main():
    """Main entry point for the orchestration system."""
    parser = argparse.ArgumentParser(
        description="Self-Healing Agentic Knowledge Graph Orchestrator"
    )
    parser.add_argument(
        "--mode",
        choices=["setup", "demo", "detect", "heal", "observe", "full"],
        default="full",
        help="Operation mode"
    )
    parser.add_argument(
        "--continuous",
        action="store_true",
        help="Run in continuous mode (keeps running)"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=3600,
        help="Interval in seconds for continuous mode (default: 3600)"
    )
    
    args = parser.parse_args()
    
    try:
        conn = setup_system()
        
        if args.mode == "setup":
            print("✓ Setup complete")
            return
        
        if args.mode == "demo" or args.mode == "full":
            run_ingestion_demo(conn)
        
        if args.mode == "detect" or args.mode == "full":
            conflicts = run_conflict_detection(conn)
            
            if args.mode == "heal" or args.mode == "full":
                run_self_healing(conn, conflicts)
        
        if args.mode == "observe" or args.mode == "full":
            run_observability_report(conn)
        
        if args.continuous:
            print(f"\n🔄 Entering continuous mode (interval: {args.interval}s)")
            print("Press Ctrl+C to stop\n")
            
            try:
                while True:
                    time.sleep(args.interval)
                    print(f"\n[{datetime.utcnow().isoformat()}] Running scheduled cycle...")
                    
                    conflicts = run_conflict_detection(conn)
                    if conflicts:
                        run_self_healing(conn, conflicts)
                    
                    run_observability_report(conn)
                    
            except KeyboardInterrupt:
                print("\n\n✓ Continuous mode stopped")
        
        print("\n" + "=" * 70)
        print("System execution complete")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        raise
    finally:
        if 'conn' in locals():
            conn.close()


if __name__ == "__main__":
    main()
