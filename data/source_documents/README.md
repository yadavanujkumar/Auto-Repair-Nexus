# Sample Data for Self-Healing Knowledge Graph

This directory contains sample source documents and data for demonstration purposes.

## Sample Facts

Example facts that can be ingested into the knowledge graph:

### Company Leadership
- Amit Kumar [CEO_OF] TechCorp {since: 2024}
- Sarah Johnson [CTO_OF] TechCorp {since: 2023}
- Michael Chen [CFO_OF] TechCorp {since: 2022}

### Company Information
- TechCorp [HEADQUARTERED_IN] San Francisco {since: 2020}
- TechCorp [FOUNDED_IN] 2019
- TechCorp [INDUSTRY] Technology

### Relationships
- Alice Smith [WORKS_AT] TechCorp {role: Senior Engineer, since: 2023}
- Bob Johnson [MANAGES] Alice Smith {since: 2023}
- TechCorp [ACQUIRED] StartupX {date: 2024-03-15}

### Intentional Conflicts (for demonstration)
- Amit Kumar [CEO_OF] InnovateCorp {since: 2025} (conflicts with TechCorp CEO role)
- TechCorp [HEADQUARTERED_IN] New York {since: 2025} (conflicts with SF headquarters)

## Source Document References

In a production system, these would be actual documents:

- `company_records_2024.pdf` - Official company records
- `press_release_2024.pdf` - Press releases and announcements
- `hr_records.pdf` - HR and employee records
- `org_chart.pdf` - Organizational structure
- `financial_reports_2024.pdf` - Financial statements
- `news_article_2024.txt` - News articles and external sources

## Using Sample Data

Load sample data using the examples script:

```bash
python examples.py
```

Or programmatically:

```python
from src.ingestion import TemporalGraphIngestion
from src.utils import get_connection

conn = get_connection()
ingestion = TemporalGraphIngestion(conn)

# Load your facts
facts = [...]
ingestion.batch_ingest_facts(facts)
```
