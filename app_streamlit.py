# ─────────────────────────────────────────────
#  app_streamlit.py — OAW Streamlit Agent Dashboard (Requirement #6)
#  Acts as the web analytics, monitoring dashboard, and user management platform.
# ─────────────────────────────────────────────

import os
import json
import requests
import pandas as pd
import plotly.express as px
import streamlit as st

API_URL = "http://127.0.0.1:5000/api/records"
USER_API_URL = "http://127.0.0.1:5000/api/users"
STATUS_API_URL = "http://127.0.0.1:5000/api/status"

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "dataset.json")
USER_FILE = os.path.join(os.path.dirname(__file__), "data", "users.json")

st.set_page_config(
    page_title="OAW — Agent Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .block-container { padding-top: 1.8rem; padding-bottom: 2rem; }
    .hero-container {
        background: linear-gradient(135deg, #1e1b4b 0%, #0f172a 100%);
        border: 1px solid #312e81;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        margin-bottom: 1.5rem;
    }
    .hero-title { font-size: 2rem; font-weight: 800; color: #f8fafc; margin-bottom: 0.2rem; }
    .hero-sub { font-size: 0.95rem; color: #a5b4fc; margin-bottom: 0; }
    [data-testid="stMetric"] {
        background-color: #1e293b;
        border: 1px solid #334155;
        padding: 1rem;
        border-radius: 10px;
    }
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

def check_server_status() -> tuple[bool, dict]:
    try:
        res = requests.get(STATUS_API_URL, timeout=1.2)
        if res.status_code == 200:
            return True, res.json()
    except Exception:
        pass
    return False, {}


def load_dataset() -> tuple[pd.DataFrame, str]:
    try:
        res = requests.get(API_URL, timeout=1.2)
        if res.status_code == 200:
            records = res.json().get("records", [])
            return pd.DataFrame(records), "REST API"
    except Exception:
        pass

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            records = json.load(f)
            return pd.DataFrame(records), "JSON Storage"

    return pd.DataFrame(), "Empty"


def load_users() -> dict:
    try:
        res = requests.get(USER_API_URL, timeout=1.2)
        if res.status_code == 200:
            return res.json().get("users", {})
    except Exception:
        pass

    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    return {}


# ── Application Main ───────────────────────────────────────────────────────

def main():
    is_server_online, server_info = check_server_status()

    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">⚡ OAW — Observable Agent Runtime Dashboard</div>
        <div class="hero-sub">Web Analytics, Monitoring & User Management Platform</div>
    </div>
    """, unsafe_allow_html=True)

    df, source_mode = load_dataset()
    users_dict = load_users()

    # Sidebar Server & System Info
    st.sidebar.markdown("### 🎛️ System Controls")
    
    if is_server_online:
        st.sidebar.success("🟢 Flask REST API: ONLINE (port 5000)")
    else:
        st.sidebar.info("🔴 Flask REST API: OFFLINE (Using JSON file storage)")

    search_term = st.sidebar.text_input("🔍 Search Tools", placeholder="e.g. search, code, api...")
    
    categories = ["All Categories"] + sorted(list(df["category"].dropna().unique())) if not df.empty else ["All Categories"]
    selected_cat = st.sidebar.selectbox("Category", categories)
    
    statuses = ["All Statuses"] + list(df["status"].dropna().unique()) if not df.empty else ["All Statuses"]
    selected_status = st.sidebar.selectbox("Status", statuses)

    filtered_df = df.copy() if not df.empty else pd.DataFrame()
    if not filtered_df.empty:
        if search_term:
            filtered_df = filtered_df[
                filtered_df["name"].str.contains(search_term, case=False, na=False) |
                filtered_df["description"].str.contains(search_term, case=False, na=False)
            ]
        if selected_cat != "All Categories":
            filtered_df = filtered_df[filtered_df["category"] == selected_cat]
        if selected_status != "All Statuses":
            filtered_df = filtered_df[filtered_df["status"] == selected_status]

    # Metrics Overview
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Agent Tools", len(df))
    with c2:
        st.metric("Registered Users", len(users_dict))
    with c3:
        avg_rat = round(df["rating"].mean(), 2) if not df.empty else 0.0
        st.metric("Avg Tool Rating", f"⭐ {avg_rat}")
    with c4:
        tot_usage = df["usage_count"].sum() if not df.empty else 0
        st.metric("Total Executions", f"{tot_usage:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    # Plotly Data Visualizations
    col_left, col_right = st.columns([1.2, 0.8])

    with col_left:
        st.markdown("#### 📊 Execution Usage by Tool")
        if not filtered_df.empty:
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
        if not filtered_df.empty:
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

    # Dashboard Tabs
    tab_records, tab_add, tab_users, tab_files = st.tabs([
        "📋 Agent Tools Records",
        "➕ Add Tool Record",
        "👤 Registered Users & Signup",
        "📁 File System Inspector"
    ])

    with tab_records:
        if not filtered_df.empty:
            st.dataframe(
                filtered_df[["id", "name", "category", "status", "usage_count", "rating", "description"]],
                use_container_width=True,
                hide_index=True
            )

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

    with tab_users:
        st.markdown("##### Registered OAW User Accounts")
        if users_dict:
            user_list = [
                {"Username": k, "Full Name": v.get("full_name"), "Email": v.get("email"), "Phone": v.get("phone"), "Dev Key": v.get("dev_key")}
                for k, v in users_dict.items()
            ]
            st.dataframe(pd.DataFrame(user_list), use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("##### Register New User Account (with RegEx Validation)")
        from auth import AuthValidator, ValidationError
        
        with st.form("signup_form", clear_on_submit=True):
            u_name = st.text_input("Full Name", placeholder="e.g. Edrin Mathew")
            u_user = st.text_input("Username", placeholder="e.g. edrin_dev")
            u_email = st.text_input("Email", placeholder="e.g. edrin@oaw.io")
            u_pass = st.text_input("Password", type="password", placeholder="Min 6 chars (digit & special char)")
            u_phone = st.text_input("Phone Number", placeholder="10-digit phone number")
            u_dev = st.text_input("Developer Key", placeholder="DEV-XXXX (e.g. DEV-1001)")

            u_sub = st.form_submit_button("Register User Account", type="primary")
            if u_sub:
                try:
                    full_name = AuthValidator.format_full_name(u_name)
                    username = AuthValidator.validate_username(u_user)
                    email = AuthValidator.validate_email(u_email)
                    pwd = AuthValidator.validate_password(u_pass)
                    phone = AuthValidator.validate_phone(u_phone)
                    dev_key = AuthValidator.validate_dev_key(u_dev)

                    user_payload = {
                        "username": username,
                        "password": pwd,
                        "full_name": full_name,
                        "email": email,
                        "phone": phone,
                        "dev_key": dev_key
                    }

                    saved_via_api = False
                    try:
                        res = requests.post(USER_API_URL, json=user_payload, timeout=1.5)
                        if res.status_code == 201:
                            saved_via_api = True
                            st.success(f"User '{username}' registered successfully via Flask API!")
                            st.rerun()
                    except Exception:
                        pass

                    if not saved_via_api:
                        curr_users = load_users()
                        curr_users[username] = user_payload
                        os.makedirs(os.path.dirname(USER_FILE), exist_ok=True)
                        with open(USER_FILE, "w", encoding="utf-8") as f:
                            json.dump(curr_users, f, indent=2)
                        st.success(f"User '{username}' registered and saved to data/users.json!")
                        st.rerun()

                except ValidationError as ve:
                    st.error(f"Validation Error: {str(ve)}")

    with tab_files:
        st.markdown("##### File System Storage Inspector")
        from file_manager import read_all_records, create_backup
        
        records = read_all_records()
        if records:
            st.text_area("Text File Records (data/records.txt)", value="".join(records), height=150, disabled=True)
        
        if st.button("💾 Generate File Backup (records_backup.txt)"):
            msg = create_backup()
            st.success(msg)


if __name__ == "__main__":
    main()
