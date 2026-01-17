# Auto-Repair-Nexus

## Self-Healing Agentic Knowledge Graph

A high-reliability enterprise data retrieval system that uses Neo4j graph database and LlamaIndex/LangGraph orchestration to create a self-healing knowledge graph with temporal tracking, conflict detection, and automated correction.

## 🌟 Features

### Core Deliverables

1. **Temporal Graph Ingestion Pipeline**
   - Stores entities with timestamps (e.g., 'Amit [CEO_OF] CompanyX {since: 2024}')
   - Tracks source documents for fact verification
   - Supports batch ingestion of facts and relationships

2. **Conflict Detection Agent (Reflexion)**
   - Periodically queries the graph for 'Semantic Collisions'
   - Detects cases where the same relationship has multiple conflicting values
   - Marks entities with conflicts and tracks severity

3. **Self-Correction Logic**
   - Deep Research task that accesses original source documents
   - Uses OpenAI GPT-4 to determine which fact is most recent or authoritative
   - Updates the graph using Cypher queries with confidence scores

4. **Value-at-Risk Observability**
   - Tracks 'Cost-to-Verify' (LLM tokens spent on healing)
   - Monitors 'Data Accuracy Score' across the knowledge graph
   - Flags nodes that are 'Unstable' (frequently changing)
   - Interactive Streamlit dashboard for visualization

## 🛠️ Tech Stack

- **Graph Database**: Neo4j
- **LLM**: OpenAI GPT-4
- **Orchestration**: LangGraph, LangChain
- **Observability**: LangSmith
- **Dashboard**: Streamlit
- **Language**: Python 3.8+

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Neo4j 5.x running locally or remotely
- OpenAI API key

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yadavanujkumar/Auto-Repair-Nexus.git
   cd Auto-Repair-Nexus
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

   Required environment variables:
   - `NEO4J_URI`: Neo4j connection URI (default: bolt://localhost:7687)
   - `NEO4J_USERNAME`: Neo4j username (default: neo4j)
   - `NEO4J_PASSWORD`: Your Neo4j password
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `LANGCHAIN_TRACING_V2`: Enable LangSmith tracing (optional)
   - `LANGCHAIN_API_KEY`: Your LangSmith API key (optional)

5. **Start Neo4j**
   
   Ensure Neo4j is running before starting the application.

## 🚀 Usage

### Command Line Interface

The system provides a comprehensive CLI for all operations:

```bash
# Full demo (setup + ingestion + detection + healing + observability)
python main.py --mode full

# Setup only (initialize schema)
python main.py --mode setup

# Run ingestion demo
python main.py --mode demo

# Detect conflicts only
python main.py --mode detect

# Run self-healing
python main.py --mode heal

# Generate observability report
python main.py --mode observe

# Continuous monitoring mode
python main.py --mode full --continuous --interval 3600
```

### Streamlit Dashboard

Launch the interactive dashboard:

```bash
streamlit run dashboard.py
```

The dashboard provides:
- Real-time metrics and KPIs
- Data accuracy score tracking
- Cost-to-verify monitoring
- Conflict detection and resolution status
- Unstable and high-risk node identification
- Interactive visualizations with Plotly

### Programmatic Usage

```python
from src.utils import get_connection
from src.ingestion import TemporalGraphIngestion
from src.agents import ConflictDetectionAgent, SelfCorrectionAgent
from src.observability import ObservabilityTracker

# Initialize connection
conn = get_connection()
conn.setup_schema()

# Ingest temporal facts
ingestion = TemporalGraphIngestion(conn)
ingestion.ingest_fact(
    subject="Amit",
    predicate="CEO_OF",
    object="CompanyX",
    metadata={"since": "2024"},
    source_document="records.pdf"
)

# Detect conflicts
detector = ConflictDetectionAgent(conn)
conflicts = detector.run_detection_cycle()

# Self-heal conflicts
healer = SelfCorrectionAgent(conn)
summary = healer.heal_all_conflicts(conflicts)

# Track metrics
tracker = ObservabilityTracker(conn)
metrics = tracker.get_current_metrics()
print(f"Data Accuracy: {metrics.data_accuracy_score:.2%}")
print(f"Total Cost: ${metrics.total_healing_cost:.4f}")
```

## 📊 Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Dashboard                       │
│            (Visualization & Control Interface)               │
└─────────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
┌─────────▼─────────┐ ┌───▼────────┐ ┌────▼──────────────┐
│   Ingestion       │ │  Agents    │ │  Observability    │
│   Pipeline        │ │  Module    │ │  Tracker          │
│                   │ │            │ │                   │
│ • Temporal Data   │ │ • Conflict │ │ • Metrics         │
│ • Entity/Rel      │ │   Detection│ │ • Cost Tracking   │
│ • Batch Loading   │ │ • Self-    │ │ • Node Health     │
│                   │ │   Correction│ │ • Accuracy Score  │
└─────────┬─────────┘ └───┬────────┘ └────┬──────────────┘
          │               │               │
          └───────────────┼───────────────┘
                          │
                  ┌───────▼────────┐
                  │   Neo4j        │
                  │   Graph DB     │
                  └────────────────┘
```

### Data Model

#### Entities
- Properties: id, name, type, timestamp, change_count, is_unstable, has_conflict
- Labels: Entity

#### Relationships
- Type: RELATED_TO
- Properties: id, type, timestamp, source_document, confidence, is_current

#### Conflict Logs
- Labels: ConflictLog
- Properties: conflict_id, severity, detected_at, resolved

#### Metrics Snapshots
- Labels: MetricsSnapshot
- Properties: timestamp, accuracy_score, total_cost, etc.

## 🔍 Key Features in Detail

### Temporal Tracking
Every entity and relationship is timestamped, allowing the system to:
- Track changes over time
- Identify the most recent information
- Maintain historical context

### Semantic Collision Detection
The Reflexion agent identifies conflicts such as:
- Multiple values for the same relationship (e.g., person being CEO of two companies)
- Low-confidence relationships
- Outdated information

### Deep Research & Self-Correction
When conflicts are detected:
1. Source documents are retrieved
2. GPT-4 analyzes the evidence
3. The most authoritative fact is identified
4. Graph is updated with confidence scores
5. Outdated relationships are marked

### Observability Dashboard
Tracks critical metrics:
- **Data Accuracy Score**: Percentage of entities without conflicts
- **Cost-to-Verify**: Total LLM token costs for healing
- **Unstable Nodes**: Entities that change frequently
- **Conflict Resolution Rate**: Success rate of self-healing

## 🧪 Example Scenarios

### Scenario 1: CEO Transition
```python
# Initial fact
ingestion.ingest_fact("John", "CEO_OF", "TechCorp", metadata={"since": "2020"})

# New conflicting fact
ingestion.ingest_fact("Jane", "CEO_OF", "TechCorp", metadata={"since": "2024"})

# System detects conflict and resolves:
# - Verifies Jane is current CEO (more recent timestamp)
# - Marks John's relationship as outdated
# - Updates confidence scores
```

### Scenario 2: Data Quality Monitoring
```python
# Track system health
metrics = tracker.get_current_metrics()
if metrics.data_accuracy_score < 0.95:
    # Trigger healing cycle
    conflicts = detector.detect_all_conflicts()
    healer.heal_all_conflicts(conflicts)
```

## 🔒 Security Considerations

- Store sensitive credentials in `.env` file (not committed)
- Use environment-specific Neo4j instances
- Monitor API costs through observability dashboard
- Implement rate limiting for LLM calls in production

## 📈 Performance Tips

- Use batch ingestion for large datasets
- Configure appropriate healing intervals for continuous mode
- Monitor token usage to control costs
- Index frequently queried properties in Neo4j

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Neo4j for graph database technology
- OpenAI for GPT-4 capabilities
- LangChain/LangGraph for orchestration framework
- Streamlit for dashboard framework

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

**Built with ❤️ for enterprise-grade self-healing knowledge graphs**