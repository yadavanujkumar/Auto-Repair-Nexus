# Architecture Documentation

## Self-Healing Agentic Knowledge Graph Architecture

### System Overview

The Self-Healing Agentic Knowledge Graph is a high-reliability enterprise data retrieval system that automatically detects and corrects inconsistencies in graph data using AI-powered agents.

## Architecture Layers

### 1. Data Layer (Neo4j Graph Database)

**Components:**
- Graph database storing entities and relationships
- Temporal tracking with timestamps
- Constraint and index management
- Source document references

**Data Model:**

```
Nodes:
├── Entity
│   ├── Properties: id, name, type, timestamp, change_count
│   ├── Flags: is_unstable, has_conflict
│   └── Metadata: source_document, last_healed_at
│
├── ConflictLog
│   ├── Properties: conflict_id, severity, detected_at
│   └── Status: resolved, resolution_decision
│
└── MetricsSnapshot
    ├── Metrics: accuracy_score, total_cost, tokens_used
    └── Timestamp: snapshot_time

Relationships:
└── RELATED_TO
    ├── Properties: type, timestamp, confidence
    ├── Flags: is_current, is_verified
    └── Metadata: source_document, verification_reasoning
```

### 2. Ingestion Layer

**Module:** `src/ingestion/`

**Components:**

```
TemporalGraphIngestion
├── ingest_entity()      → Create/update entities with timestamps
├── ingest_relationship() → Create relationships with metadata
├── ingest_fact()        → Convenient triple ingestion (S-P-O)
└── batch_ingest_facts() → Bulk data loading
```

**Features:**
- Temporal tracking of all changes
- Source document attribution
- Change counting for instability detection
- Batch processing support

### 3. Agent Layer

**Module:** `src/agents/`

#### 3.1 Conflict Detection Agent (Reflexion)

**File:** `conflict_detection.py`

```
ConflictDetectionAgent
├── detect_duplicate_relationships()
│   → Finds entities with multiple same-type relationships
│
├── detect_contradictory_facts()
│   → Identifies low-confidence or outdated relationships
│
├── mark_conflict_in_graph()
│   → Flags entities with conflicts
│
└── run_detection_cycle()
    → Complete detection and logging cycle
```

**Detection Strategies:**
1. **Duplicate Relationships**: Same entity with multiple relationships of same type
2. **Temporal Conflicts**: Overlapping time periods for exclusive relationships
3. **Confidence-Based**: Low confidence scores indicating uncertainty
4. **Outdated Information**: Relationships marked as not current

#### 3.2 Self-Correction Agent

**File:** `self_correction.py`

```
SelfCorrectionAgent
├── DeepResearchTask
│   ├── analyze_source_documents()
│   │   → Uses GPT-4 to analyze conflicting evidence
│   └── _prepare_conflict_context()
│       → Formats conflict for LLM analysis
│
├── fetch_source_documents()
│   → Retrieves original source materials
│
├── apply_correction()
│   → Updates graph with verified facts
│   ├── Mark correct relationship as current
│   ├── Flag outdated relationships
│   └── Update confidence scores
│
└── heal_all_conflicts()
    → Complete healing cycle with metrics
```

**Healing Process:**
1. Fetch source documents for conflicting facts
2. Prepare context with all conflicting information
3. Use GPT-4 to analyze and determine truth
4. Apply corrections via Cypher queries
5. Update confidence scores and timestamps
6. Log resolution and track token usage

### 4. Observability Layer

**Module:** `src/observability/`

**File:** `metrics.py`

```
ObservabilityTracker
├── get_current_metrics()
│   → Snapshot of system health
│   ├── Total entities/relationships
│   ├── Conflict counts
│   ├── Data accuracy score
│   └── Cost metrics
│
├── mark_unstable_nodes()
│   → Flag frequently changing entities
│
├── get_unstable_nodes()
│   → List nodes exceeding change threshold
│
├── get_high_risk_nodes()
│   → Entities with conflicts + instability
│
└── store_metrics_snapshot()
    → Historical tracking
```

**Key Metrics:**

1. **Data Accuracy Score**
   ```
   accuracy = 1 - (entities_with_conflicts / total_entities)
   ```

2. **Cost-to-Verify**
   ```
   cost = (tokens_used / 1000) × cost_per_1k_tokens
   ```

3. **Node Stability**
   ```
   unstable = change_count >= threshold
   ```

4. **Average Confidence**
   ```
   avg_confidence = mean(relationship.confidence where is_current=true)
   ```

### 5. Presentation Layer

#### 5.1 Streamlit Dashboard

**File:** `dashboard.py`

**Features:**
- Real-time metrics visualization
- Interactive conflict management
- Cost and accuracy tracking
- Node health monitoring
- Control panel for operations

**Dashboard Sections:**

```
Dashboard
├── Metrics Overview
│   ├── Data Accuracy Score (gauge)
│   ├── Total Healing Cost (USD)
│   ├── Active Conflicts (count)
│   └── Unstable Nodes (count)
│
├── System Statistics
│   ├── Entity/Relationship counts (bar chart)
│   └── Conflict resolution (pie chart)
│
├── Cost Analysis
│   ├── Token usage tracking
│   └── Cost per entity metrics
│
└── Node Health
    ├── Unstable nodes table
    └── High-risk nodes table
```

#### 5.2 CLI Interface

**File:** `main.py`

**Operations:**
```bash
# Setup and configuration
python main.py --mode setup

# Data ingestion
python main.py --mode demo

# Conflict detection
python main.py --mode detect

# Self-healing
python main.py --mode heal

# Observability
python main.py --mode observe

# Full cycle
python main.py --mode full

# Continuous monitoring
python main.py --continuous --interval 3600
```

## Data Flow

### 1. Ingestion Flow

```
Source Data
    ↓
Temporal Ingestion Pipeline
    ↓
Neo4j Graph Database
    ├── Entities with timestamps
    ├── Relationships with metadata
    └── Change tracking
```

### 2. Conflict Detection Flow

```
Graph Database
    ↓
Conflict Detection Agent (Periodic Query)
    ↓
Semantic Collision Analysis
    ├── Duplicate relationships
    ├── Temporal conflicts
    └── Low confidence facts
    ↓
Conflict Logs + Entity Flags
```

### 3. Self-Healing Flow

```
Detected Conflicts
    ↓
Fetch Source Documents
    ↓
Deep Research Task (GPT-4)
    ├── Analyze evidence
    ├── Determine truth
    └── Assign confidence
    ↓
Apply Corrections (Cypher)
    ├── Update current relationships
    ├── Mark outdated facts
    └── Clear conflict flags
    ↓
Track Metrics (tokens, cost, accuracy)
```

### 4. Observability Flow

```
Graph Operations
    ↓
Metrics Collection
    ├── Entity counts
    ├── Conflict status
    ├── Token usage
    └── Confidence scores
    ↓
Metrics Storage (Neo4j)
    ↓
Dashboard Visualization
```

## Technology Stack Details

### Core Technologies

1. **Neo4j 5.16.0**
   - Native graph database
   - Cypher query language
   - ACID transactions
   - Temporal data support

2. **OpenAI GPT-4**
   - Deep research and fact verification
   - Confidence scoring
   - Natural language reasoning

3. **LangChain/LangGraph**
   - Agent orchestration
   - LLM workflow management
   - State tracking

4. **Streamlit**
   - Interactive dashboard
   - Real-time updates
   - Plotly visualizations

### Supporting Libraries

- **Pydantic**: Data validation and models
- **Python-dotenv**: Configuration management
- **Plotly**: Interactive visualizations
- **Pandas**: Data manipulation

## Deployment Architecture

### Local Development

```
Developer Machine
├── Python Application
├── Neo4j (Docker/Local)
└── Environment Variables (.env)
```

### Docker Deployment

```
Docker Compose
├── Neo4j Container
│   ├── Data volume
│   ├── Plugins volume
│   └── Ports: 7474, 7687
│
└── Application Container
    ├── Streamlit Dashboard
    ├── Port: 8501
    └── Shared data volume
```

### Production Deployment

```
Production Environment
├── Load Balancer
├── Application Servers (N instances)
│   ├── Streamlit Dashboard
│   ├── CLI Workers
│   └── Scheduled Healers
│
├── Neo4j Cluster
│   ├── Core Servers (Consensus)
│   └── Read Replicas
│
├── LangSmith (Observability)
│   ├── Trace collection
│   └── Performance monitoring
│
└── OpenAI API
    └── Rate limiting & retry logic
```

## Security Considerations

1. **Credentials Management**
   - Environment variables for secrets
   - No hardcoded credentials
   - .env file excluded from version control

2. **API Security**
   - OpenAI API key rotation
   - Rate limiting on LLM calls
   - Cost monitoring and caps

3. **Database Security**
   - Neo4j authentication required
   - Encrypted connections (TLS)
   - Regular backups

4. **Input Validation**
   - Pydantic models for data validation
   - Cypher query parameterization
   - Sanitized user inputs

## Performance Optimization

1. **Database Indexes**
   - Entity IDs (unique constraints)
   - Relationship types
   - Timestamps
   - Conflict flags

2. **Query Optimization**
   - Parameterized queries
   - Appropriate MATCH patterns
   - Index hints where needed

3. **Batch Processing**
   - Bulk data ingestion
   - Grouped conflict detection
   - Parallel healing (when safe)

4. **Caching**
   - Metrics caching in dashboard
   - Connection pooling
   - Query result caching

## Scalability

### Horizontal Scaling

- Multiple application instances
- Neo4j read replicas
- Load balanced API calls

### Vertical Scaling

- Increased Neo4j heap size
- More CPU cores for parallel processing
- SSD storage for database

### Data Scaling

- Graph partitioning strategies
- Archive old conflict logs
- Metrics aggregation

## Monitoring and Alerting

### Key Metrics to Monitor

1. **System Health**
   - Neo4j connectivity
   - Query response times
   - Error rates

2. **Data Quality**
   - Accuracy score trends
   - Conflict resolution rate
   - Unstable node count

3. **Cost Management**
   - Token usage per hour
   - Cost trends
   - Per-entity costs

4. **Performance**
   - Query latency
   - Healing cycle duration
   - Dashboard response time

### Alert Conditions

- Data accuracy drops below 90%
- Unresolved conflicts exceed threshold
- Cost per hour exceeds budget
- System errors spike
- Neo4j connection failures

## Future Enhancements

1. **Advanced Conflict Resolution**
   - Multiple source document ranking
   - Confidence decay over time
   - Expert system rules

2. **Enhanced Observability**
   - Grafana integration
   - Custom alert rules
   - Detailed audit logs

3. **Scalability Improvements**
   - Distributed healing
   - Sharded graph storage
   - Async processing queue

4. **AI Enhancements**
   - Fine-tuned models for fact verification
   - Embedding-based similarity detection
   - Multi-agent collaboration

---

**Document Version:** 1.0  
**Last Updated:** 2024  
**Maintained By:** Auto-Repair-Nexus Team
