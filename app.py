# app.py
# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
from mdm_engine import DataForgeEngine

# Page Configuration
st.set_page_config(
    page_title="DataForge MDM & Governance Console",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Executive Custom Styling
st.markdown("""
<style>
    /* Dark Deep Space Background */
    .stApp {
        background-color: #0D1117;
        color: #C9D1D9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Executive Header Block */
    .header-banner {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 24px;
        margin-bottom: 24px;
    }
    
    .header-title {
        color: #58A6FF;
        font-size: 2.0rem;
        font-weight: 700;
        margin: 0 0 4px 0;
        letter-spacing: -0.5px;
    }

    .header-subtitle {
        color: #8B949E;
        font-size: 0.95rem;
        margin: 0;
    }

    /* KPI Metric Cards */
    .metric-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 8px;
        padding: 18px;
        position: relative;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
    }

    .border-blue { border-top: 3px solid #58A6FF; }
    .border-green { border-top: 3px solid #3FB950; }
    .border-amber { border-top: 3px solid #D29922; }
    .border-red { border-top: 3px solid #F85149; }

    .card-label {
        color: #8B949E;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    .val-blue { color: #58A6FF; font-size: 2.2rem; font-weight: 700; }
    .val-green { color: #3FB950; font-size: 2.2rem; font-weight: 700; }
    .val-amber { color: #D29922; font-size: 2.2rem; font-weight: 700; }
    .val-red { color: #F85149; font-size: 2.2rem; font-weight: 700; }

    .card-subtext {
        color: #6E7681;
        font-size: 0.78rem;
        margin-top: 4px;
    }

    /* Tab Customization */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 1px solid #30363D;
    }

    .stTabs [data-baseweb="tab"] {
        background-color: #161B22;
        border: 1px solid #30363D;
        border-radius: 6px 6px 0 0;
        color: #8B949E;
        padding: 10px 18px;
        font-weight: 600;
        font-size: 0.9rem;
    }

    .stTabs [aria-selected="true"] {
        background-color: #21262D !important;
        border-color: #58A6FF !important;
        color: #58A6FF !important;
    }
</style>
""", unsafe_allow_html=True)

# Data Loading
def load_data():
    return pd.read_csv("raw_vendor_data.csv")

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading dataset: {e}")
    st.stop()

# Initialize Engine
engine = DataForgeEngine(df)
metrics = engine.run_profiling()
engine.enforce_data_rules()

# Control Sidebar
with st.sidebar:
    st.markdown("### Controls & Parameters")
    st.markdown("---")
    col_to_match = st.selectbox(
        "Fuzzy Match Target Field", 
        [c for c in df.columns if df[c].dtype == 'object'], 
        index=1
    )
    match_threshold = st.slider("Similarity Threshold (%)", 50, 100, 80)
    st.markdown("---")
    st.caption("Engine Version 2.4 | Active Session")

# Main Header
st.markdown("""
<div class="header-banner">
    <div class="header-title">DataForge MDM & Governance Console</div>
    <div class="header-subtitle">Enterprise Master Data Management — Data Profiling, Entity Resolution, and Quarantine Control</div>
</div>
""", unsafe_allow_html=True)

# KPI Cards
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"""
    <div class="metric-card border-blue">
        <div class="card-label">Total Ingested Records</div>
        <div class="val-blue">{metrics['total_records']}</div>
        <div class="card-subtext">Active Input Pipeline</div>
    </div>
    """, unsafe_allow_html=True)

with c2:
    st.markdown(f"""
    <div class="metric-card border-green">
        <div class="card-label">Completeness Index</div>
        <div class="val-green">{metrics['completeness_score']}%</div>
        <div class="card-subtext">Threshold Satisfied</div>
    </div>
    """, unsafe_allow_html=True)

with c3:
    st.markdown(f"""
    <div class="metric-card border-amber">
        <div class="card-label">Exact Duplicates</div>
        <div class="val-amber">{metrics['exact_duplicates']}</div>
        <div class="card-subtext">Flagged for Merging</div>
    </div>
    """, unsafe_allow_html=True)

with c4:
    st.markdown(f"""
    <div class="metric-card border-red">
        <div class="card-label">Quarantined Records</div>
        <div class="val-red">{metrics['quarantined_records']}</div>
        <div class="card-subtext">Integrity Violations</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Navigation Tabs
tab1, tab2, tab3 = st.tabs([
    "Data Health & Analytics", 
    "Entity Resolution (Golden Master)", 
    "Governance Quarantine Log"
])

# Tab 1: Profiling and Analytics
with tab1:
    col_left, col_right = st.columns([1.1, 0.9])
    
    with col_left:
        with st.container(border=True):
            st.markdown("##### Ingested Raw Dataset")
            st.dataframe(df, use_container_width=True, height=360)

    with col_right:
        with st.container(border=True):
            st.markdown("##### Missing Field Breakdown")
            
            null_df = pd.DataFrame(list(metrics['null_metrics'].items()), columns=["Attribute", "Missing Count"])
            
            fig_null = px.bar(
                null_df, 
                x="Attribute", 
                y="Missing Count",
                color="Missing Count",
                color_continuous_scale=["#1F6FEB", "#58A6FF", "#F85149"],
                template="plotly_dark"
            )
            
            fig_null.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(showgrid=False, title=""),
                yaxis=dict(showgrid=True, gridcolor="#30363D", title="Missing Rows"),
                coloraxis_showscale=False,
                margin=dict(l=20, r=20, t=20, b=20),
                height=300
            )
            st.plotly_chart(fig_null, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown("##### Regional Record Distribution")
        if 'Region' in df.columns:
            region_counts = df['Region'].value_counts().reset_index()
            region_counts.columns = ['Region', 'Count']
            
            fig_pie = px.pie(
                region_counts, 
                values='Count', 
                names='Region', 
                hole=0.5,
                color_discrete_sequence=['#58A6FF', '#3FB950', '#D29922', '#A371F7', '#F85149'],
                template="plotly_dark"
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                margin=dict(l=20, r=20, t=20, b=20),
                height=300
            )
            st.plotly_chart(fig_pie, use_container_width=True)

# Tab 2: Golden Master Generation
with tab2:
    golden_df = engine.generate_golden_records(match_column=col_to_match, threshold=match_threshold)

    with st.container(border=True):
        st.markdown("##### Master Golden Records Output")
        st.info(f"Consolidated {engine.audit_summary['merged_duplicates']} record variations into {len(golden_df)} master entries using a {match_threshold}% match threshold.")
        st.dataframe(golden_df, use_container_width=True, height=400)
        
        golden_df.to_csv("golden_master_records.csv", index=False)
        engine.quarantine_df.to_csv("quarantine_records.csv", index=False)

# Tab 3: Quarantine Log
with tab3:
    with st.container(border=True):
        st.markdown("##### Isolated Quarantine Log")
        st.caption("Records missing mandatory business keys or exhibiting validation failures are quarantined automatically.")
        st.dataframe(engine.quarantine_df, use_container_width=True, height=400)
        
        