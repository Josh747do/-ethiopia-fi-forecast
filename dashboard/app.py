# dashboard/app.py - COMPLETE FILE
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import os

# Set page config
st.set_page_config(
    page_title="Ethiopia Financial Inclusion Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title and description
st.title("📈 Ethiopia Financial Inclusion Dashboard")
st.markdown("""
Interactive dashboard for tracking Ethiopia's digital financial transformation.
Forecasting access (account ownership) and usage (digital payments) for 2025-2027.
""")

# Add sidebar
with st.sidebar:
    st.header("Dashboard Navigation")
    page = st.radio(
        "Select Page:",
        ["📊 Overview", "📈 Trends", "🔮 Forecasts", "🎯 Projections", "📋 About"]
    )
    
    st.divider()
    st.header("Settings")
    forecast_year = st.slider("Forecast Horizon (Years)", 1, 5, 3)
    confidence_level = st.slider("Confidence Level (%)", 80, 99, 95)

# Load data function
@st.cache_data
def load_data():
    """Load all forecasting data from Task 4 outputs"""
    
    # Define paths to Task 4 outputs
    # Try different possible project structures
    possible_paths = [
        Path.cwd().parent,  # dashboard/ in project root
        Path.cwd(),         # Running from project root
        Path.cwd().parent.parent  # Nested structure
    ]
    
    data = {}
    data_processed_path = None
    
    # Find the data directory
    for base_path in possible_paths:
        test_path = base_path / "data" / "processed"
        if test_path.exists():
            data_processed_path = test_path
            break
    
    if data_processed_path is None:
        st.sidebar.error("❌ Could not find data/processed directory")
        return data, False
    
    try:
        # 1. Load baseline forecasts
        baseline_path = data_processed_path / "baseline_forecasts_summary.csv"
        if baseline_path.exists():
            data['baseline'] = pd.read_csv(baseline_path)
            st.sidebar.success(f"✅ Loaded baseline forecasts")
        
        # 2. Load event-augmented forecasts
        augmented_path = data_processed_path / "event_augmented_forecasts.csv"
        if augmented_path.exists():
            data['augmented'] = pd.read_csv(augmented_path)
            st.sidebar.success(f"✅ Loaded event-augmented forecasts")
        
        # 3. Load scenario comparison
        scenario_path = data_processed_path / "scenario_forecasts_comparison.csv"
        if scenario_path.exists():
            data['scenarios'] = pd.read_csv(scenario_path)
            st.sidebar.success(f"✅ Loaded scenario forecasts")
        
        # 4. Load final forecast table
        final_forecast_path = data_processed_path / "final_forecast_table.csv"
        if final_forecast_path.exists():
            data['forecasts'] = pd.read_csv(final_forecast_path)
            st.sidebar.success(f"✅ Loaded final forecasts")
        
        # 5. Load scenario comparison for 2027
        comparison_path = data_processed_path / "scenario_comparison_2027.csv"
        if comparison_path.exists():
            data['comparison_2027'] = pd.read_csv(comparison_path)
            st.sidebar.success(f"✅ Loaded 2027 comparison")
        
        # 6. Load historical data (if available)
        historical_path = data_processed_path / "enriched_main_data.csv"
        if historical_path.exists():
            historical_df = pd.read_csv(historical_path)
            # Filter for observations only
            if 'record_type' in historical_df.columns:
                data['historical'] = historical_df[historical_df['record_type'] == 'observation'].copy()
                st.sidebar.success(f"✅ Loaded historical data")
        
        # 7. Load events data
        events_path = data_processed_path / "event_indicator_matrix_refined.csv"
        if events_path.exists():
            data['events'] = pd.read_csv(events_path, index_col=0)
            st.sidebar.success(f"✅ Loaded events matrix")
        
        # 8. Load executive summary
        summary_path = data_processed_path / "forecasting_executive_summary.txt"
        if summary_path.exists():
            with open(summary_path, 'r', encoding='utf-8') as f:
                data['executive_summary'] = f.read()
            st.sidebar.success(f"✅ Loaded executive summary")
        
        # 9. Load final report
        report_path = data_processed_path / "final_forecasting_report.json"
        if report_path.exists():
            with open(report_path, 'r') as f:
                data['report'] = json.load(f)
            st.sidebar.success(f"✅ Loaded final report")
        
        data_loaded = len(data) > 0
        return data, data_loaded
            
    except Exception as e:
        st.sidebar.error(f"❌ Error loading data: {str(e)}")
        return data, False

# Load data
data, data_loaded = load_data()

# Main content based on selected page
if page == "📊 Overview":
    st.header("Overview Dashboard")
    
    if data_loaded:
        # Create metrics columns
        col1, col2, col3, col4 = st.columns(4)
        
        # Helper function to extract forecast values safely
        def get_forecast_value(indicator, year):
            if 'forecasts' in data:
                try:
                    value = data['forecasts'][
                        (data['forecasts']['Indicator'] == indicator) & 
                        (data['forecasts']['Year'] == year)
                    ]['Forecast_%'].values[0]
                    return float(value.replace('%', ''))
                except:
                    return None
            return None
        
        with col1:
            # Current account ownership (from document)
            current_acc = 49.0  # 2024 value from document
            st.metric(
                label="Current Account Ownership (2024)",
                value=f"{current_acc:.1f}%",
                delta="+3pp since 2021"
            )
        
        with col2:
            # 2027 forecast
            acc_2027 = get_forecast_value('ACC_OWNERSHIP', 2027)
            if acc_2027 is not None:
                st.metric(
                    label="2027 Forecast (Base)",
                    value=f"{acc_2027:.1f}%",
                    delta=f"vs 2024: +{acc_2027 - 49:.1f}pp"
                )
            else:
                st.metric(
                    label="2027 Forecast (Base)",
                    value="Loading...",
                    delta="Data required"
                )
        
        with col3:
            # Target gap
            target_2030 = 70.0  # NFIS-II target
            acc_2027 = get_forecast_value('ACC_OWNERSHIP', 2027)
            if acc_2027 is not None:
                gap = target_2030 - acc_2027
                st.metric(
                    label="Gap to 2030 Target",
                    value=f"{gap:.1f}pp",
                    delta="Remaining"
                )
            else:
                st.metric(
                    label="Gap to 2030 Target",
                    value="--",
                    delta="Data required"
                )
        
        with col4:
            # Scenario range
            if 'comparison_2027' in data:
                try:
                    row = data['comparison_2027'][
                        data['comparison_2027']['Indicator'] == 'ACC_OWNERSHIP'
                    ].iloc[0]
                    if 'Range_pp' in row and pd.notna(row['Range_pp']):
                        st.metric(
                            label="Scenario Range (2027)",
                            value=f"{row['Range_pp']}pp",
                            delta="Optimistic vs Pessimistic"
                        )
                    else:
                        st.metric(
                            label="Scenario Range (2027)",
                            value="--",
                            delta="Data required"
                        )
                except:
                    st.metric(
                        label="Scenario Range (2027)",
                        value="--",
                        delta="Data required"
                    )
            else:
                st.metric(
                    label="Scenario Range (2027)",
                    value="--",
                    delta="Data required"
                )
        
        # Executive summary section
        st.subheader("Executive Summary")
        if 'executive_summary' in data:
            # Display first 500 characters with expander
            with st.expander("View Executive Summary"):
                st.write(data['executive_summary'])
        else:
            st.info("Run Task 4 to generate executive summary")
        
        # Quick insights
        st.subheader("Quick Insights")
        insight_col1, insight_col2 = st.columns(2)
        
        with insight_col1:
            st.info("""
            **📱 Mobile Money Driving Growth**
            - Telebirr: 54M+ users (2021 launch)
            - M-Pesa: 10M+ users (2023 entry)
            - P2P transfers now exceed ATM withdrawals
            """)
        
        with insight_col2:
            st.info("""
            **🎯 Key Challenges**
            - Account ownership grew only +3pp (2021-2024)
            - Gender gap persists (~10pp difference)
            - Rural access remains limited
            """)
        
        # Data availability
        st.subheader("Data Availability")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            datasets_loaded = len([k for k in data.keys() if k not in ['executive_summary', 'report']])
            st.metric("Datasets Loaded", datasets_loaded)
        
        with col2:
            if 'historical' in data:
                historical_points = len(data['historical'])
                st.metric("Historical Data Points", historical_points)
            else:
                st.metric("Historical Data Points", 0)
        
        with col3:
            if 'events' in data:
                event_relationships = data['events'].notna().sum().sum()
                st.metric("Event Relationships", event_relationships)
            else:
                st.metric("Event Relationships", 0)
    
    else:
        st.warning("⚠️ Data not loaded. Please run Task 4 forecasting first.")
        st.info("""
        To load data:
        1. Run Task 4 (04_forecasting_access_usage.ipynb)
        2. Ensure outputs are saved to `data/processed/`
        3. Restart this dashboard
        """)

elif page == "📈 Trends":
    st.header("Historical Trends Analysis")
    st.info("This page will show interactive historical trend charts")
    st.write("Coming soon...")

elif page == "🔮 Forecasts":
    st.header("Forecasts 2025-2027")
    st.info("This page will show forecast visualizations")
    st.write("Coming soon...")

elif page == "🎯 Projections":
    st.header("Inclusion Projections")
    st.info("This page will show progress toward 2030 targets")
    st.write("Coming soon...")

elif page == "📋 About":
    st.header("About this Dashboard")
    
    st.subheader("Project Overview")
    st.write("""
    This dashboard presents forecasts for Ethiopia's financial inclusion indicators,
    focusing on two core dimensions from the World Bank's Global Findex:
    
    1. **Access** - Account Ownership Rate
    2. **Usage** - Digital Payment Adoption Rate
    
    The forecasts incorporate event impacts from:
    - Telebirr launch (2021)
    - M-Pesa market entry (2023)
    - Digital ID (Fayda) rollout
    - NFIS-II policy implementation
    - Infrastructure investments
    """)
    
    st.subheader("Methodology")
    st.write("""
    **Forecasting Approach:**
    - Baseline trend projection (linear regression)
    - Event-augmented modeling (impact matrix from Task 3)
    - Scenario analysis (Optimistic/Base/Pessimistic)
    
    **Data Sources:**
    - Global Findex Database (2011-2024)
    - National Bank of Ethiopia reports
    - EthSwitch transaction data
    - Telebirr and M-Pesa user statistics
    - Policy documents and regulatory announcements
    """)
    
    st.subheader("Technical Details")
    st.code("""
    Framework: Streamlit
    Visualization: Plotly, Matplotlib
    Forecasting: scikit-learn, statsmodels
    Data Processing: pandas, numpy
    """)
    
    st.subheader("Team")
    st.write("""
    - **Selam Analytics** - Financial technology consulting
    - **Development Partners** - Consortium of stakeholders
    - **National Bank of Ethiopia** - Regulatory guidance
    """)

# Footer
st.divider()
st.caption("""
Developed by Selam Analytics | Data Sources: Global Findex, NBE, EthSwitch, Telebirr, M-Pesa | 
Last Updated: February 2026
""")