"""
Neo4j Connection and Configuration Module
"""
import os
from typing import Optional
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()


class Neo4jConnection:
    """Manages Neo4j database connections and operations."""
    
    def __init__(
        self,
        uri: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """Initialize Neo4j connection."""
        self.uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.username = username or os.getenv("NEO4J_USERNAME", "neo4j")
        self.password = password or os.getenv("NEO4J_PASSWORD", "password")
        self.driver = None
        
    def connect(self):
        """Establish connection to Neo4j."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.username, self.password)
            )
            # Test connection
            self.driver.verify_connectivity()
            print(f"✓ Connected to Neo4j at {self.uri}")
        except Exception as e:
            print(f"✗ Failed to connect to Neo4j: {e}")
            raise
            
    def close(self):
        """Close the Neo4j connection."""
        if self.driver:
            self.driver.close()
            print("✓ Neo4j connection closed")
            
    def execute_query(self, query: str, parameters: Optional[dict] = None):
        """Execute a Cypher query and return results."""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")
            
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
            
    def execute_write(self, query: str, parameters: Optional[dict] = None):
        """Execute a write transaction."""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j. Call connect() first.")
            
        with self.driver.session() as session:
            result = session.execute_write(
                lambda tx: tx.run(query, parameters or {}).data()
            )
            return result
            
    def setup_schema(self):
        """Set up the graph schema with constraints and indexes."""
        schema_queries = [
            # Constraints for unique entities
            "CREATE CONSTRAINT entity_id IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
            
            # Indexes for performance
            "CREATE INDEX entity_name IF NOT EXISTS FOR (e:Entity) ON (e.name)",
            "CREATE INDEX relationship_type IF NOT EXISTS FOR ()-[r:RELATED_TO]-() ON (r.type)",
            "CREATE INDEX relationship_timestamp IF NOT EXISTS FOR ()-[r:RELATED_TO]-() ON (r.timestamp)",
            "CREATE INDEX conflict_flag IF NOT EXISTS FOR (e:Entity) ON (e.has_conflict)",
            "CREATE INDEX unstable_flag IF NOT EXISTS FOR (e:Entity) ON (e.is_unstable)",
        ]
        
        for query in schema_queries:
            try:
                self.execute_write(query)
                print(f"✓ Executed: {query[:50]}...")
            except Exception as e:
                # Constraint/index might already exist
                if "already exists" in str(e).lower():
                    print(f"⚠ Already exists: {query[:50]}...")
                else:
                    print(f"✗ Error: {e}")


def get_connection() -> Neo4jConnection:
    """Get a configured Neo4j connection instance."""
    conn = Neo4jConnection()
    conn.connect()
    return conn
