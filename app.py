"""
app.py
Description: Streamlit dashboard for Telecom Customer Churn Analysis.
Includes KPIs, interactive Plotly visualizations of risk drivers, and a Churn Risk Calculator.
"""

import os
import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------------------
# 1. Page Configuration & Custom CSS
# -------------------------------------------------------------
st.set_page_config(
    page_title="Telecom Churn Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom styling for a clean, premium look
st.markdown("""
<style>
    .main {
        background-color: #0f1115;
        color: #e6e8eb;
    }
    .stMetric {
        background-color: #1b1e24;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #2d3139;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }
    [data-testid="stMetricLabel"] {
        color: #a0aec0 !important;
    }
    .stAlert {
        border-radius: 8px;
    }
    div[data-testid="stSidebar"] {
        background-color: #15181e;
        border-right: 1px solid #2d3139;
    }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. Data Loading Function
# -------------------------------------------------------------
@st.cache_data
def load_data():
    db_path = os.path.join("data", "churn_analysis.db")
    if not os.path.exists(db_path):
        # Auto-initialize database if not present (helpful for serverless deploys like Streamlit Cloud)
        st.info("SQLite Database not found. Auto-running the data pipeline to initialize the database...")
        
        # Ensure directories exist
        os.makedirs(os.path.join("data", "raw"), exist_ok=True)
        os.makedirs(os.path.join("data", "processed"), exist_ok=True)
        
        try:
            import sys
            # Add both the script's directory and its parent directory to python path
            # to make sure we find 'scripts/' regardless of whether app.py is run
            # from the root folder or from the 'dashboard/' subfolder
            current_dir = os.path.abspath(os.path.dirname(__file__))
            parent_dir = os.path.abspath(os.path.join(current_dir, ".."))
            
            if current_dir not in sys.path:
                sys.path.append(current_dir)
            if parent_dir not in sys.path:
                sys.path.append(parent_dir)
                
            from scripts.download_data import download_dataset
            from scripts.clean_data import clean_dataset
            from scripts.import_data import import_to_sqlite
            
            with st.spinner("Initializing database (Downloading raw data)..."):
                download_dataset()
            with st.spinner("Initializing database (Cleaning data)..."):
                clean_dataset()
            with st.spinner("Initializing database (Importing to SQLite)..."):
                import_to_sqlite()
                
            st.success("Database initialized successfully!")
        except Exception as init_err:
            st.error(f"Failed to auto-initialize SQLite database: {init_err}")
            st.stop()
    
    conn = sqlite3.connect(db_path)
    # Load entire dataset
    df = pd.read_sql_query("SELECT * FROM customer_churn", conn)
    conn.close()
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# -------------------------------------------------------------
# 3. Sidebar: Title & Churn Risk Calculator
# -------------------------------------------------------------
st.sidebar.markdown("<h2 style='text-align: center; color: #4A90E2;'>Telecom MNC</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<h3 style='text-align: center; margin-top: -15px;'>Retention Center</h3>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.subheader("🔮 Churn Risk Calculator")
st.sidebar.write("Input customer attributes to calculate their estimated probability of churn.")

# Inputs for Churn Calculator
tenure_input = st.sidebar.slider("Tenure (Months)", min_value=0, max_value=72, value=12, step=1)
contract_input = st.sidebar.selectbox("Contract Type", ["Month-to-month", "One year", "Two year"])
internet_input = st.sidebar.selectbox("Internet Service", ["Fiber optic", "DSL", "No"])
tech_support_input = st.sidebar.selectbox("Tech Support Subscriber", ["Yes", "No"])
payment_input = st.sidebar.selectbox("Payment Method", ["Electronic check", "Mailed check", "Bank transfer (automatic)", "Credit card (automatic)"])
monthly_charges_input = st.sidebar.slider("Monthly Charges ($)", min_value=18.0, max_value=120.0, value=70.0, step=1.0)

# Calculate Risk based on SQL insights weights
def calculate_churn_risk(tenure, contract, internet, tech_support, payment, monthly_charges):
    # Base probability is the general churn rate (26.54%)
    prob = 0.2654
    
    # Contract Type Impact
    if contract == "Month-to-month":
        prob += 0.20
    elif contract == "Two year":
        prob -= 0.15
    elif contract == "One year":
        prob -= 0.08
        
    # Payment Method Impact
    if payment == "Electronic check":
        prob += 0.12
    else:
        prob -= 0.05
        
    # Internet Service Type Impact
    if internet == "Fiber optic":
        prob += 0.12
    elif internet == "No":
        prob -= 0.10
        
    # Tech Support Impact
    if internet != "No":
        if tech_support == "No":
            prob += 0.10
        elif tech_support == "Yes":
            prob -= 0.10
            
    # Tenure Impact
    if tenure <= 6:
        prob += 0.20
    elif tenure <= 12:
        prob += 0.10
    elif tenure > 60:
        prob -= 0.15
    elif tenure > 36:
        prob -= 0.08
        
    # Monthly Charges Impact
    if monthly_charges > 75:
        prob += 0.08
    elif monthly_charges < 45:
        prob -= 0.08
        
    # Cap between 1% and 99%
    prob = max(0.01, min(0.99, prob))
    return prob

prob_val = calculate_churn_risk(
    tenure_input, contract_input, internet_input, 
    tech_support_input, payment_input, monthly_charges_input
)

# Render Gauge Chart / Risk Metric in Sidebar
if prob_val >= 0.50:
    risk_color = "red"
    risk_label = "HIGH RISK"
    alert_func = st.sidebar.error
elif prob_val >= 0.25:
    risk_color = "orange"
    risk_label = "MEDIUM RISK"
    alert_func = st.sidebar.warning
else:
    risk_color = "green"
    risk_label = "LOW RISK"
    alert_func = st.sidebar.success

st.sidebar.markdown(f"<h3 style='text-align: center; color: {risk_color};'>{risk_label} ({prob_val*100:.1f}%)</h3>", unsafe_allow_html=True)
alert_func(f"Customer has a {prob_val*100:.1f}% chance of churning.")

st.sidebar.markdown("---")
st.sidebar.markdown("Designed for Portfolio Presentation")

# -------------------------------------------------------------
# 4. Main Panel: Header & Tabs
# -------------------------------------------------------------
st.title("📊 Customer Churn Analysis Dashboard")
st.markdown("Analysis of Retention and Revenue Leakage for an MNC Telecom Provider.")
st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📈 Executive Summary", "🔍 Churn Drivers", "📋 Customer Explorer"])

# -------------------------------------------------------------
# Tab 1: Executive Summary
# -------------------------------------------------------------
with tab1:
    st.subheader("Key Portfolio Indicators")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_cust = len(df)
    churn_yes = len(df[df['churn'] == 'Yes'])
    churn_rate = (churn_yes / total_cust) * 100
    
    total_rev = df['monthly_charges'].sum()
    lost_rev = df[df['churn'] == 'Yes']['monthly_charges'].sum()
    lost_rev_pct = (lost_rev / total_rev) * 100
    
    col1.metric("Total Customers", f"{total_cust:,}", help="Total customers in database")
    col2.metric("Churn Rate", f"{churn_rate:.2f}%", help="Percentage of customer headcount lost")
    col3.metric("Total Monthly Charges", f"${total_rev:,.2f}", help="Total potential monthly recurring revenue")
    col4.metric("Lost Monthly Revenue", f"${lost_rev:,.2f}", f"-{lost_rev_pct:.1f}% Revenue Leak", delta_color="inverse")
    
    st.markdown("---")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Churn Rate by Tenure Cohort")
        # Define Cohorts
        cohorts = []
        for tenure in df['tenure']:
            if tenure <= 6: cohorts.append('0-6 Months')
            elif tenure <= 12: cohorts.append('7-12 Months')
            elif tenure <= 24: cohorts.append('1-2 Years')
            elif tenure <= 36: cohorts.append('2-3 Years')
            elif tenure <= 48: cohorts.append('3-4 Years')
            elif tenure <= 60: cohorts.append('4-5 Years')
            else: cohorts.append('5+ Years')
        
        df_cohort = df.copy()
        df_cohort['tenure_cohort'] = cohorts
        
        cohort_summary = df_cohort.groupby('tenure_cohort').agg(
            total=('churn', 'count'),
            churned=('churn', lambda x: (x == 'Yes').sum())
        ).reset_index()
        cohort_summary['churn_rate'] = (cohort_summary['churned'] / cohort_summary['total']) * 100
        
        fig_cohort = px.bar(
            cohort_summary,
            x='tenure_cohort',
            y='churn_rate',
            text=cohort_summary['churn_rate'].apply(lambda x: f"{x:.1f}%"),
            labels={'tenure_cohort': 'Tenure Cohort', 'churn_rate': 'Churn Rate (%)'},
            color='churn_rate',
            color_continuous_scale='Reds'
        )
        fig_cohort.update_layout(showlegend=False, template="plotly_dark", height=400)
        st.plotly_chart(fig_cohort, use_container_width=True)
        st.caption("Observation: Churn drops off dramatically after the 6-month onboarding window.")
        
    with col_right:
        st.subheader("Average Monthly Charges: Active vs. Churned")
        # Charges distribution box plot
        fig_charges = px.box(
            df,
            x='churn',
            y='monthly_charges',
            color='churn',
            color_discrete_map={'No': '#4A90E2', 'Yes': '#E24A4A'},
            labels={'churn': 'Churned Status', 'monthly_charges': 'Monthly Charges ($)'}
        )
        fig_charges.update_layout(template="plotly_dark", height=400)
        st.plotly_chart(fig_charges, use_container_width=True)
        st.caption("Observation: Customers who churn have a higher median monthly fee ($79.60) vs active customers ($64.40).")

# -------------------------------------------------------------
# Tab 2: Churn Drivers
# -------------------------------------------------------------
with tab2:
    st.subheader("Analysis of Core Churn Factors")
    
    col2_left, col2_right = st.columns(2)
    
    with col2_left:
        st.subheader("Churn Rate by Contract Type")
        contract_summary = df.groupby('contract').agg(
            total=('churn', 'count'),
            churned=('churn', lambda x: (x == 'Yes').sum())
        ).reset_index()
        contract_summary['churn_rate'] = (contract_summary['churned'] / contract_summary['total']) * 100
        
        fig_contract = px.bar(
            contract_summary,
            x='contract',
            y='churn_rate',
            text=contract_summary['churn_rate'].apply(lambda x: f"{x:.1f}%"),
            color='contract',
            color_discrete_sequence=['#E24A4A', '#F5A623', '#4A90E2'],
            labels={'contract': 'Contract Type', 'churn_rate': 'Churn Rate (%)'}
        )
        fig_contract.update_layout(showlegend=False, template="plotly_dark", height=380)
        st.plotly_chart(fig_contract, use_container_width=True)
        
    with col2_right:
        st.subheader("Churn Rate by Internet Service Type")
        internet_summary = df.groupby('internet_service').agg(
            total=('churn', 'count'),
            churned=('churn', lambda x: (x == 'Yes').sum())
        ).reset_index()
        internet_summary['churn_rate'] = (internet_summary['churned'] / internet_summary['total']) * 100
        
        fig_internet = px.bar(
            internet_summary,
            x='internet_service',
            y='churn_rate',
            text=internet_summary['churn_rate'].apply(lambda x: f"{x:.1f}%"),
            color='internet_service',
            color_discrete_sequence=['#E24A4A', '#4A90E2', '#50E3C2'],
            labels={'internet_service': 'Internet Service', 'churn_rate': 'Churn Rate (%)'}
        )
        fig_internet.update_layout(showlegend=False, template="plotly_dark", height=380)
        st.plotly_chart(fig_internet, use_container_width=True)
        
    st.markdown("---")
    
    col3_left, col3_right = st.columns(2)
    
    with col3_left:
        st.subheader("Tech Support Subscription vs. Churn Rate")
        # Filter to Internet Users
        df_net = df[df['internet_service'] != 'No']
        support_summary = df_net.groupby('tech_support').agg(
            total=('churn', 'count'),
            churned=('churn', lambda x: (x == 'Yes').sum())
        ).reset_index()
        support_summary['churn_rate'] = (support_summary['churned'] / support_summary['total']) * 100
        
        fig_support = px.bar(
            support_summary,
            x='tech_support',
            y='churn_rate',
            text=support_summary['churn_rate'].apply(lambda x: f"{x:.1f}%"),
            color='tech_support',
            color_discrete_map={'No': '#E24A4A', 'Yes': '#4A90E2'},
            labels={'tech_support': 'Has Tech Support', 'churn_rate': 'Churn Rate (%)'}
        )
        fig_support.update_layout(showlegend=False, template="plotly_dark", height=380)
        st.plotly_chart(fig_support, use_container_width=True)
        st.caption("Focus on customer success: Adding tech support reduces churn probability by over 60%.")
        
    with col3_right:
        st.subheader("Churn Rate by Payment Method")
        payment_summary = df.groupby('payment_method').agg(
            total=('churn', 'count'),
            churned=('churn', lambda x: (x == 'Yes').sum())
        ).reset_index()
        payment_summary['churn_rate'] = (payment_summary['churned'] / payment_summary['total']) * 100
        
        fig_payment = px.bar(
            payment_summary,
            y='payment_method',
            x='churn_rate',
            orientation='h',
            text=payment_summary['churn_rate'].apply(lambda x: f"{x:.1f}%"),
            color='churn_rate',
            color_continuous_scale='Reds',
            labels={'payment_method': 'Payment Method', 'churn_rate': 'Churn Rate (%)'}
        )
        fig_payment.update_layout(showlegend=False, template="plotly_dark", height=380)
        st.plotly_chart(fig_payment, use_container_width=True)
        st.caption("Friction point: Electronic checks churn at 45.3%, while automated payments hover around 15%.")

# -------------------------------------------------------------
# Tab 3: Customer Explorer
# -------------------------------------------------------------
with tab3:
    st.subheader("Database Search & Export")
    st.markdown("Search for individual customers in the database and download the segmented list.")
    
    # Simple search bar
    search_id = st.text_input("Search Customer by ID (e.g., 7590-VHVEG, 5575-GNVDE):", "").strip()
    
    if search_id:
        cust_record = df[df['customer_id'].str.lower() == search_id.lower()]
        if not cust_record.empty:
            st.success(f"Customer {search_id} found!")
            
            # Display vertical list of traits
            cols = st.columns(2)
            with cols[0]:
                st.write("**Account Info**")
                st.write(f"- Contract: {cust_record['contract'].values[0]}")
                st.write(f"- Tenure: {cust_record['tenure'].values[0]} months")
                st.write(f"- Monthly Charges: ${cust_record['monthly_charges'].values[0]:.2f}")
                st.write(f"- Total Charges: ${cust_record['total_charges'].values[0]:.2f}")
                st.write(f"- Churned: {cust_record['churn'].values[0]}")
            with cols[1]:
                st.write("**Services**")
                st.write(f"- Internet: {cust_record['internet_service'].values[0]}")
                st.write(f"- Tech Support: {cust_record['tech_support'].values[0]}")
                st.write(f"- Phone Service: {cust_record['phone_service'].values[0]}")
                st.write(f"- Payment Method: {cust_record['payment_method'].values[0]}")
        else:
            st.error(f"Customer {search_id} not found in database.")
            
    st.markdown("---")
    st.subheader("Filter Churned List for Marketing Campaigns")
    
    filter_contract = st.multiselect("Select Contract Type(s):", df['contract'].unique(), default=list(df['contract'].unique()))
    filter_service = st.multiselect("Select Internet Service(s):", df['internet_service'].unique(), default=list(df['internet_service'].unique()))
    
    filtered_df = df[
        (df['contract'].isin(filter_contract)) &
        (df['internet_service'].isin(filter_service)) &
        (df['churn'] == 'Yes')
    ]
    
    st.write(f"Showing {len(filtered_df)} churned customers matching filters.")
    st.dataframe(filtered_df[['customer_id', 'contract', 'tenure', 'internet_service', 'monthly_charges', 'payment_method']].head(100))
    
    # Download button
    csv_data = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Cleaned Churn List CSV",
        data=csv_data,
        file_name="churned_customers_campaign.csv",
        mime="text/csv"
    )
