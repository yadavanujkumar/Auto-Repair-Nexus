# Quick Start Guide

## 5-Minute Setup

### 1. Prerequisites Check

```bash
# Check Python version (requires 3.8+)
python --version

# Check if Neo4j is available
# Option A: Using Docker (recommended)
docker --version

# Option B: Local installation
# Download from https://neo4j.com/download/
```

### 2. Start Neo4j

**Using Docker (Recommended):**
```bash
docker run \
    --name neo4j-knowledge-graph \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/your_password \
    -v $HOME/neo4j/data:/data \
    neo4j:5.16.0
```

Access Neo4j Browser at: http://localhost:7474
- Username: `neo4j`
- Password: `your_password`

**Using Local Installation:**
```bash
neo4j start
```

### 3. Setup Project

```bash
# Clone repository
git clone https://github.com/yadavanujkumar/Auto-Repair-Nexus.git
cd Auto-Repair-Nexus

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your credentials
```

### 4. Configure .env File

Edit `.env` with your configuration:

```env
# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# OpenAI API Key
OPENAI_API_KEY=sk-your-openai-api-key-here

# LangSmith (Optional - for advanced tracing)
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=
LANGCHAIN_PROJECT=auto-repair-nexus
```

### 5. Run the System

**Option A: Full Demo**
```bash
python main.py --mode full
```

This will:
1. Setup the Neo4j schema
2. Ingest sample data
3. Detect conflicts
4. Run self-healing (if OpenAI key is configured)
5. Generate observability report

**Option B: Interactive Dashboard**
```bash
streamlit run dashboard.py
```

Then open your browser to: http://localhost:8501

**Option C: Run Examples**
```bash
python examples.py
```

### 6. Verify Installation

You should see output like:
```
✓ Connected to Neo4j at bolt://localhost:7687
✓ Setup complete
✓ Ingested 4 facts successfully
✓ Detected 1 conflicts
✓ Data Accuracy Score: 98.50%
```

## Common Operations

### Add Data to Knowledge Graph

```python
from src.utils import get_connection
from src.ingestion import TemporalGraphIngestion

conn = get_connection()
ingestion = TemporalGraphIngestion(conn)

# Simple fact ingestion
ingestion.ingest_fact(
    subject="John Doe",
    predicate="WORKS_AT",
    object="TechCorp",
    metadata={"since": "2024", "role": "Engineer"},
    source_document="hr_records.pdf"
)
```

### Detect and View Conflicts

```bash
# Via CLI
python main.py --mode detect

# Or programmatically
```

```python
from src.agents import ConflictDetectionAgent

detector = ConflictDetectionAgent(conn)
conflicts = detector.run_detection_cycle()

for conflict in conflicts:
    print(f"Conflict: {conflict.description}")
```

### Run Self-Healing

```bash
# Requires OPENAI_API_KEY in .env
python main.py --mode heal
```

### Monitor System Health

```bash
# Generate report
python main.py --mode observe

# Or use dashboard
streamlit run dashboard.py
```

## Continuous Monitoring

Run the system in continuous mode to automatically detect and heal conflicts:

```bash
# Check every hour (3600 seconds)
python main.py --continuous --interval 3600

# Check every 30 minutes
python main.py --continuous --interval 1800
```

## Troubleshooting

### "Failed to connect to Neo4j"

**Check if Neo4j is running:**
```bash
# Docker
docker ps | grep neo4j

# Local
neo4j status
```

**Verify credentials:**
- Check `.env` file has correct URI, username, and password
- Try connecting via Neo4j Browser: http://localhost:7474

### "OpenAI API Error"

**Verify API key:**
```bash
# Test API key
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

**Check balance:**
- Visit https://platform.openai.com/account/billing

### "Import Error" or "Module not found"

**Reinstall dependencies:**
```bash
pip install -r requirements.txt --upgrade
```

**Verify virtual environment is activated:**
```bash
which python  # Should point to venv/bin/python
```

## Next Steps

1. **Customize for Your Use Case**
   - Modify entity types in `src/ingestion/temporal_ingestion.py`
   - Adjust conflict detection rules in `src/agents/conflict_detection.py`
   - Configure thresholds in `.env`

2. **Load Your Data**
   - Prepare your data as facts (subject, predicate, object)
   - Use batch ingestion: `ingestion.batch_ingest_facts(facts)`
   - Track source documents for verification

3. **Set Up Production Monitoring**
   - Enable LangSmith tracing for detailed observability
   - Configure alerting based on data accuracy scores
   - Schedule regular healing cycles

4. **Integrate with Your Systems**
   - Connect to your document store
   - Add custom data sources
   - Implement domain-specific conflict resolution logic

## Resources

- **Documentation**: See README.md
- **Examples**: Run `python examples.py`
- **Dashboard**: Run `streamlit run dashboard.py`
- **Neo4j Browser**: http://localhost:7474

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the examples in `examples.py`
3. Open an issue on GitHub

---

**You're all set! 🚀 Start building your self-healing knowledge graph.**
