# ─────────────────────────────────────────────
#  app_streamlit.py — Interactive Streamlit Dashboard
#  Domain: AI Agent Tools & Runtime Capabilities Explorer
#  Demonstrates: Streamlit Widgets, Data Visualization, User Interaction, and REST API Integration
# ─────────────────────────────────────────────

import os
import json
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

API_URL = "http://127.0.0.1:5000/api/records"
LOCAL_DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "dataset.json")

# ── Page Config & Custom Styling ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Agent Tools Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-title { font-size: 2.2rem; font-weight: 700; color: #a78bfa; margin-bottom: 0.2rem; }
    .sub-title { font-size: 1rem; color: #94a3b8; margin-bottom: 1.5rem; }
    .card { background-color: #1e293b; padding: 1rem; border-radius: 8px; border: 1px solid #334155; }
</style>
""", unsafe_allow_html=True)


# ── Data Loading & API Fallback Helper ──────────────────────────────────────

def fetch_data() -> tuple[pd.DataFrame, bool]:
    """Fetch records from Flask REST API or fallback to local JSON file."""
    try:
        res = requests.get(API_URL, timeout=2)
        if res.status_code == 200:
            records = res.json().get("records", [])
            df = pd.DataFrame(records)
            return df, True
    except Exception:
        pass

    # Fallback to local JSON file
    if os.path.exists(LOCAL_DATA_FILE):
        with open(LOCAL_DATA_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
            return pd.DataFrame(records), False

    return pd.DataFrame(), False


# ── Main Application ────────────────────────────────────────────────────────

def main():
    st.markdown('<div class="main-title">🤖 AI Agent Tools & Runtime Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Interactive Streamlit Web Application — REST API & Data Visualization</div>', unsafe_allow_html=True)

    df, is_api_online = fetch_data()

    # Connection Status Banner
    if is_api_online:
        st.sidebar.success("🟢 Connected to Flask REST API (http://127.0.0.1:5000)")
    else:
        st.sidebar.warning("🟡 API Server Offline — Using Local `dataset.json` Storage")

    if df.empty:
        st.error("No dataset records found. Please check data/dataset.json.")
        return

    # ── Sidebar Widgets & Filters (User Interaction) ─────────────────────────
    st.sidebar.header("🔍 Filter & Interaction Widgets")

    # 1. Search text input
    search_query = st.sidebar.text_input("Search by Name / Description", placeholder="e.g. search, python, api...")

    # 2. Selectbox for Category
    categories = ["All Categories"] + sorted(list(df["category"].dropna().unique()))
    selected_category = st.sidebar.selectbox("Filter by Category", categories)

    # 3. Radio button for Status
    statuses = ["All"] + list(df["status"].dropna().unique())
    selected_status = st.sidebar.radio("Filter by Tool Status", statuses)

    # 4. Slider for Minimum Usage Count
    max_usage = int(df["usage_count"].max()) if not df.empty else 1000
    min_usage = st.sidebar.slider("Minimum Usage Count", min_value=0, max_value=max_usage, value=0, step=10)

    # Apply filters
    filtered_df = df.copy()
    if search_query:
        filtered_df = filtered_df[
            filtered_df["name"].str.contains(search_query, case=False, na=False) |
            filtered_df["description"].str.contains(search_query, case=False, na=False)
        ]
    if selected_category != "All Categories":
        filtered_df = filtered_df[filtered_df["category"] == selected_category]
    if selected_status != "All":
        filtered_df = filtered_df[filtered_df["status"] == selected_status]
    filtered_df = filtered_df[filtered_df["usage_count"] >= min_usage]

    # ── Metric Summary Cards ────────────────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Registered Tools", len(df))
    with col2:
        st.metric("Filtered Records", len(filtered_df))
    with col3:
        avg_rating = round(df["rating"].mean(), 2) if not df.empty else 0
        st.metric("Average Rating", f"⭐ {avg_rating}")
    with col4:
        total_usage = df["usage_count"].sum() if not df.empty else 0
        st.metric("Total Execution Count", f"{total_usage:,}")

    st.markdown("---")

    # ── Data Visualizations (Plotly Charts) ──────────────────────────────────
    st.subheader("📊 Analytics & Data Visualizations")

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.markdown("**Tool Usage Count by Name**")
        fig_bar = px.bar(
            filtered_df,
            x="name",
            y="usage_count",
            color="category",
            hover_data=["status", "rating"],
            title="Usage Count per Agent Tool",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_bar.update_layout(xaxis_tickangle=-45, height=400)
        st.plotly_chart(fig_bar, use_container_width=True)

    with chart_col2:
        st.markdown("**Distribution of Tool Statuses**")
        status_counts = filtered_df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig_pie = px.pie(
            status_counts,
            values="Count",
            names="Status",
            hole=0.4,
            title="Status Distribution",
            color_discrete_sequence=px.colors.sequential.Purples_r
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # ── Dataset Table & Interactive CRUD ─────────────────────────────────────
    st.subheader("📑 Interactive Dataset & CRUD Operations")

    tab1, tab2, tab3 = st.tabs(["📋 View & Edit Records", "➕ Add New Tool Record", "❌ Delete Record"])

    with tab1:
        st.markdown("Use the interactive data editor below to explore and update tool ratings:")
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("### Add New Tool Record (POST endpoint integration)")
        with st.form("add_tool_form"):
            new_name = st.text_input("Tool Name", placeholder="e.g. Vision Transformer Tool")
            new_cat = st.selectbox("Category", ["Information Retrieval", "Code & Compute", "Network & Integration", "Memory & State", "Multimodal", "Database & Storage", "System Utilities"])
            new_desc = st.text_area("Description", placeholder="Provide a brief functional summary...")
            new_status = st.radio("Status", ["Active", "Beta", "Deprecated"], horizontal=True)
            new_usage = st.number_input("Initial Usage Count", min_value=0, value=10)
            new_rating = st.slider("Tool Rating", min_value=1.0, max_value=5.0, value=4.5, step=0.1)

            submitted = st.form_submit_button("Submit New Record")
            if submitted:
                if not new_name or not new_desc:
                    st.error("Please provide both Name and Description.")
                else:
                    payload = {
                        "name": new_name,
                        "category": new_cat,
                        "description": new_desc,
                        "status": new_status,
                        "usage_count": new_usage,
                        "rating": new_rating
                    }
                    if is_api_online:
                        res = requests.post(API_URL, json=payload)
                        if res.status_code == 201:
                            st.success(f"Record '{new_name}' created successfully via Flask API!")
                            st.rerun()
                        else:
                            st.error(f"API Error: {res.text}")
                    else:
                        st.info("API is offline. Run server.py to persist mutations via REST API.")

    with tab3:
        st.markdown("### Delete Record (DELETE endpoint integration)")
        record_to_delete = st.selectbox(
            "Select Record to Remove",
            options=df["id"].tolist(),
            format_func=lambda x: f"ID {x}: {df[df['id'] == x]['name'].values[0]}" if not df[df['id'] == x].empty else str(x)
        )
        if st.button("Confirm Delete Record", type="primary"):
            if is_api_online:
                res = requests.delete(f"{API_URL}/{record_to_delete}")
                if res.status_code == 200:
                    st.success(f"Record ID {record_to_delete} deleted successfully!")
                    st.rerun()
                else:
                    st.error(f"Delete Error: {res.text}")
            else:
                st.warning("API Server offline. Please start server.py to execute DELETE calls.")

    # ── Section 4: File Handling & RegEx Validation Lab Module ────────────────
    st.markdown("---")
    st.subheader("📁 Lab Module: File Handling & RegEx Validation")

    from file_manager import (
        read_all_records, append_record, search_record, update_record,
        delete_record, create_backup, validate_id, validate_email, validate_date, validate_tool_code
    )

    ftab1, ftab2, ftab3 = st.tabs(["📄 File Records Viewer", "🔍 RegEx Input Validation & Append", "💾 Backup File"])

    with ftab1:
        st.markdown("### Text File Storage (`data/records.txt`)")
        file_lines = read_all_records()
        if file_lines:
            file_df = pd.DataFrame([l.strip().split("|") for l in file_lines], columns=["ID", "Tool Code", "Name", "Email", "Date", "Status"])
            st.dataframe(file_df, use_container_width=True, hide_index=True)
        else:
            st.info("File is empty.")

    with ftab2:
        st.markdown("### Data Entry with RegEx Input Validation")
        with st.form("file_entry_form"):
            f_id = st.text_input("Record ID (RegEx: 1-5 digits)", value="105")
            f_code = st.text_input("Tool Code (RegEx: e.g. OAW-105)", value="OAW-105")
            f_name = st.text_input("Tool Name", value="File System Tool")
            f_email = st.text_input("Contact Email (RegEx: name@domain.com)", value="dev@oaw.io")
            f_date = st.text_input("Date (RegEx: YYYY-MM-DD)", value="2026-08-10")
            f_status = st.selectbox("Status", ["Active", "Beta", "Deprecated"])

            f_submit = st.form_submit_button("Validate RegEx & Append Record (Mode 'a')")
            if f_submit:
                # RegEx Validation Checks
                errors = []
                if not validate_id(f_id):
                    errors.append("❌ Invalid ID format (must be 1-5 digits).")
                if not validate_tool_code(f_code):
                    errors.append("❌ Invalid Tool Code format (must be e.g. OAW-105).")
                if not validate_email(f_email):
                    errors.append("❌ Invalid Email format (must be name@domain.com).")
                if not validate_date(f_date):
                    errors.append("❌ Invalid Date format (must be YYYY-MM-DD).")

                if errors:
                    for err in errors:
                        st.error(err)
                else:
                    new_line = f"{f_id}|{f_code}|{f_name}|{f_email}|{f_date}|{f_status}"
                    msg = append_record(new_line)
                    st.success(f"✅ All RegEx Validations Passed! {msg}")
                    st.rerun()

    with ftab3:
        st.markdown("### Create Data File Backup Copy")
        if st.button("Generate Backup Copy ('records_backup.txt')"):
            b_msg = create_backup()
            st.success(f"✅ {b_msg}")


if __name__ == "__main__":
    main()

