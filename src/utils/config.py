"""
Configuration management for the self-healing knowledge graph system.
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Neo4jConfig:
    """Neo4j database configuration."""
    uri: str
    username: str
    password: str


@dataclass
class OpenAIConfig:
    """OpenAI API configuration."""
    api_key: str
    model: str = "gpt-4"
    embedding_model: str = "text-embedding-3-small"


@dataclass
class LangSmithConfig:
    """LangSmith observability configuration."""
    enabled: bool
    api_key: Optional[str]
    project: str


@dataclass
class ObservabilityConfig:
    """Observability and monitoring configuration."""
    token_cost_per_1k: float = 0.03  # USD per 1K tokens (GPT-4)
    accuracy_threshold: float = 0.95
    unstable_node_threshold: int = 3  # Changes before marked unstable
    healing_check_interval: int = 3600  # Seconds (1 hour)


@dataclass
class Config:
    """Main application configuration."""
    neo4j: Neo4jConfig
    openai: OpenAIConfig
    langsmith: LangSmithConfig
    observability: ObservabilityConfig


def load_config() -> Config:
    """Load configuration from environment variables."""
    neo4j_config = Neo4jConfig(
        uri=os.getenv("NEO4J_URI", "bolt://localhost:7687"),
        username=os.getenv("NEO4J_USERNAME", "neo4j"),
        password=os.getenv("NEO4J_PASSWORD", "password"),
    )
    
    openai_config = OpenAIConfig(
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model=os.getenv("OPENAI_MODEL", "gpt-4"),
        embedding_model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
    )
    
    langsmith_config = LangSmithConfig(
        enabled=os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true",
        api_key=os.getenv("LANGCHAIN_API_KEY"),
        project=os.getenv("LANGCHAIN_PROJECT", "auto-repair-nexus"),
    )
    
    observability_config = ObservabilityConfig(
        token_cost_per_1k=float(os.getenv("TOKEN_COST_PER_1K", "0.03")),
        accuracy_threshold=float(os.getenv("ACCURACY_THRESHOLD", "0.95")),
        unstable_node_threshold=int(os.getenv("UNSTABLE_NODE_THRESHOLD", "3")),
        healing_check_interval=int(os.getenv("HEALING_CHECK_INTERVAL", "3600")),
    )
    
    return Config(
        neo4j=neo4j_config,
        openai=openai_config,
        langsmith=langsmith_config,
        observability=observability_config,
    )
