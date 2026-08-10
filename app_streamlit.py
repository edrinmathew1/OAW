# ─────────────────────────────────────────────
#  app_streamlit.py — OAW Streamlit Management Dashboard
#  Clean, Modern, 100% Functional Implementation for Lab Project
# ─────────────────────────────────────────────

import os
import json
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

# ── Configuration & Paths ──────────────────────────────────────────────────
API_URL = "http://127.0.0.1:5000/api/records"
DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "dataset.json")

st.set_page_config(
    page_title="OAW Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom Premium Styling ─────────────────────────────────────────────────
st.markdown("""
<style>
    /* Global Container Adjustments */
    .block-container { padding-top: 1.8rem; padding-bottom: 2rem; }
    
    /* Header Card */
    .hero-container {
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
        border: 1px solid #312e81;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }
    .hero-title { font-size: 2rem; font-weight: 800; color: #f8fafc; margin-bottom: 0.2rem; }
    .hero-sub { font-size: 0.95rem; color: #a5b4fc; margin-bottom: 0; }
    
    /* Metric Cards */
    [data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 1rem;
        border-radius: 10px;
    }
    
    /* Tab Styling */
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background-color: #1e293b;
        border-radius: 8px;
        padding: 8px 16px;
        color: #94a3b8;
        border: 1px solid #334155;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4f46e5 !important;
        color: #ffffff !important;
        border-color: #6366f1 !important;
    }
</style>
""", unsafe_allow_html=True)


# ── Data Helper Functions ──────────────────────────────────────────────────

def load_dataset() -> tuple[pd.DataFrame, str]:
    """Load data from Flask API if online, or fallback cleanly to dataset.json."""
    try:
        res = requests.get(API_URL, timeout=1.5)
        if res.status_code == 200:
            records = res.json().get("records", [])
            return pd.DataFrame(records), "REST API"
    except Exception:
        pass

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
            return pd.DataFrame(records), "JSON Dataset"

    return pd.DataFrame(), "Empty"


# ── Application Main ───────────────────────────────────────────────────────

def main():
    # 1. Hero Header
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">⚡ OAW — Observable Agent Runtime Dashboard</div>
        <div class="hero-sub">Interactive Web Management & Analytics Platform</div>
    </div>
    """, unsafe_allow_html=True)

    df, source_mode = load_dataset()

    if df.empty:
        st.error("No dataset records found in data/dataset.json.")
        return

    # 2. Sidebar Filters (Streamlit Widgets Requirement)
    st.sidebar.markdown("### 🎛️ Filter Controls")
    
    search_term = st.sidebar.text_input("🔍 Search Tools", placeholder="e.g. search, code, api...")
    
    categories = ["All Categories"] + sorted(list(df["category"].dropna().unique()))
    selected_cat = st.sidebar.selectbox("Category", categories)
    
    statuses = ["All Statuses"] + list(df["status"].dropna().unique())
    selected_status = st.sidebar.selectbox("Status", statuses)
    
    max_count = int(df["usage_count"].max()) if not df.empty else 500
    min_usage = st.sidebar.slider("Minimum Usage Count", 0, max_count, 0, step=10)

    # Filter logic
    filtered_df = df.copy()
    if search_term:
        filtered_df = filtered_df[
            filtered_df["name"].str.contains(search_term, case=False, na=False) |
            filtered_df["description"].str.contains(search_term, case=False, na=False)
        ]
    if selected_cat != "All Categories":
        filtered_df = filtered_df[filtered_df["category"] == selected_cat]
    if selected_status != "All Statuses":
        filtered_df = filtered_df[filtered_df["status"] == selected_status]
    filtered_df = filtered_df[filtered_df["usage_count"] >= min_usage]

    # 3. Metric Overview Cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Agent Tools", len(df))
    with c2:
        st.metric("Filtered View", len(filtered_df))
    with c3:
        avg_rat = round(df["rating"].mean(), 2) if not df.empty else 0.0
        st.metric("Average Rating", f"⭐ {avg_rat}")
    with c4:
        tot_usage = df["usage_count"].sum() if not df.empty else 0
        st.metric("Total Executions", f"{tot_usage:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    # 4. Data Visualizations (Plotly Requirement)
    col_left, col_right = st.columns([1.2, 0.8])

    with col_left:
        st.markdown("#### 📊 Execution Usage by Tool")
        fig_bar = px.bar(
            filtered_df,
            x="name",
            y="usage_count",
            color="category",
            hover_data=["status", "rating"],
            labels={"name": "Agent Tool", "usage_count": "Executions"},
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        fig_bar.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=340,
            margin=dict(l=10, r=10, t=20, b=20)
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.markdown("#### 🎯 Status Breakdown")
        status_df = filtered_df["status"].value_counts().reset_index()
        status_df.columns = ["Status", "Count"]
        fig_pie = px.pie(
            status_df,
            values="Count",
            names="Status",
            hole=0.45,
            color_discrete_sequence=px.colors.sequential.Purples_r
        )
        fig_pie.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=340,
            margin=dict(l=10, r=10, t=20, b=20)
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 5. Lab Modules Tabs (Clean User Interactions & File Operations)
    tab_records, tab_add, tab_files = st.tabs([
        "📋 Agent Tools Records",
        "➕ Add New Tool",
        "📁 File Handling & RegEx Lab Module"
    ])

    # Tab 1: Dataset Table
    with tab_records:
        st.dataframe(
            filtered_df[["id", "name", "category", "status", "usage_count", "rating", "description"]],
            use_container_width=True,
            hide_index=True
        )

    # Tab 2: Add New Record Form
    with tab_add:
        st.markdown("##### Add New Agent Tool Record")
        with st.form("add_tool_form", clear_on_submit=True):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                t_name = st.text_input("Tool Name", placeholder="e.g. Vision Transformer Tool")
                t_cat = st.selectbox("Category", ["Information Retrieval", "Code & Compute", "Network & Integration", "Memory & State", "Multimodal", "Database & Storage"])
            with f_col2:
                t_status = st.selectbox("Status", ["Active", "Beta", "Deprecated"])
                t_rating = st.slider("Rating", 1.0, 5.0, 4.5, step=0.1)

            t_desc = st.text_area("Description", placeholder="Functional description of what the tool accomplishes...")
            
            sub = st.form_submit_button("Submit Record", type="primary")
            if sub:
                if not t_name or not t_desc:
                    st.error("Please fill in both Tool Name and Description.")
                else:
                    payload = {
                        "name": t_name,
                        "category": t_cat,
                        "description": t_desc,
                        "status": t_status,
                        "usage_count": 10,
                        "rating": t_rating
                    }
                    saved_via_api = False
                    try:
                        res = requests.post(API_URL, json=payload, timeout=1.5)
                        if res.status_code == 201:
                            saved_via_api = True
                            st.success(f"Record '{t_name}' created successfully via Flask API!")
                            st.rerun()
                    except Exception:
                        pass

                    if not saved_via_api and os.path.exists(DATA_FILE):
                        with open(DATA_FILE, "r+", encoding="utf-8") as f:
                            current_records = json.load(f)
                            new_id = max([r.get("id", 0) for r in current_records], default=100) + 1
                            payload["id"] = new_id
                            current_records.append(payload)
                            f.seek(0)
                            json.dump(current_records, f, indent=2)
                            f.truncate()
                        st.success(f"Record '{t_name}' created and saved to data/dataset.json!")
                        st.rerun()


    # Tab 3: Lab File Handling & RegEx Module
    with tab_files:
        st.markdown("##### File Handling & RegEx Input Validation Module")
        
        from file_manager import (
            read_all_records, append_record, create_backup,
            validate_id, validate_email, validate_date, validate_tool_code
        )

        sub_tab1, sub_tab2 = st.tabs(["📄 Read File Records & Backup", "📝 Add Line with RegEx Check"])

        with sub_tab1:
            records = read_all_records()
            if records:
                st.text_area("Text File Content (data/records.txt)", value="".join(records), height=140, disabled=True)
            
            if st.button("💾 Generate File Backup (records_backup.txt)"):
                msg = create_backup()
                st.success(msg)

        with sub_tab2:
            with st.form("regex_form"):
                r_id = st.text_input("Record ID (RegEx: 1-5 digits)", value="105")
                r_code = st.text_input("Tool Code (RegEx: e.g. OAW-105)", value="OAW-105")
                r_name = st.text_input("Tool Name", value="File System Tool")
                r_email = st.text_input("Email (RegEx: name@domain.com)", value="dev@oaw.io")
                r_date = st.text_input("Date (RegEx: YYYY-MM-DD)", value="2026-08-10")
                r_status = st.selectbox("Status", ["Active", "Beta", "Deprecated"])

                if st.form_submit_button("Validate RegEx & Append Line"):
                    errs = []
                    if not validate_id(r_id):
                        errs.append("Invalid ID format (must be digits).")
                    if not validate_tool_code(r_code):
                        errs.append("Invalid Tool Code format (e.g. OAW-105).")
                    if not validate_email(r_email):
                        errs.append("Invalid Email format (name@domain.com).")
                    if not validate_date(r_date):
                        errs.append("Invalid Date format (YYYY-MM-DD).")

                    if errs:
                        for e in errs:
                            st.error(e)
                    else:
                        line_str = f"{r_id}|{r_code}|{r_name}|{r_email}|{r_date}|{r_status}"
                        res_msg = append_record(line_str)
                        st.success(f"RegEx Passed! {res_msg}")
                        st.rerun()


if __name__ == "__main__":
    main()
