#!/usr/bin/env python3
"""
Enhanced Streamlit Demo: Multi-Dataset Women's Health MCP
Interactive web interface with multiple SWAN visits and longitudinal analysis
"""

import streamlit as st
import asyncio
import json
import sys
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path
from typing import Dict, Any
import time

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from demos.mcp_server.mcp_protocol import MCPServer
from core.multi_dataset_integration import multi_dataset_integration

# Page configuration
st.set_page_config(
    page_title="Enhanced Women's Health MCP Demo",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .dataset-card {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4169e1;
        margin: 0.5rem 0;
    }
    .longitudinal-card {
        background-color: #f5f5dc;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #daa520;
        margin: 0.5rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .warning-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffc107;
    }
    .info-box {
        background-color: #d1ecf1;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #17a2b8;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def initialize_mcp_server():
    """Initialize the MCP server - cached for performance."""
    return MCPServer()

@st.cache_data
def get_datasets_overview():
    """Get overview of all available datasets - cached."""
    return multi_dataset_integration.get_datasets_overview()

async def call_mcp_tool(server: MCPServer, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Call an MCP tool and return the result."""
    request = {
        'name': tool_name,
        'arguments': arguments
    }
    
    response = await server._handle_call_tool(f'{tool_name}_call', request)
    
    if 'error' in response:
        return {'error': response['error']}
    
    try:
        result = json.loads(response['result']['content'][0]['text'])
        return result
    except:
        return {'error': 'Failed to parse response'}

def main():
    """Main enhanced Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">🌊 Enhanced Women\'s Health MCP Demo</h1>', unsafe_allow_html=True)
    st.markdown("**Multi-Dataset SWAN Integration + Model Context Protocol + Longitudinal Analysis**")
    
    # Initialize MCP server
    mcp_server = initialize_mcp_server()
    
    # Sidebar for navigation
    st.sidebar.title("🔧 Enhanced Demo Navigation")
    demo_mode = st.sidebar.selectbox(
        "Choose Demo Mode:",
        [
            "📊 Multi-Dataset Overview",
            "📈 Longitudinal Analysis", 
            "🔬 Cross-Visit Variable Tracking",
            "🧮 Enhanced Clinical Calculator",
            "🤖 Multi-Visit AI Consultation",
            "📋 Population Demographics",
            "🔍 Advanced Variable Search",
            "⏰ Temporal Trends Analysis"
        ]
    )
    
    # Multi-Dataset Status
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🌊 Multi-Dataset Status")
    
    datasets_overview = get_datasets_overview()
    st.sidebar.success(f"✅ {datasets_overview['loaded_datasets']}/{datasets_overview['total_datasets']} datasets loaded")
    
    if datasets_overview.get('total_participants'):
        st.sidebar.info(f"👥 Total: {datasets_overview['total_participants']:,} participants")
        st.sidebar.info(f"📊 Variables: {datasets_overview['total_variables']:,}")
        st.sidebar.info(f"📅 Range: {datasets_overview.get('date_range', 'Multiple periods')}")
    
    # Show loaded datasets
    if datasets_overview['loaded_datasets'] > 0:
        st.sidebar.markdown("### 📋 Loaded Datasets")
        for dataset_id, info in datasets_overview['datasets'].items():
            if info['loaded']:
                st.sidebar.write(f"✅ {info['visit']} ({info['period']})")
    
    # Main content based on selected mode
    if demo_mode == "📊 Multi-Dataset Overview":
        show_multi_dataset_overview()
    elif demo_mode == "📈 Longitudinal Analysis":
        show_longitudinal_analysis()
    elif demo_mode == "🔬 Cross-Visit Variable Tracking":
        show_cross_visit_tracking()
    elif demo_mode == "🧮 Enhanced Clinical Calculator":
        show_enhanced_clinical_calculator(mcp_server)
    elif demo_mode == "🤖 Multi-Visit AI Consultation":
        show_multi_visit_consultation(mcp_server)
    elif demo_mode == "📋 Population Demographics":
        show_population_demographics()
    elif demo_mode == "🔍 Advanced Variable Search":
        show_advanced_variable_search()
    elif demo_mode == "⏰ Temporal Trends Analysis":
        show_temporal_trends()

def show_multi_dataset_overview():
    """Show overview of all available SWAN datasets."""
    
    st.header("📊 Multi-Dataset Overview")
    st.markdown("Comprehensive view of all available SWAN study visits")
    
    datasets_overview = get_datasets_overview()
    
    # Overall statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Total Datasets", f"{datasets_overview['loaded_datasets']}/{datasets_overview['total_datasets']}")
    
    with col2:
        if datasets_overview.get('total_participants'):
            st.metric("👥 Total Participants", f"{datasets_overview['total_participants']:,}")
    
    with col3:
        if datasets_overview.get('total_variables'):
            st.metric("📊 Total Variables", f"{datasets_overview['total_variables']:,}")
    
    with col4:
        if datasets_overview.get('date_range'):
            st.metric("📅 Study Period", datasets_overview['date_range'])
    
    # Dataset details
    st.subheader("📋 Dataset Details")
    
    datasets_data = []
    for dataset_id, info in datasets_overview['datasets'].items():
        datasets_data.append({
            'Dataset ID': dataset_id,
            'Visit': info['visit'],
            'Period': info['period'],
            'Status': '✅ Loaded' if info['loaded'] else '❌ Not Loaded',
            'Participants': f"{info['participants']:,}" if info['loaded'] else 'N/A',
            'Variables': f"{info['variables']:,}" if info['loaded'] else 'N/A',
            'Description': info['description']
        })
    
    datasets_df = pd.DataFrame(datasets_data)
    st.dataframe(datasets_df, width='stretch')
    
    # Timeline visualization
    st.subheader("📅 SWAN Study Timeline")
    
    loaded_datasets = [(k, v) for k, v in datasets_overview['datasets'].items() if v['loaded']]
    if loaded_datasets:
        # Create timeline chart
        timeline_data = []
        for dataset_id, info in loaded_datasets:
            start_year = int(info['period'].split('-')[0])
            end_year = int(info['period'].split('-')[1])
            timeline_data.append({
                'Visit': info['visit'],
                'Start': start_year,
                'End': end_year,
                'Duration': end_year - start_year,
                'Participants': info['participants'],
                'Dataset': dataset_id
            })
        
        timeline_df = pd.DataFrame(timeline_data)
        
        # Create Gantt-style chart
        fig = px.timeline(
            timeline_df,
            x_start='Start',
            x_end='End', 
            y='Visit',
            color='Participants',
            title="SWAN Study Visits Timeline",
            labels={'Start': 'Year', 'End': 'Year'}
        )
        
        fig.update_layout(height=400)
        st.plotly_chart(fig, width='stretch')
    
    # Sample size comparison
    st.subheader("👥 Sample Size Comparison")
    
    if loaded_datasets:
        sample_data = []
        for dataset_id, info in loaded_datasets:
            sample_data.append({
                'Visit': info['visit'],
                'Participants': info['participants'],
                'Variables': info['variables']
            })
        
        sample_df = pd.DataFrame(sample_data)
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = px.bar(
                sample_df,
                x='Visit',
                y='Participants',
                title="Participants by Visit",
                color='Participants',
                color_continuous_scale='Blues'
            )
            st.plotly_chart(fig, width='stretch')
        
        with col2:
            fig = px.bar(
                sample_df,
                x='Visit', 
                y='Variables',
                title="Variables by Visit",
                color='Variables',
                color_continuous_scale='Greens'
            )
            st.plotly_chart(fig, width='stretch')

def show_longitudinal_analysis():
    """Show longitudinal analysis across multiple SWAN visits."""
    
    st.header("📈 Longitudinal Analysis")
    st.markdown("Analyze trends across multiple SWAN study visits")
    
    # Analysis parameters
    st.subheader("🔍 Analysis Parameters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        condition = st.selectbox(
            "Analysis Focus:",
            ["menopause progression", "hormone trajectories", "population demographics"]
        )
        
        include_age_filter = st.checkbox("Apply age filter")
        
        if include_age_filter:
            age_range = st.slider("Age Range", 40, 70, (45, 55))
        else:
            age_range = None
    
    with col2:
        st.markdown("**Available for Analysis:**")
        datasets_overview = get_datasets_overview()
        loaded_count = datasets_overview['loaded_datasets']
        st.info(f"📊 {loaded_count} SWAN visits loaded")
        st.info(f"📅 Study period: {datasets_overview.get('date_range', 'Multiple periods')}")
    
    if st.button("📈 Run Longitudinal Analysis", type="primary"):
        
        with st.spinner("Analyzing longitudinal trends across SWAN visits..."):
            
            # Get longitudinal analysis
            analysis = multi_dataset_integration.get_longitudinal_analysis(condition, age_range)
            
            if 'error' not in analysis:
                
                st.subheader("📊 Analysis Results")
                
                # Summary metrics
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("🔬 Visits Analyzed", analysis['visits_analyzed'])
                
                with col2:
                    total_sample = sum(data['sample_size'] for data in analysis['longitudinal_data'].values())
                    st.metric("👥 Total Sample Size", f"{total_sample:,}")
                
                with col3:
                    date_range = analysis['summary']['date_range']
                    st.metric("📅 Study Period", date_range)
                
                # Detailed results by visit
                st.subheader("📋 Results by Visit")
                
                for dataset_id, data in analysis['longitudinal_data'].items():
                    
                    with st.expander(f"{data['visit']} ({data['period']}) - {data['sample_size']:,} participants"):
                        
                        analysis_data = data['analysis']
                        
                        if condition == "menopause progression":
                            
                            if 'age_stats' in analysis_data:
                                age_stats = analysis_data['age_stats']
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Mean Age", f"{age_stats['mean']:.1f}")
                                with col2:
                                    st.metric("Median Age", f"{age_stats['median']:.1f}")
                                with col3:
                                    st.metric("Age Range", f"{age_stats['range'][0]:.0f}-{age_stats['range'][1]:.0f}")
                            
                            if 'ethnicity_distribution' in analysis_data:
                                st.write("**Ethnicity Distribution:**")
                                ethnicity_data = analysis_data['ethnicity_distribution']
                                for ethnicity, count in ethnicity_data.items():
                                    st.write(f"• {ethnicity.replace('_', ' ').title()}: {count:,}")
                        
                        elif condition == "hormone trajectories":
                            
                            if 'hormone_variables' in analysis_data:
                                st.write(f"**Hormone Variables Available:** {analysis_data['hormone_variables']['total_count']}")
                                
                                if 'hormone_statistics' in analysis_data:
                                    hormone_stats = analysis_data['hormone_statistics']
                                    
                                    for var, stats in hormone_stats.items():
                                        st.write(f"**{var}:**")
                                        st.write(f"  - Valid measurements: {stats['n_valid']:,}")
                                        st.write(f"  - Mean: {stats['mean']:.3f}")
                                        st.write(f"  - Median: {stats['median']:.3f}")
                        
                        elif condition == "population demographics":
                            
                            if 'age_distribution' in analysis_data:
                                age_dist = analysis_data['age_distribution']
                                st.write(f"**Mean Age:** {age_dist['mean']:.1f}")
                                
                                by_decade = age_dist['by_decade']
                                st.write("**Age Distribution:**")
                                for decade, count in by_decade.items():
                                    st.write(f"  - {decade}: {count:,}")
                
                # Longitudinal trends visualization
                st.subheader("📈 Longitudinal Trends")
                
                if condition == "menopause progression" and len(analysis['longitudinal_data']) > 1:
                    
                    # Extract age trends across visits
                    visit_data = []
                    for dataset_id, data in analysis['longitudinal_data'].items():
                        if 'age_stats' in data['analysis']:
                            visit_data.append({
                                'Visit': data['visit'],
                                'Period': data['period'].split('-')[0],  # Start year
                                'Mean_Age': data['analysis']['age_stats']['mean'],
                                'Sample_Size': data['sample_size']
                            })
                    
                    if visit_data:
                        trends_df = pd.DataFrame(visit_data)
                        trends_df = trends_df.sort_values('Period')
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            fig = px.line(
                                trends_df,
                                x='Period',
                                y='Mean_Age',
                                markers=True,
                                title="Mean Age Across Visits"
                            )
                            st.plotly_chart(fig, width='stretch')
                        
                        with col2:
                            fig = px.bar(
                                trends_df,
                                x='Visit',
                                y='Sample_Size',
                                title="Sample Size by Visit"
                            )
                            st.plotly_chart(fig, width='stretch')
            
            else:
                st.error("Error running longitudinal analysis")

def show_cross_visit_tracking():
    """Show cross-visit variable tracking."""
    
    st.header("🔬 Cross-Visit Variable Tracking")
    st.markdown("Track specific variables across multiple SWAN visits")
    
    # Variable selection
    st.subheader("🔍 Variable Selection")
    
    col1, col2 = st.columns(2)
    
    with col1:
        variable_categories = {
            "Estrogen": "ESTR",
            "FSH": "FSH",
            "AMH": "AMH", 
            "Age": "AGE",
            "Menopause": "MENO",
            "Period/Cycle": "PERIOD",
            "Weight/BMI": "WEIGHT",
            "Blood Pressure": "SYSTOL"
        }
        
        selected_category = st.selectbox("Variable Category:", list(variable_categories.keys()))
        variable_pattern = variable_categories[selected_category]
    
    with col2:
        st.markdown("**Cross-Visit Analysis:**")
        st.info("Analyze how variables change across visits")
        st.info("Compare measurements over time")
        st.info("Identify data availability patterns")
    
    if st.button("🔬 Track Variable Across Visits"):
        
        with st.spinner(f"Tracking {selected_category} variables across visits..."):
            
            # Search variables across datasets
            search_results = multi_dataset_integration.search_variables_across_datasets(variable_pattern)
            
            if search_results:
                
                st.subheader(f"📊 {selected_category} Variable Tracking Results")
                
                # Overview
                st.markdown(f"**Found {selected_category.lower()} variables in {len(search_results)} visits**")
                
                # Detailed results by visit
                tracking_data = []
                
                for dataset_id, results in search_results.items():
                    
                    with st.expander(f"{results['visit']} ({results['period']}) - {results['count']} variables"):
                        
                        st.write("**Variables found:**")
                        for var in results['variables'][:10]:  # Show first 10
                            st.write(f"• {var}")
                        
                        if len(results['variables']) > 10:
                            st.write(f"... and {len(results['variables']) - 10} more")
                    
                    # Collect data for visualization
                    tracking_data.append({
                        'Visit': results['visit'],
                        'Period': results['period'].split('-')[0],
                        'Variable_Count': results['count']
                    })
                
                # Visualization
                if len(tracking_data) > 1:
                    st.subheader("📈 Variable Availability Trends")
                    
                    tracking_df = pd.DataFrame(tracking_data)
                    tracking_df = tracking_df.sort_values('Period')
                    
                    fig = px.line(
                        tracking_df,
                        x='Period',
                        y='Variable_Count',
                        markers=True,
                        title=f"{selected_category} Variable Count Across Visits"
                    )
                    
                    st.plotly_chart(fig, width='stretch')
                
                # Cross-visit analysis
                st.subheader("🔍 Detailed Cross-Visit Analysis")
                
                cross_analysis = multi_dataset_integration.get_cross_visit_variable_analysis(variable_pattern)
                
                if cross_analysis['visits_with_data'] > 0:
                    
                    analysis_data = []
                    for dataset_id, data in cross_analysis['cross_visit_analysis'].items():
                        if data['analysis']:
                            for var, stats in data['analysis'].items():
                                analysis_data.append({
                                    'Visit': data['visit'],
                                    'Period': data['period'],
                                    'Variable': var,
                                    'N': stats['n'],
                                    'Mean': stats['mean'],
                                    'Std': stats['std']
                                })
                    
                    if analysis_data:
                        analysis_df = pd.DataFrame(analysis_data)
                        st.dataframe(analysis_df, width='stretch')
                        
                        # Create comparison charts
                        if len(analysis_df) > 1:
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                fig = px.bar(
                                    analysis_df,
                                    x='Visit',
                                    y='N',
                                    color='Variable',
                                    title="Sample Size by Visit and Variable"
                                )
                                st.plotly_chart(fig, width='stretch')
                            
                            with col2:
                                fig = px.line(
                                    analysis_df,
                                    x='Visit',
                                    y='Mean',
                                    color='Variable',
                                    markers=True,
                                    title="Mean Values Across Visits"
                                )
                                st.plotly_chart(fig, width='stretch')
            
            else:
                st.warning(f"No {selected_category.lower()} variables found in loaded datasets")

def show_enhanced_clinical_calculator(mcp_server: MCPServer):
    """Show enhanced clinical calculator with multi-dataset context."""
    
    st.header("🧮 Enhanced Clinical Calculator")
    st.markdown("Evidence-based calculations with multi-visit SWAN population context")
    
    # Input form
    st.subheader("👤 Patient Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        age = st.number_input("Age (years)", min_value=18, max_value=70, value=38, step=1)
        amh = st.number_input("AMH Level (ng/mL)", min_value=0.0, max_value=10.0, value=0.8, step=0.1)
        fsh = st.number_input("FSH Level (mIU/mL) - Optional", min_value=0.0, max_value=50.0, value=12.5, step=0.1)
    
    with col2:
        compare_to_swan = st.checkbox("Compare to SWAN population data", value=True)
        longitudinal_context = st.checkbox("Include longitudinal context", value=True)
        
        datasets_overview = get_datasets_overview()
        st.info(f"📊 {datasets_overview['loaded_datasets']} SWAN visits available")
    
    if st.button("🧮 Enhanced Clinical Assessment", type="primary"):
        
        with st.spinner("Running enhanced clinical calculations with SWAN context..."):
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Step 1: Basic clinical calculations
            status_text.text("🧮 Running clinical calculators...")
            progress_bar.progress(25)
            
            ovarian_result = asyncio.run(call_mcp_tool(mcp_server, 'assess-ovarian-reserve', {
                'age': age, 'amh': amh, 'fsh': fsh
            }))
            
            ivf_result = asyncio.run(call_mcp_tool(mcp_server, 'predict-ivf-success', {
                'age': age, 'amh': amh, 'cycle_type': 'fresh'
            }))
            
            # Step 2: SWAN population context
            if compare_to_swan:
                status_text.text("📊 Gathering SWAN population context...")
                progress_bar.progress(50)
                
                swan_context = multi_dataset_integration.get_longitudinal_analysis(
                    "population demographics", 
                    age_range=(age-5, age+5)
                )
            
            # Step 3: Longitudinal analysis
            if longitudinal_context:
                status_text.text("📈 Analyzing longitudinal trends...")
                progress_bar.progress(75)
                
                longitudinal_data = multi_dataset_integration.get_longitudinal_analysis(
                    "hormone trajectories"
                )
            
            status_text.text("✅ Analysis complete!")
            progress_bar.progress(100)
            time.sleep(1)
            
            # Clear progress indicators
            progress_bar.empty()
            status_text.empty()
        
        # Display enhanced results
        st.subheader("🎯 Enhanced Clinical Assessment Results")
        
        if 'error' not in ovarian_result and 'error' not in ivf_result:
            
            ovarian = ovarian_result['result']
            ivf = ivf_result['result']
            
            # Main clinical results
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="dataset-card">', unsafe_allow_html=True)
                st.markdown("### 🔬 Ovarian Reserve Assessment")
                
                category = ovarian['category'].replace('_', ' ').title()
                percentile = ovarian['percentile']
                
                if category.lower() in ['very_low', 'low']:
                    st.warning(f"**Category:** {category} ({percentile}th percentile)")
                else:
                    st.success(f"**Category:** {category} ({percentile}th percentile)")
                
                st.write(f"**Interpretation:** {ovarian['interpretation']}")
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.markdown('<div class="dataset-card">', unsafe_allow_html=True)
                st.markdown("### 📈 IVF Success Prediction")
                
                success_rate = ivf['live_birth_rate']
                confidence = ivf['confidence_interval']
                
                # Enhanced success rate gauge
                fig = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = success_rate,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Live Birth Rate (%)"},
                    delta = {'reference': 25},
                    gauge = {
                        'axis': {'range': [None, 50]},
                        'bar': {'color': "darkblue"},
                        'steps': [
                            {'range': [0, 15], 'color': "lightgray"},
                            {'range': [15, 25], 'color': "yellow"},
                            {'range': [25, 50], 'color': "green"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 30
                        }
                    }
                ))
                
                fig.update_layout(height=250)
                st.plotly_chart(fig, width='stretch')
                
                st.write(f"**Confidence Interval:** {confidence[0]:.1f}% - {confidence[1]:.1f}%")
                st.markdown('</div>', unsafe_allow_html=True)
            
            # SWAN Population Context
            if compare_to_swan and 'error' not in swan_context:
                st.subheader("📊 SWAN Population Context")
                
                st.markdown('<div class="longitudinal-card">', unsafe_allow_html=True)
                
                visits_analyzed = swan_context['visits_analyzed']
                total_sample = sum(data['sample_size'] for data in swan_context['longitudinal_data'].values())
                
                st.write(f"**Population Comparison:** Your profile compared to {total_sample:,} women across {visits_analyzed} SWAN visits")
                
                # Age context across visits
                age_comparisons = []
                for dataset_id, data in swan_context['longitudinal_data'].items():
                    if 'age_distribution' in data['analysis']:
                        age_dist = data['analysis']['age_distribution']
                        age_comparisons.append({
                            'Visit': data['visit'],
                            'Period': data['period'],
                            'Mean_Age': age_dist['mean'],
                            'Your_Age': age
                        })
                
                if age_comparisons:
                    comp_df = pd.DataFrame(age_comparisons)
                    
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=comp_df['Visit'],
                        y=comp_df['Mean_Age'],
                        mode='lines+markers',
                        name='SWAN Population Mean',
                        line=dict(color='blue')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=comp_df['Visit'],
                        y=comp_df['Your_Age'],
                        mode='lines+markers',
                        name='Your Age',
                        line=dict(color='red', dash='dash')
                    ))
                    
                    fig.update_layout(
                        title="Age Comparison Across SWAN Visits",
                        xaxis_title="Visit",
                        yaxis_title="Age (years)",
                        height=300
                    )
                    
                    st.plotly_chart(fig, width='stretch')
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Longitudinal Context
            if longitudinal_context and 'error' not in longitudinal_data:
                st.subheader("📈 Longitudinal Hormone Context")
                
                st.markdown('<div class="longitudinal-card">', unsafe_allow_html=True)
                
                st.write("**Hormone Variable Trends Across SWAN Visits:**")
                
                # Show hormone availability across visits
                hormone_data = []
                for dataset_id, data in longitudinal_data['longitudinal_data'].items():
                    if 'hormone_variables' in data['analysis']:
                        hormone_data.append({
                            'Visit': data['visit'],
                            'Period': data['period'].split('-')[0],
                            'Hormone_Variables': data['analysis']['hormone_variables']['total_count']
                        })
                
                if hormone_data:
                    hormone_df = pd.DataFrame(hormone_data)
                    
                    fig = px.bar(
                        hormone_df,
                        x='Visit',
                        y='Hormone_Variables',
                        title="Hormone Variables Available by Visit",
                        color='Hormone_Variables',
                        color_continuous_scale='Viridis'
                    )
                    
                    st.plotly_chart(fig, width='stretch')
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Enhanced recommendations
            st.subheader("💡 Enhanced Evidence-Based Recommendations")
            
            urgency = "HIGH" if (ovarian['category'] in ['low', 'very_low'] and ivf['live_birth_rate'] < 25) else "ROUTINE"
            timeline = "1-2 months" if urgency == "HIGH" else "3-6 months"
            
            recommendation = f"""
**CLINICAL ASSESSMENT:**
• **Ovarian Reserve:** {category} ({percentile}th percentile for age {age})
• **IVF Success Rate:** {success_rate:.1f}% per fresh cycle
• **Population Context:** Compared against {datasets_overview.get('total_participants', 'N/A'):,} SWAN participants across {visits_analyzed if compare_to_swan else 'multiple'} visits

**EVIDENCE-BASED RECOMMENDATION:**
{f'URGENT - Schedule fertility consultation within {timeline}.' if urgency == 'HIGH' else f'Schedule consultation within {timeline} for optimal planning.'}

**LONGITUDINAL CONTEXT:**
Your age ({age}) and AMH level ({amh} ng/mL) place you in a {'time-sensitive fertility window' if urgency == 'HIGH' else 'manageable fertility planning period'} based on longitudinal SWAN study data.

**NEXT STEPS:**
1. {'Expedited' if urgency == 'HIGH' else 'Routine'} reproductive endocrinology consultation
2. Additional testing: Antral follicle count, comprehensive metabolic panel
3. Treatment timeline discussion with consideration of age-related decline
4. {'Consider immediate treatment planning' if urgency == 'HIGH' else 'Explore fertility preservation options'}

**ENHANCED EVIDENCE BASIS:**
• **Multi-Visit SWAN Data:** {datasets_overview['loaded_datasets']} longitudinal visits spanning {datasets_overview.get('date_range', 'multiple years')}
• **Population Comparison:** Age-matched cohorts from comprehensive reproductive health study
• **Clinical Guidelines:** ASRM/ESHRE protocols with real-world validation
"""
            
            if urgency == "HIGH":
                st.markdown(f'<div class="warning-box">{recommendation}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="success-box">{recommendation}</div>', unsafe_allow_html=True)
        
        else:
            st.error("Error in clinical calculations")

# Additional demo functions for the new categories would go here...
# For brevity, I'll include the key structure for the remaining functions

def show_multi_visit_consultation(mcp_server: MCPServer):
    """Show multi-visit AI consultation with enhanced SWAN context."""
    st.header("🤖 Multi-Visit AI Consultation")
    st.markdown("Enhanced AI consultation with longitudinal SWAN context")
    # Implementation similar to enhanced_clinical_calculator but focused on AI consultation
    st.info("🚧 Multi-visit AI consultation mode - Enhanced with longitudinal analysis")

def show_population_demographics():
    """Show enhanced population demographics across visits."""
    st.header("📋 Population Demographics")
    st.markdown("Comprehensive demographic analysis across SWAN visits")
    # Implementation for demographic analysis
    st.info("🚧 Population demographics mode - Multi-dataset demographic analysis")

def show_advanced_variable_search():
    """Show advanced variable search across datasets."""
    st.header("🔍 Advanced Variable Search")
    st.markdown("Search and analyze variables across multiple SWAN datasets")
    # Implementation for advanced search
    st.info("🚧 Advanced variable search mode - Cross-dataset variable analysis")

def show_temporal_trends():
    """Show temporal trends analysis."""
    st.header("⏰ Temporal Trends Analysis")
    st.markdown("Analyze how reproductive health metrics change over time")
    # Implementation for temporal analysis
    st.info("🚧 Temporal trends mode - Longitudinal trend analysis")

if __name__ == "__main__":
    main()