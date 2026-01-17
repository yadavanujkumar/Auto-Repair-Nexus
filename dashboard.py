"""
Streamlit Dashboard for Self-Healing Knowledge Graph
Displays metrics, conflicts, and system health.
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils import Neo4jConnection, get_connection, load_config
from src.agents import ConflictDetectionAgent, SelfCorrectionAgent
from src.observability import ObservabilityTracker


# Page configuration
st.set_page_config(
    page_title="Self-Healing Knowledge Graph Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)


def init_connection():
    """Initialize Neo4j connection."""
    if 'neo4j_conn' not in st.session_state:
        try:
            st.session_state.neo4j_conn = get_connection()
            st.session_state.connected = True
        except Exception as e:
            st.session_state.connected = False
            st.error(f"Failed to connect to Neo4j: {e}")
    return st.session_state.get('neo4j_conn')


def main():
    """Main dashboard application."""
    st.title("🧠 Self-Healing Knowledge Graph Dashboard")
    st.markdown("### Value-at-Risk Observability for Enterprise Data Retrieval")
    
    # Initialize connection
    conn = init_connection()
    
    if not st.session_state.get('connected'):
        st.warning("⚠️ Not connected to Neo4j. Please check your configuration.")
        st.info("""
        **Configuration Required:**
        1. Ensure Neo4j is running
        2. Set environment variables in `.env` file:
           - NEO4J_URI
           - NEO4J_USERNAME
           - NEO4J_PASSWORD
           - OPENAI_API_KEY
        """)
        return
    
    # Initialize components
    tracker = ObservabilityTracker(conn)
    conflict_agent = ConflictDetectionAgent(conn)
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Control Panel")
        
        # Refresh button
        if st.button("🔄 Refresh Metrics", use_container_width=True):
            st.rerun()
            
        st.divider()
        
        # Run conflict detection
        if st.button("🔍 Detect Conflicts", type="primary", use_container_width=True):
            with st.spinner("Detecting conflicts..."):
                conflicts = conflict_agent.run_detection_cycle()
                st.success(f"✓ Detected {len(conflicts)} conflicts")
                st.rerun()
                
        # Run self-healing
        if st.button("🔧 Run Self-Healing", type="primary", use_container_width=True):
            with st.spinner("Running self-healing process..."):
                try:
                    config = load_config()
                    correction_agent = SelfCorrectionAgent(conn, config.openai.api_key)
                    
                    # Get unresolved conflicts
                    query = "MATCH (c:ConflictLog) WHERE c.resolved = false RETURN c"
                    unresolved = conn.execute_query(query)
                    
                    if unresolved:
                        st.info(f"Found {len(unresolved)} unresolved conflicts")
                        # Note: In production, would convert to SemanticConflict objects
                        st.warning("Self-healing requires conflict objects - run detection first")
                    else:
                        st.info("No unresolved conflicts found")
                except Exception as e:
                    st.error(f"Error during self-healing: {e}")
                    
        st.divider()
        
        # Mark unstable nodes
        if st.button("⚠️ Mark Unstable Nodes", use_container_width=True):
            count = tracker.mark_unstable_nodes()
            st.success(f"✓ Marked {count} nodes as unstable")
            st.rerun()
    
    # Get current metrics
    metrics = tracker.get_current_metrics()
    
    # Main metrics row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Data Accuracy Score",
            f"{metrics.data_accuracy_score:.2%}",
            delta="Target: 95%",
            delta_color="normal" if metrics.data_accuracy_score >= 0.95 else "inverse"
        )
        
    with col2:
        st.metric(
            "Total Healing Cost",
            f"${metrics.total_healing_cost:.2f}",
            delta=f"{metrics.total_tokens_used:,} tokens"
        )
        
    with col3:
        st.metric(
            "Active Conflicts",
            metrics.unresolved_conflicts,
            delta=f"Resolved: {metrics.resolved_conflicts}"
        )
        
    with col4:
        st.metric(
            "Unstable Nodes",
            metrics.unstable_nodes,
            delta=f"Total: {metrics.total_entities}",
            delta_color="inverse" if metrics.unstable_nodes > 0 else "off"
        )
    
    st.divider()
    
    # Two column layout for charts
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📊 System Overview")
        
        # Entity and relationship counts
        overview_data = {
            "Metric": ["Total Entities", "Total Relationships", "Entities with Conflicts"],
            "Count": [metrics.total_entities, metrics.total_relationships, metrics.entities_with_conflicts]
        }
        overview_df = pd.DataFrame(overview_data)
        
        fig_overview = px.bar(
            overview_df,
            x="Metric",
            y="Count",
            color="Metric",
            title="Graph Statistics"
        )
        st.plotly_chart(fig_overview, use_container_width=True)
        
    with col_right:
        st.subheader("🎯 Conflict Resolution")
        
        # Conflict resolution status
        conflict_data = {
            "Status": ["Resolved", "Unresolved"],
            "Count": [metrics.resolved_conflicts, metrics.unresolved_conflicts]
        }
        conflict_df = pd.DataFrame(conflict_data)
        
        fig_conflicts = px.pie(
            conflict_df,
            names="Status",
            values="Count",
            title="Conflict Status",
            color="Status",
            color_discrete_map={"Resolved": "green", "Unresolved": "red"}
        )
        st.plotly_chart(fig_conflicts, use_container_width=True)
    
    st.divider()
    
    # Cost-to-Verify vs Data Accuracy
    st.subheader("💰 Cost-to-Verify vs Data Accuracy")
    
    col_cost1, col_cost2 = st.columns(2)
    
    with col_cost1:
        # Gauge chart for data accuracy
        fig_accuracy = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=metrics.data_accuracy_score * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Data Accuracy %"},
            delta={'reference': 95},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 70], 'color': "lightgray"},
                    {'range': [70, 90], 'color': "yellow"},
                    {'range': [90, 100], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ))
        st.plotly_chart(fig_accuracy, use_container_width=True)
        
    with col_cost2:
        # Cost breakdown
        st.markdown("**💵 Cost Breakdown**")
        st.metric("Total Tokens Used", f"{metrics.total_tokens_used:,}")
        st.metric("Cost per 1K Tokens", "$0.03")
        st.metric("Total Cost", f"${metrics.total_healing_cost:.4f}")
        
        if metrics.total_entities > 0:
            cost_per_entity = metrics.total_healing_cost / metrics.total_entities
            st.metric("Cost per Entity", f"${cost_per_entity:.6f}")
    
    st.divider()
    
    # Unstable and high-risk nodes
    st.subheader("⚠️ High-Risk & Unstable Nodes")
    
    tab1, tab2 = st.tabs(["Unstable Nodes", "High-Risk Nodes"])
    
    with tab1:
        unstable_nodes = tracker.get_unstable_nodes(limit=20)
        
        if unstable_nodes:
            unstable_data = []
            for node in unstable_nodes:
                unstable_data.append({
                    "Entity Name": node.entity_name,
                    "Change Count": node.change_count,
                    "Healing Count": node.healing_count,
                    "Has Conflict": "Yes" if node.has_conflict else "No",
                    "Confidence": f"{node.confidence_score:.2%}",
                    "Last Healed": node.last_healed_at or "Never"
                })
            
            unstable_df = pd.DataFrame(unstable_data)
            st.dataframe(unstable_df, use_container_width=True, height=400)
        else:
            st.info("No unstable nodes found")
    
    with tab2:
        high_risk_nodes = tracker.get_high_risk_nodes(limit=20)
        
        if high_risk_nodes:
            risk_data = []
            for node in high_risk_nodes:
                risk_data.append({
                    "Entity Name": node.entity_name,
                    "Change Count": node.change_count,
                    "Healing Count": node.healing_count,
                    "Confidence": f"{node.confidence_score:.2%}",
                    "Last Healed": node.last_healed_at or "Never"
                })
            
            risk_df = pd.DataFrame(risk_data)
            st.dataframe(risk_df, use_container_width=True, height=400)
        else:
            st.success("No high-risk nodes found! 🎉")
    
    # Footer
    st.divider()
    st.caption(f"Last updated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")


if __name__ == "__main__":
    main()
