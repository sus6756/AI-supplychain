import io
import time
import requests
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
import mysql.connector
from mysql.connector import Error

# ====================================================================
# 1. PAGE & SESSION STATE INITIALIZATION
# ====================================================================
st.set_page_config(page_title="Traqify", layout="wide", page_icon="📦")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "username" not in st.session_state:
    st.session_state.username = ""
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

# ====================================================================
# 2. GLOBAL CSS ANIMATIONS & STYLING
# ====================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

@keyframes fadeInDown {
    from { opacity: 0; transform: translateY(-30px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(30px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInLeft {
    from { opacity: 0; transform: translateX(-40px); }
    to   { opacity: 1; transform: translateX(0); }
}
@keyframes pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(99,102,241,0.4); }
    50%       { box-shadow: 0 0 20px 6px rgba(99,102,241,0.2); }
}
@keyframes shimmer {
    0%   { background-position: -1000px 0; }
    100% { background-position:  1000px 0; }
}
@keyframes gradientShift {
    0%   { background-position: 0% 50%; }
    50%  { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}
@keyframes countUp {
    from { opacity: 0; transform: scale(0.5); }
    to   { opacity: 1; transform: scale(1); }
}

h1 {
    background: linear-gradient(135deg, #6366f1, #06b6d4, #8b5cf6);
    background-size: 200% 200%;
    animation: fadeInDown 0.7s ease both, gradientShift 4s ease infinite;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    font-weight: 700 !important;
}
h2, h3 { animation: fadeInLeft 0.6s ease both; color: #e2e8f0 !important; }
.main .block-container { animation: fadeInUp 0.5s ease both; padding-top: 2rem; }

[data-testid="metric-container"] {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 100%);
    border: 1px solid rgba(99,102,241,0.3);
    border-radius: 16px;
    padding: 1.2rem 1.5rem;
    animation: fadeInUp 0.6s ease both, pulse 3s infinite;
    transition: transform 0.25s ease, box-shadow 0.25s ease;
}
[data-testid="metric-container"]:hover {
    transform: translateY(-6px) scale(1.02);
    box-shadow: 0 12px 32px rgba(99,102,241,0.35);
    border-color: rgba(99,102,241,0.7);
}
[data-testid="metric-container"] > div:first-child {
    color: #a5b4fc !important; font-size: 0.8rem !important;
    text-transform: uppercase; letter-spacing: 1px;
}
[data-testid="stMetricValue"] {
    color: #ffffff !important; font-weight: 700 !important;
    font-size: 2rem !important;
    animation: countUp 0.8s cubic-bezier(0.175,0.885,0.32,1.275) both;
}

.stButton > button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white !important; border: none; border-radius: 10px;
    padding: 0.55rem 1.4rem; font-weight: 600;
    transition: transform 0.2s ease, box-shadow 0.2s ease;
    position: relative; overflow: hidden;
}
.stButton > button::after {
    content: ''; position: absolute;
    top: -50%; left: -75%; width: 50%; height: 200%;
    background: rgba(255,255,255,0.15); transform: skewX(-20deg);
    transition: left 0.4s ease;
}
.stButton > button:hover::after { left: 125%; }
.stButton > button:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(99,102,241,0.45);
}
.stButton > button:active { transform: translateY(0px) scale(0.97); }

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0e17 0%, #1a1a2e 60%, #16213e 100%) !important;
    border-right: 1px solid rgba(99,102,241,0.2);
    animation: fadeInLeft 0.5s ease both;
}
[data-testid="stDataFrame"] {
    border-radius: 12px; overflow: hidden;
    border: 1px solid rgba(99,102,241,0.2);
    animation: fadeInUp 0.7s ease both; transition: box-shadow 0.3s ease;
}
[data-testid="stDataFrame"]:hover { box-shadow: 0 8px 30px rgba(99,102,241,0.2); }
[data-testid="stPlotlyChart"] {
    border-radius: 16px; overflow: hidden;
    border: 1px solid rgba(99,102,241,0.2);
    animation: fadeInUp 0.8s ease both; transition: box-shadow 0.3s ease;
}
[data-testid="stPlotlyChart"]:hover { box-shadow: 0 10px 40px rgba(6,182,212,0.2); }

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: rgba(30,27,75,0.6) !important;
    border: 1px solid rgba(99,102,241,0.3) !important;
    border-radius: 10px !important; color: #e2e8f0 !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.2) !important;
}

.auth-card {
    background: linear-gradient(135deg, rgba(30,27,75,0.9), rgba(17,24,39,0.95));
    border: 1px solid rgba(99,102,241,0.35); border-radius: 20px;
    padding: 2.5rem 2rem; backdrop-filter: blur(10px);
    animation: fadeInUp 0.7s cubic-bezier(0.175,0.885,0.32,1.275) both;
    box-shadow: 0 20px 60px rgba(0,0,0,0.5), 0 0 40px rgba(99,102,241,0.1);
}
[data-testid="stAlert"] { border-radius: 12px !important; animation: fadeInDown 0.4s ease both; }

.stTabs [data-baseweb="tab-list"] {
    gap: 8px; background: rgba(30,27,75,0.4); border-radius: 12px; padding: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 9px; padding: 0.5rem 1.2rem; font-weight: 600;
    color: #94a3b8 !important; transition: all 0.25s ease; background: transparent;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #8b5cf6) !important;
    color: white !important; box-shadow: 0 4px 15px rgba(99,102,241,0.4);
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0f0e17; }
::-webkit-scrollbar-thumb { background: #6366f1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #8b5cf6; }

.hero-banner {
    background: linear-gradient(135deg, #1e1b4b, #312e81, #1e3a5f);
    background-size: 300% 300%;
    animation: gradientShift 6s ease infinite;
    border-radius: 20px; padding: 2rem 2.5rem; margin-bottom: 1.5rem;
    border: 1px solid rgba(99,102,241,0.3);
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}
.hero-banner h2 { margin: 0 !important; font-size: 1.6rem !important; color: #e2e8f0 !important; }
.hero-banner p  { margin: 0.3rem 0 0 0; color: #94a3b8; font-size: 0.9rem; }

.section-divider {
    height: 2px;
    background: linear-gradient(90deg, transparent, #6366f1, #06b6d4, transparent);
    border-radius: 2px; margin: 1.5rem 0;
    animation: shimmer 2.5s linear infinite; background-size: 1000px 2px;
}

[data-testid="column"]:nth-child(1) [data-testid="metric-container"] { animation-delay: 0.1s; }
[data-testid="column"]:nth-child(2) [data-testid="metric-container"] { animation-delay: 0.2s; }
[data-testid="column"]:nth-child(3) [data-testid="metric-container"] { animation-delay: 0.3s; }
[data-testid="column"]:nth-child(4) [data-testid="metric-container"] { animation-delay: 0.4s; }

.badge-ontime  { background:#14532d; color:#4ade80; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-delayed { background:#450a0a; color:#f87171; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
.badge-critical{ background:#431407; color:#fb923c; padding:2px 10px; border-radius:20px; font-size:0.78rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ====================================================================
# 3. MYSQL CONFIG & DB SETUP
# ====================================================================
DB_CONFIG = {
    "host":     st.secrets["DB_HOST"],
    "user":     st.secrets["DB_USER"],
    "password": st.secrets["DB_PASSWORD"],
    "database": st.secrets["DB_NAME"],
    "port":     st.secrets["DB_PORT"]
}

def init_db():
    try:
        conn   = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            email VARCHAR(255) DEFAULT NULL);""")
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN email VARCHAR(255) DEFAULT NULL;")
        except Exception:
            pass  # column already exists
        conn.commit(); cursor.close(); conn.close()
    except Error as e:
        st.error(f"DB Init Error: {e}")

def init_supply_chain_tables():
    try:
        conn   = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS products (
            product_id INT PRIMARY KEY, product_name VARCHAR(100),
            category VARCHAR(50), stock_quantity INT,
            reorder_level INT, warehouse_location VARCHAR(50),
            unit_price DECIMAL(10,2));""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id INT PRIMARY KEY, supplier_name VARCHAR(100),
            country VARCHAR(50), reliability_score FLOAT);""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS shipments (
            shipment_id INT PRIMARY KEY, supplier_id INT, product_id INT,
            shipment_date DATE, expected_delivery DATE, actual_delivery DATE,
            quantity INT, transport_cost DECIMAL(10,2),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
            FOREIGN KEY (product_id)  REFERENCES products(product_id));""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS sales (
            sale_id INT PRIMARY KEY, product_id INT, sale_date DATE,
            quantity_sold INT, revenue DECIMAL(10,2),
            FOREIGN KEY (product_id) REFERENCES products(product_id));""")
        conn.commit(); cursor.close(); conn.close()
    except Error as e:
        st.error(f"Table Init Error: {e}")

init_db()
init_supply_chain_tables()

# ====================================================================
# 4. HELPERS
# ====================================================================
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(15,14,23,0.6)",
    font=dict(family="Inter", color="#e2e8f0"),
)

def to_excel_bytes(dfs: dict) -> bytes:
    """Serialize a dict of {sheet_name: df} to an xlsx bytes buffer."""
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        for sheet, df in dfs.items():
            df.to_excel(writer, sheet_name=sheet, index=False)
    return buf.getvalue()

def shipment_badge(delay: float) -> str:
    if pd.isna(delay) or delay <= 0:
        return '<span class="badge-ontime">✅ On Time</span>'
    elif delay <= 3:
        return '<span class="badge-delayed">⚠️ Delayed</span>'
    else:
        return '<span class="badge-critical">🚨 Critical</span>'

def forecast_revenue(sales_df: pd.DataFrame, periods: int = 3) -> pd.DataFrame:
    """Simple linear regression forecast on monthly revenue."""
    sales_df = sales_df.copy()
    sales_df["month_dt"] = sales_df["sale_date"].dt.to_period("M").dt.to_timestamp()
    monthly = sales_df.groupby("month_dt")["revenue"].sum().reset_index()
    monthly["t"] = np.arange(len(monthly))

    X = monthly[["t"]].values
    y = monthly["revenue"].values
    model = LinearRegression().fit(X, y)

    future_t = np.arange(len(monthly), len(monthly) + periods).reshape(-1, 1)
    last_date = monthly["month_dt"].max()
    future_dates = pd.date_range(last_date + pd.DateOffset(months=1), periods=periods, freq="MS")
    forecast_df = pd.DataFrame({"month_dt": future_dates, "revenue": model.predict(future_t), "t": future_t.flatten()})
    monthly["type"] = "Actual"
    forecast_df["type"] = "Forecast"
    return pd.concat([monthly, forecast_df], ignore_index=True)

# ====================================================================
# 5. EMAIL NOTIFICATIONS
# ====================================================================
def send_email(to_addr: str, subject: str, html_body: str) -> bool:
    try:
        api_key = st.secrets["RESEND_API_KEY"]
        resp = requests.post(
            "https://api.resend.com/emails",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={
                "from": "Traqify <onboarding@resend.dev>",
                "to":   [to_addr],
                "subject": subject,
                "html": html_body,
            },
            timeout=10,
        )
        if resp.status_code in (200, 201):
            return True
        else:
            st.error(f"Email error: {resp.status_code} — {resp.text}")
            return False
    except Exception as e:
        st.error(f"Email error: {e}")
        return False

def email_template(title: str, body_html: str) -> str:
    return f"""
    <html><body style="margin:0;padding:0;background:#0f0e17;font-family:Inter,sans-serif;">
    <div style="max-width:600px;margin:30px auto;background:linear-gradient(135deg,#1e1b4b,#1a1a2e);
        border:1px solid rgba(99,102,241,0.3);border-radius:16px;overflow:hidden;">
        <div style="background:linear-gradient(135deg,#6366f1,#8b5cf6);padding:24px 32px;">
            <h1 style="margin:0;color:#fff;font-size:1.4rem;">🚛 Traqify</h1>
            <p style="margin:4px 0 0;color:rgba(255,255,255,0.7);font-size:0.85rem;">Track · Analyze · Notify</p>
        </div>
        <div style="padding:28px 32px;">
            <h2 style="color:#a5b4fc;margin:0 0 16px;">{title}</h2>
            {body_html}
        </div>
        <div style="padding:16px 32px;border-top:1px solid rgba(99,102,241,0.2);text-align:center;">
            <p style="color:#475569;font-size:0.75rem;margin:0;">Traqify · Automated Alert System</p>
        </div>
    </div></body></html>"""

def send_low_stock_alert(to_addr: str, low_df):
    rows = ""
    for _, r in low_df.iterrows():
        name = r.get("product_name", r.get("product_id", "N/A"))
        rows += f"""<tr>
            <td style="padding:8px 12px;color:#e2e8f0;">{name}</td>
            <td style="padding:8px 12px;color:#f87171;text-align:center;">{r["stock_quantity"]}</td>
            <td style="padding:8px 12px;color:#a5b4fc;text-align:center;">{r["reorder_level"]}</td>
            <td style="padding:8px 12px;color:#fb923c;text-align:center;">{r["reorder_level"] - r["stock_quantity"]}</td>
        </tr>"""
    body = f"""<p style="color:#94a3b8;">These products are below reorder level:</p>
    <table style="width:100%;border-collapse:collapse;margin-top:12px;background:rgba(0,0,0,0.3);border-radius:8px;overflow:hidden;">
        <thead><tr style="background:rgba(99,102,241,0.2);">
            <th style="padding:10px 12px;color:#a5b4fc;text-align:left;">Product</th>
            <th style="padding:10px 12px;color:#a5b4fc;">Stock</th>
            <th style="padding:10px 12px;color:#a5b4fc;">Reorder Level</th>
            <th style="padding:10px 12px;color:#a5b4fc;">Units Needed</th>
        </tr></thead><tbody>{rows}</tbody></table>"""
    return send_email(to_addr, f"\u26a0\ufe0f Low Stock Alert \u2014 {len(low_df)} Products", email_template("\u26a0\ufe0f Low Stock Alert", body))

def send_delay_alert(to_addr: str, delayed_df):
    rows = ""
    for _, r in delayed_df.iterrows():
        rows += f"""<tr>
            <td style="padding:8px 12px;color:#e2e8f0;">{r.get("shipment_id","N/A")}</td>
            <td style="padding:8px 12px;color:#e2e8f0;">{r.get("product_id","N/A")}</td>
            <td style="padding:8px 12px;color:#94a3b8;">{str(r.get("expected_delivery",""))[:10]}</td>
            <td style="padding:8px 12px;color:#f87171;text-align:center;">{int(r.get("delay_days",0))} days</td>
        </tr>"""
    body = f"""<p style="color:#94a3b8;">{len(delayed_df)} shipments are currently delayed:</p>
    <table style="width:100%;border-collapse:collapse;margin-top:12px;background:rgba(0,0,0,0.3);border-radius:8px;overflow:hidden;">
        <thead><tr style="background:rgba(99,102,241,0.2);">
            <th style="padding:10px 12px;color:#a5b4fc;text-align:left;">Shipment ID</th>
            <th style="padding:10px 12px;color:#a5b4fc;">Product ID</th>
            <th style="padding:10px 12px;color:#a5b4fc;">Expected</th>
            <th style="padding:10px 12px;color:#a5b4fc;">Delay</th>
        </tr></thead><tbody>{rows}</tbody></table>"""
    return send_email(to_addr, f"\U0001f6a8 Shipment Delay Alert \u2014 {len(delayed_df)} Delayed", email_template("\U0001f6a8 Shipment Delay Alert", body))

def send_summary_email(to_addr: str, total_rev: float, delayed: int, low_stock: int, products: int):
    body = f"""<p style="color:#94a3b8;">Your current supply chain summary:</p>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:16px;">
        <div style="background:rgba(99,102,241,0.15);border:1px solid rgba(99,102,241,0.3);border-radius:10px;padding:16px;text-align:center;">
            <div style="color:#a5b4fc;font-size:0.75rem;text-transform:uppercase;">Total Revenue</div>
            <div style="color:#fff;font-size:1.6rem;font-weight:700;">${total_rev:,.0f}</div>
        </div>
        <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);border-radius:10px;padding:16px;text-align:center;">
            <div style="color:#fca5a5;font-size:0.75rem;text-transform:uppercase;">Delayed Shipments</div>
            <div style="color:#f87171;font-size:1.6rem;font-weight:700;">{delayed}</div>
        </div>
        <div style="background:rgba(234,179,8,0.1);border:1px solid rgba(234,179,8,0.3);border-radius:10px;padding:16px;text-align:center;">
            <div style="color:#fde68a;font-size:0.75rem;text-transform:uppercase;">Low Stock Items</div>
            <div style="color:#fbbf24;font-size:1.6rem;font-weight:700;">{low_stock}</div>
        </div>
        <div style="background:rgba(34,197,94,0.1);border:1px solid rgba(34,197,94,0.3);border-radius:10px;padding:16px;text-align:center;">
            <div style="color:#86efac;font-size:0.75rem;text-transform:uppercase;">Total Products</div>
            <div style="color:#4ade80;font-size:1.6rem;font-weight:700;">{products}</div>
        </div>
    </div>"""
    return send_email(to_addr, "\U0001f4ca Your Supply Chain Summary Report", email_template("\U0001f4ca Dashboard Summary", body))



# ====================================================================
# 5. AUTH PAGE
# ====================================================================
def auth_page():
    st.markdown("""
    <div style="text-align:center; animation:fadeInDown 0.8s ease both; padding:2rem 0 1rem 0;">
        <div style="font-size:4rem;filter:drop-shadow(0 0 12px rgba(99,102,241,0.7));">📦</div>
        <h1 style="font-size:3rem; margin:0.3rem 0; font-weight:900; letter-spacing:2px;">Traqify</h1>
        <p style="color:#94a3b8; font-size:1rem; margin:0;">Track · Analyze · Notify</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    _, center_col, _ = st.columns([1, 1.4, 1])
    with center_col:
        st.markdown('<div class="auth-card">', unsafe_allow_html=True)

        if st.session_state.auth_mode == "login":
            st.markdown("""
            <div style="text-align:center;margin-bottom:1.5rem;">
                <span style="font-size:2rem;">🔐</span>
                <h3 style="margin:0.3rem 0;color:#e2e8f0;">Welcome Back</h3>
                <p style="color:#64748b;font-size:0.85rem;margin:0;">Sign in to your account</p>
            </div>""", unsafe_allow_html=True)
            with st.form("login"):
                username = st.text_input("👤 Username")
                password = st.text_input("🔑 Password", type="password")
                if st.form_submit_button("Login →", use_container_width=True):
                    with st.spinner("Authenticating..."):
                        conn   = mysql.connector.connect(**DB_CONFIG)
                        cursor = conn.cursor()
                        cursor.execute("SELECT password, email FROM users WHERE username=%s", (username,))
                        row = cursor.fetchone(); cursor.close(); conn.close()
                    if row and row[0] == password:
                        st.success("✅ Login successful! Loading dashboard...")
                        time.sleep(0.6)
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.user_email = row[1] or ""
                        st.rerun()
                    else:
                        st.error("❌ Invalid username or password")
        else:
            st.markdown("""
            <div style="text-align:center;margin-bottom:1.5rem;">
                <span style="font-size:2rem;">📝</span>
                <h3 style="margin:0.3rem 0;color:#e2e8f0;">Create Account</h3>
                <p style="color:#64748b;font-size:0.85rem;margin:0;">Join the platform today</p>
            </div>""", unsafe_allow_html=True)
            with st.form("signup"):
                username = st.text_input("👤 Username")
                password = st.text_input("🔑 Password", type="password")
                email_signup = st.text_input("📧 Email Address (for notifications)")
                if st.form_submit_button("Create Account →", use_container_width=True):
                    with st.spinner("Creating account..."):
                        conn   = mysql.connector.connect(**DB_CONFIG)
                        cursor = conn.cursor()
                        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
                        exists = cursor.fetchone()
                        if exists:
                            st.error("⚠️ Username already exists")
                        else:
                            cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, password, email_signup or None))
                            conn.commit()
                            st.success("🎉 Account created! You can now log in.")
                        cursor.close(); conn.close()

        st.markdown("---")
        label = "Don't have an account? Sign Up →" if st.session_state.auth_mode == "login" else "Already have an account? Login →"
        if st.button(label, use_container_width=True):
            st.session_state.auth_mode = "signup" if st.session_state.auth_mode == "login" else "login"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# ====================================================================
# 6. MAIN DASHBOARD
# ====================================================================
def main_dashboard():
    # ── Sidebar ──────────────────────────────────────────────────────
    st.sidebar.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem 0;">
        <div style="font-size:3rem;filter:drop-shadow(0 0 8px rgba(99,102,241,0.6));">📦</div>
        <h3 style="color:#a5b4fc;margin:0.4rem 0;font-size:1.4rem;font-weight:800;letter-spacing:1px;">Traqify</h3>
        <p style="color:#6366f1;font-size:0.78rem;margin:0;font-weight:600;letter-spacing:2px;text-transform:uppercase;">Dashboard</p>
    </div>
    <hr style="border-color:rgba(99,102,241,0.3);margin:0.8rem 0;">
    """, unsafe_allow_html=True)

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    st.sidebar.markdown("---")
    option = st.sidebar.radio("📂 Upload Type", ["Excel", "CSV"])

    # ── Hero Banner ───────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-banner">
        <h2>🚛 Traqify — Supply Chain Dashboard</h2>
        <p>Real-time analytics · Inventory · Shipments · Forecasting · Alerts</p>
    </div>
    """, unsafe_allow_html=True)

    # ── File Upload ───────────────────────────────────────────────────
    products_df = sales_df = shipments_df = None
    data_loaded = False

    if option == "Excel":
        file = st.sidebar.file_uploader("📊 Upload Excel (.xlsx)", type=["xlsx"])
        if file:
            with st.spinner("Loading Excel..."):
                products_df  = pd.read_excel(file, sheet_name="products")
                shipments_df = pd.read_excel(file, sheet_name="shipments")
                sales_df     = pd.read_excel(file, sheet_name="sales")
                data_loaded  = True
            st.toast("✅ Excel loaded!", icon="📊")
    else:
        p  = st.sidebar.file_uploader("📦 products.csv",  type=["csv"])
        s  = st.sidebar.file_uploader("💰 sales.csv",     type=["csv"])
        sh = st.sidebar.file_uploader("🚚 shipments.csv", type=["csv"])
        if p and s and sh:
            with st.spinner("Loading CSVs..."):
                products_df  = pd.read_csv(p)
                sales_df     = pd.read_csv(s)
                shipments_df = pd.read_csv(sh)
                data_loaded  = True
            st.toast("✅ CSVs loaded!", icon="📁")

    if not data_loaded:
        st.markdown("""
        <div style="background:linear-gradient(135deg,rgba(234,179,8,0.1),rgba(234,179,8,0.05));
            border:1px solid rgba(234,179,8,0.3);border-radius:14px;
            padding:1.5rem 2rem;text-align:center;animation:fadeInUp 0.5s ease both;">
            <div style="font-size:2rem;margin-bottom:0.5rem;">📂</div>
            <h4 style="color:#fbbf24;margin:0;">No data loaded yet</h4>
            <p style="color:#94a3b8;margin:0.3rem 0 0 0;font-size:0.9rem;">
                Upload your Excel or CSV files from the sidebar to get started.</p>
        </div>""", unsafe_allow_html=True)
        st.stop()

    # ── Data Prep ─────────────────────────────────────────────────────
    sales_df["revenue"]               = pd.to_numeric(sales_df["revenue"], errors="coerce")
    sales_df["sale_date"]             = pd.to_datetime(sales_df["sale_date"], errors="coerce")
    shipments_df["expected_delivery"] = pd.to_datetime(shipments_df["expected_delivery"], errors="coerce")
    shipments_df["actual_delivery"]   = pd.to_datetime(shipments_df["actual_delivery"], errors="coerce")
    shipments_df["delay_days"]        = (shipments_df["actual_delivery"] - shipments_df["expected_delivery"]).dt.days
    shipments_df["status"]            = shipments_df["delay_days"].apply(shipment_badge)

    # ── Sidebar: Date Range Filter ────────────────────────────────────
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📅 Date Range Filter")
    min_d = sales_df["sale_date"].min().date()
    max_d = sales_df["sale_date"].max().date()
    date_range = st.sidebar.date_input("Filter sales by date", value=(min_d, max_d), min_value=min_d, max_value=max_d)
    if len(date_range) == 2:
        sales_df = sales_df[(sales_df["sale_date"].dt.date >= date_range[0]) &
                            (sales_df["sale_date"].dt.date <= date_range[1])]

    # ── KPIs ──────────────────────────────────────────────────────────
    total_rev     = sales_df["revenue"].sum()
    delayed_count = len(shipments_df[shipments_df["delay_days"] > 0])
    low_stock     = len(products_df[products_df["stock_quantity"] < products_df["reorder_level"]])
    product_count = len(products_df)

    # Delta: compare first half vs second half of the date-filtered revenue
    mid = sales_df["sale_date"].median()
    rev_first  = sales_df[sales_df["sale_date"] <= mid]["revenue"].sum()
    rev_second = sales_df[sales_df["sale_date"] >  mid]["revenue"].sum()
    rev_delta  = rev_second - rev_first

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("💰 Total Revenue",     f"${total_rev:,.0f}",  delta=f"${rev_delta:,.0f}")
    c2.metric("⚠️ Delayed Shipments", delayed_count)
    c3.metric("📉 Low Stock Items",   low_stock)
    c4.metric("📦 Total Products",    product_count)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Export Button ─────────────────────────────────────────────────
    export_bytes = to_excel_bytes({
        "Sales": sales_df, "Products": products_df, "Shipments": shipments_df
    })
    st.sidebar.markdown("---")
    st.sidebar.download_button(
        label="📥 Export Dashboard (Excel)",
        data=export_bytes,
        file_name="supply_chain_export.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

    # ── Tabs ──────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 Revenue & Forecast",
        "📦 Inventory",
        "🚚 Shipments",
        "🏆 Supplier Scorecard",
        "🌍 Supplier Map",
        "🗿 SQL Console",
        "📧 Notifications",
    ])

    # ─────────────────────────────────────────────────────────────────
    # TAB 1 — REVENUE & FORECAST
    # ─────────────────────────────────────────────────────────────────
    with tab1:
        st.markdown("### 💰 Monthly Revenue Trends")
        sales_df["month"] = sales_df["sale_date"].dt.strftime("%Y-%m")
        monthly = sales_df.groupby("month")["revenue"].sum().reset_index()
        fig_bar = px.bar(
            monthly, x="month", y="revenue",
            color="revenue",
            color_continuous_scale=["#4f46e5","#06b6d4","#8b5cf6"],
            template="plotly_dark",
            labels={"month":"Month","revenue":"Revenue ($)"},
        )
        fig_bar.update_layout(**CHART_LAYOUT, margin=dict(l=10,r=10,t=40,b=10), showlegend=False)
        fig_bar.update_traces(marker_line_width=0)
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("### 🔮 Demand Forecast (Next 3 Months)")
        forecast_periods = st.slider("Forecast periods (months)", 1, 12, 3)
        try:
            fc_df = forecast_revenue(sales_df, periods=forecast_periods)
            fig_fc = px.line(
                fc_df, x="month_dt", y="revenue", color="type",
                color_discrete_map={"Actual": "#6366f1", "Forecast": "#06b6d4"},
                markers=True, template="plotly_dark",
                labels={"month_dt": "Month", "revenue": "Revenue ($)", "type": ""},
            )
            fig_fc.update_traces(line=dict(width=2.5))
            fig_fc.update_layout(**CHART_LAYOUT, margin=dict(l=10,r=10,t=40,b=10), showlegend=True)
            st.plotly_chart(fig_fc, use_container_width=True)
            forecast_only = fc_df[fc_df["type"] == "Forecast"][["month_dt","revenue"]].copy()
            forecast_only.columns = ["Month", "Forecasted Revenue ($)"]
            forecast_only["Forecasted Revenue ($)"] = forecast_only["Forecasted Revenue ($)"].map("${:,.0f}".format)
            st.dataframe(forecast_only, use_container_width=True, hide_index=True)
        except Exception as e:
            st.warning(f"Forecast unavailable: {e}")

    # ─────────────────────────────────────────────────────────────────
    # TAB 2 — INVENTORY
    # ─────────────────────────────────────────────────────────────────
    with tab2:
        st.markdown("### 📦 Inventory Status")

        # Search bar
        search = st.text_input("🔍 Search products by name or category", placeholder="e.g. Electronics")
        filtered_products = products_df.copy()
        if search:
            mask = filtered_products.apply(lambda row: row.astype(str).str.contains(search, case=False).any(), axis=1)
            filtered_products = filtered_products[mask]

        low_df = filtered_products[filtered_products["stock_quantity"] < filtered_products["reorder_level"]]
        if not low_df.empty:
            st.markdown(f"""
            <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);
                border-radius:10px;padding:0.8rem 1rem;margin-bottom:1rem;animation:fadeInDown 0.4s ease both;">
                ⚠️ <strong style="color:#f87171;">{len(low_df)} products</strong>
                <span style="color:#94a3b8;"> are below reorder level</span>
            </div>""", unsafe_allow_html=True)

        st.dataframe(filtered_products, use_container_width=True, height=320)

        # Reorder alert table + CSV export
        if not low_df.empty:
            st.markdown("#### 🚨 Reorder Alerts")
            reorder = low_df.copy()
            reorder["units_needed"] = reorder["reorder_level"] - reorder["stock_quantity"]
            st.dataframe(reorder[["product_id","product_name","stock_quantity","reorder_level","units_needed"]
                                 if all(c in reorder.columns for c in ["product_name","units_needed"])
                                 else reorder.columns],
                         use_container_width=True, hide_index=True)
            st.download_button(
                "📥 Download Reorder List (CSV)",
                data=reorder.to_csv(index=False).encode(),
                file_name="reorder_alerts.csv",
                mime="text/csv",
            )

        col_a, col_b = st.columns(2)
        with col_a:
            # Stock bar chart
            name_col = "product_name" if "product_name" in products_df.columns else products_df.columns[0]
            fig_stock = px.bar(
                products_df.sort_values("stock_quantity").head(15),
                x=name_col, y="stock_quantity",
                color="stock_quantity",
                color_continuous_scale=["#ef4444","#f59e0b","#22c55e"],
                template="plotly_dark", title="Bottom 15 Stock Levels",
            )
            fig_stock.update_layout(**CHART_LAYOUT, margin=dict(l=10,r=10,t=40,b=80), showlegend=False)
            st.plotly_chart(fig_stock, use_container_width=True)

        with col_b:
            # Category donut chart
            if "category" in products_df.columns:
                cat_counts = products_df["category"].value_counts().reset_index()
                cat_counts.columns = ["category","count"]
                fig_donut = px.pie(
                    cat_counts, names="category", values="count",
                    hole=0.55, template="plotly_dark", title="Products by Category",
                    color_discrete_sequence=px.colors.sequential.Plasma_r,
                )
                fig_donut.update_layout(**CHART_LAYOUT, margin=dict(l=10,r=10,t=40,b=10), showlegend=True)
                st.plotly_chart(fig_donut, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────
    # TAB 3 — SHIPMENTS
    # ─────────────────────────────────────────────────────────────────
    with tab3:
        st.markdown("### 🚚 Shipment Tracker")

        # Search bar
        ship_search = st.text_input("🔍 Search shipments", placeholder="e.g. shipment ID or product ID", key="ship_search")
        filtered_ship = shipments_df.copy()
        if ship_search:
            mask = filtered_ship.drop(columns=["status"]).apply(
                lambda row: row.astype(str).str.contains(ship_search, case=False).any(), axis=1)
            filtered_ship = filtered_ship[mask]

        if delayed_count == 0:
            st.success("✅ All shipments on time — no delays detected.")
        else:
            st.warning(f"⚠️ {delayed_count} shipments are running late.")

        # Status badges rendered in HTML
        display_cols = [c for c in filtered_ship.columns if c != "status"]
        badge_html = filtered_ship["status"].values
        table_df = filtered_ship[display_cols].copy()
        table_df["Status"] = badge_html
        st.write(table_df.to_html(escape=False, index=False), unsafe_allow_html=True)

        st.markdown("---")
        c_a, c_b = st.columns(2)
        with c_a:
            fig_scatter = px.scatter(
                shipments_df, x="expected_delivery", y="actual_delivery",
                color="delay_days",
                color_continuous_scale=["#22c55e","#f59e0b","#ef4444"],
                template="plotly_dark", title="Expected vs Actual Delivery",
                labels={"expected_delivery":"Expected","actual_delivery":"Actual","delay_days":"Delay (days)"},
            )
            fig_scatter.update_layout(**CHART_LAYOUT, margin=dict(l=10,r=10,t=40,b=10), showlegend=False)
            st.plotly_chart(fig_scatter, use_container_width=True)
        with c_b:
            delay_hist = px.histogram(
                shipments_df[shipments_df["delay_days"].notna()],
                x="delay_days", nbins=20,
                color_discrete_sequence=["#6366f1"],
                template="plotly_dark", title="Delay Days Distribution",
                labels={"delay_days":"Delay (days)"},
            )
            delay_hist.update_layout(**CHART_LAYOUT, margin=dict(l=10,r=10,t=40,b=10), showlegend=False)
            st.plotly_chart(delay_hist, use_container_width=True)

    # ─────────────────────────────────────────────────────────────────
    # TAB 4 — SUPPLIER SCORECARD
    # ─────────────────────────────────────────────────────────────────
    with tab4:
        st.markdown("### 🏆 Supplier Scorecard")

        # Build scorecard from shipments + products join
        if "supplier_id" in shipments_df.columns:
            score_df = shipments_df.groupby("supplier_id").agg(
                total_shipments=("shipment_id","count"),
                avg_delay=("delay_days","mean"),
                delayed_count=("delay_days", lambda x: (x > 0).sum()),
            ).reset_index()
            score_df["on_time_rate"] = ((score_df["total_shipments"] - score_df["delayed_count"])
                                        / score_df["total_shipments"] * 100).round(1)
            score_df["avg_delay"] = score_df["avg_delay"].round(1)
            score_df = score_df.sort_values("on_time_rate", ascending=False)

            # Color-coded on-time rate
            fig_score = px.bar(
                score_df, x="supplier_id", y="on_time_rate",
                color="on_time_rate",
                color_continuous_scale=["#ef4444","#f59e0b","#22c55e"],
                range_color=[0,100],
                template="plotly_dark", title="Supplier On-Time Delivery Rate (%)",
                labels={"supplier_id":"Supplier ID","on_time_rate":"On-Time Rate (%)"},
                text="on_time_rate",
            )
            fig_score.update_traces(texttemplate="%{text}%", textposition="outside")
            fig_score.update_layout(**CHART_LAYOUT, margin=dict(l=10,r=10,t=40,b=10), showlegend=False)
            st.plotly_chart(fig_score, use_container_width=True)
            st.dataframe(score_df, use_container_width=True, hide_index=True)
        else:
            st.info("Supplier scorecard requires a `supplier_id` column in your shipments data.")

    # ─────────────────────────────────────────────────────────────────
    # TAB 5 — SUPPLIER MAP
    # ─────────────────────────────────────────────────────────────────
    with tab5:
        st.markdown("### 🌍 Supplier World Map")

        # Try to detect a country column in products or shipments
        map_source = None
        for df, name in [(products_df, "products"), (shipments_df, "shipments")]:
            for col in df.columns:
                if "country" in col.lower() or "location" in col.lower() or "region" in col.lower():
                    map_source = (df, col, name)
                    break

        if map_source:
            df_map, col_map, source_name = map_source
            country_counts = df_map[col_map].value_counts().reset_index()
            country_counts.columns = ["location","count"]
            fig_map = px.choropleth(
                country_counts, locations="location",
                locationmode="country names",
                color="count",
                color_continuous_scale=["#1e1b4b","#6366f1","#06b6d4"],
                template="plotly_dark",
                title=f"Supplier Distribution by {col_map} (from {source_name})",
            )
            fig_map.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                geo=dict(bgcolor="rgba(15,14,23,0.8)", showframe=False,
                         showcoastlines=True, coastlinecolor="#334155",
                         landcolor="#1e1b4b", oceancolor="#0f0e17", showocean=True),
                font=dict(family="Inter", color="#e2e8f0"),
                margin=dict(l=0, r=0, t=40, b=0),
            )
            st.plotly_chart(fig_map, use_container_width=True)
        else:
            st.info("No `country`, `location`, or `region` column detected in your data. Add one to see the map.")

    # ─────────────────────────────────────────────────────────────────
    # TAB 6 — SQL CONSOLE
    # ─────────────────────────────────────────────────────────────────
    with tab6:
        st.markdown("### 🗿 MySQL Console")
        st.markdown('<p style="color:#64748b;font-size:0.85rem;">Run raw SQL against your connected database.</p>',
                    unsafe_allow_html=True)
        query = st.text_area("SQL Query", "SELECT * FROM users;", height=120)
        if st.button("▶ Run Query"):
            with st.spinner("Executing..."):
                try:
                    conn = mysql.connector.connect(**DB_CONFIG)
                    df   = pd.read_sql(query, conn)
                    conn.close()
                    st.success(f"✅ Returned {len(df)} rows")
                    st.dataframe(df, use_container_width=True)
                except Error as e:
                    st.error(f"❌ Query Error: {e}")

    # ─────────────────────────────────────────────────────────────────
    # TAB 7 — NOTIFICATIONS
    # ─────────────────────────────────────────────────────────────────
    with tab7:
        # ── Admin password gate ──────────────────────────────────────
        if "notif_unlocked" not in st.session_state:
            st.session_state.notif_unlocked = False

        if not st.session_state.notif_unlocked:
            st.markdown("""
            <div style="background:linear-gradient(135deg,rgba(30,27,75,0.9),rgba(17,24,39,0.95));
                border:1px solid rgba(99,102,241,0.35);border-radius:20px;
                padding:2.5rem 2rem;max-width:420px;margin:2rem auto;text-align:center;
                animation:fadeInUp 0.6s ease both;
                box-shadow:0 20px 60px rgba(0,0,0,0.5),0 0 40px rgba(99,102,241,0.1);">
                <div style="font-size:2.5rem;margin-bottom:0.5rem;">🔒</div>
                <h3 style="color:#e2e8f0;margin:0.3rem 0;">Admin Access Required</h3>
                <p style="color:#64748b;font-size:0.85rem;margin:0.5rem 0 1.5rem;">
                    This section is restricted. Enter the admin password to continue.
                </p>
            </div>""", unsafe_allow_html=True)
            _, mid_col, _ = st.columns([1, 1.2, 1])
            with mid_col:
                pwd = st.text_input("🔑 Admin Password", type="password", key="notif_pwd")
                if st.button("Unlock →", use_container_width=True, key="notif_unlock_btn"):
                    if pwd == st.secrets.get("NOTIF_PASSWORD", ""):
                        st.session_state.notif_unlocked = True
                        st.rerun()
                    else:
                        st.error("❌ Incorrect password")

                st.markdown("<div style='text-align:center;margin-top:1rem;'>", unsafe_allow_html=True)
                st.markdown("<p style='color:#475569;font-size:0.8rem;margin-bottom:0.5rem;'>Don\'t have access?</p>", unsafe_allow_html=True)
                if st.button("�� Request Admin Access", use_container_width=True, key="request_access_btn"):
                    requester = st.session_state.get("username", "Unknown user")
                    requester_email = st.session_state.get("user_email", "Not saved")
                    body = f"""
                    <p style="color:#94a3b8;">A user has requested admin access to the Notifications tab on <strong style="color:#a5b4fc;">Traqify</strong>.</p>
                    <table style="margin-top:12px;background:rgba(0,0,0,0.3);border-radius:8px;overflow:hidden;width:100%;border-collapse:collapse;">
                        <tr style="background:rgba(99,102,241,0.2);">
                            <th style="padding:10px 14px;color:#a5b4fc;text-align:left;">Field</th>
                            <th style="padding:10px 14px;color:#a5b4fc;text-align:left;">Value</th>
                        </tr>
                        <tr>
                            <td style="padding:8px 14px;color:#94a3b8;">Username</td>
                            <td style="padding:8px 14px;color:#e2e8f0;">{requester}</td>
                        </tr>
                        <tr>
                            <td style="padding:8px 14px;color:#94a3b8;">Email</td>
                            <td style="padding:8px 14px;color:#e2e8f0;">{requester_email}</td>
                        </tr>
                    </table>
                    <p style="color:#64748b;font-size:0.82rem;margin-top:16px;">
                        Reply to their email or share the admin password if you approve this request.
                    </p>"""
                    html = email_template("🔐 Admin Access Request", body)
                    ok = send_email("sashankmidhun@gmail.com", f"🔐 Admin Access Request from {requester}", html)
                    if ok:
                        st.success("✅ Request sent! The admin will get back to you.")
                st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("### 📧 Email Notifications")
        st.markdown("""
        <p style="color:#94a3b8;margin-bottom:1.5rem;">
            Save your email below to receive alerts. Admin access required to send reports.
        </p>""", unsafe_allow_html=True)

        # Pre-fill from saved email, allow update
        saved_email = st.session_state.get("user_email", "")
        email_input = st.text_input("📬 Your Email Address", value=saved_email, placeholder="you@example.com")

        save_col, _ = st.columns([1, 3])
        with save_col:
            if st.button("💾 Save Email", key="save_email_btn"):
                if email_input:
                    try:
                        conn   = mysql.connector.connect(**DB_CONFIG)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE users SET email=%s WHERE username=%s",
                                       (email_input, st.session_state.username))
                        conn.commit(); cursor.close(); conn.close()
                        st.session_state.user_email = email_input
                        st.success("✅ Email saved!")
                    except Exception as e:
                        st.error(f"Could not save: {e}")
                else:
                    st.warning("Enter an email first.")

        if email_input:
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

            # Admin-only send section
            if not st.session_state.notif_unlocked:
                st.markdown("""
                <div style="background:rgba(99,102,241,0.08);border:1px dashed rgba(99,102,241,0.3);
                    border-radius:12px;padding:1.2rem;text-align:center;">
                    <div style="font-size:1.5rem;">🔒</div>
                    <p style="color:#64748b;margin:0.4rem 0 0;font-size:0.85rem;">
                        Enter the admin password above to send alerts and reports.
                    </p>
                </div>""", unsafe_allow_html=True)
            else:
                st.markdown("#### Choose what to send:")
                col_n1, col_n2, col_n3 = st.columns(3)

                with col_n1:
                    st.markdown("""
                    <div style="background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.3);
                        border-radius:12px;padding:1.2rem;text-align:center;margin-bottom:0.8rem;">
                        <div style="font-size:1.8rem;">⚠️</div>
                        <div style="color:#f87171;font-weight:600;margin-top:4px;">Low Stock Alert</div>
                        <div style="color:#64748b;font-size:0.8rem;margin-top:4px;">
                            Sends a list of all products below reorder level
                        </div>
                    </div>""", unsafe_allow_html=True)
                    low_stock_df = products_df[products_df["stock_quantity"] < products_df["reorder_level"]]
                    if st.button("📤 Send Low Stock Alert", use_container_width=True, key="btn_stock"):
                        if low_stock_df.empty:
                            st.info("No low stock items to report.")
                        else:
                            with st.spinner("Sending..."):
                                ok = send_low_stock_alert(email_input, low_stock_df)
                            if ok:
                                st.success(f"✅ Sent to {email_input}")

                with col_n2:
                    st.markdown("""
                    <div style="background:rgba(251,146,60,0.1);border:1px solid rgba(251,146,60,0.3);
                        border-radius:12px;padding:1.2rem;text-align:center;margin-bottom:0.8rem;">
                        <div style="font-size:1.8rem;">🚨</div>
                        <div style="color:#fb923c;font-weight:600;margin-top:4px;">Delay Alert</div>
                        <div style="color:#64748b;font-size:0.8rem;margin-top:4px;">
                            Sends details of all delayed shipments
                        </div>
                    </div>""", unsafe_allow_html=True)
                    delayed_df = shipments_df[shipments_df["delay_days"] > 0]
                    if st.button("📤 Send Delay Alert", use_container_width=True, key="btn_delay"):
                        if delayed_df.empty:
                            st.info("No delayed shipments to report.")
                        else:
                            with st.spinner("Sending..."):
                                ok = send_delay_alert(email_input, delayed_df)
                            if ok:
                                st.success(f"✅ Sent to {email_input}")

                with col_n3:
                    st.markdown("""
                    <div style="background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.3);
                        border-radius:12px;padding:1.2rem;text-align:center;margin-bottom:0.8rem;">
                        <div style="font-size:1.8rem;">📊</div>
                        <div style="color:#a5b4fc;font-weight:600;margin-top:4px;">Summary Report</div>
                        <div style="color:#64748b;font-size:0.8rem;margin-top:4px;">
                            Full dashboard KPI summary in your inbox
                        </div>
                    </div>""", unsafe_allow_html=True)
                    if st.button("📤 Send Summary Report", use_container_width=True, key="btn_summary"):
                        with st.spinner("Sending..."):
                            ok = send_summary_email(email_input, total_rev, delayed_count, low_stock, product_count)
                        if ok:
                            st.success(f"✅ Sent to {email_input}")

            # ── Send report to a specific user ──────────────────────
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown("#### 📤 Send Report to a Specific User")
            st.markdown("<p style=\'color:#64748b;font-size:0.85rem;\'>Look up a registered user and send them a report directly.</p>", unsafe_allow_html=True)

            try:
                conn_u = mysql.connector.connect(**DB_CONFIG)
                users_df = pd.read_sql("SELECT username, email FROM users WHERE email IS NOT NULL AND email != ''", conn_u)
                conn_u.close()
            except Exception:
                users_df = pd.DataFrame(columns=["username","email"])

            if users_df.empty:
                st.info("No users with saved emails found.")
            else:
                user_options = {f"{row.username} ({row.email})": row.email for _, row in users_df.iterrows()}
                selected_user = st.selectbox("👤 Select User", list(user_options.keys()), key="admin_user_select")
                target_email  = user_options[selected_user]
                report_type   = st.selectbox("📊 Report Type", ["Low Stock Alert", "Shipment Delay Alert", "Summary Report"], key="admin_report_type")

                if st.button("📤 Send to User", use_container_width=False, key="admin_send_btn"):
                    with st.spinner(f"Sending {report_type} to {target_email}..."):
                        if report_type == "Low Stock Alert":
                            ls_df = products_df[products_df["stock_quantity"] < products_df["reorder_level"]]
                            ok = send_low_stock_alert(target_email, ls_df) if not ls_df.empty else False
                            if ls_df.empty: st.info("No low stock items to report.")
                        elif report_type == "Shipment Delay Alert":
                            dl_df = shipments_df[shipments_df["delay_days"] > 0]
                            ok = send_delay_alert(target_email, dl_df) if not dl_df.empty else False
                            if dl_df.empty: st.info("No delayed shipments to report.")
                        else:
                            ok = send_summary_email(target_email, total_rev, delayed_count, low_stock, product_count)
                    if ok:
                        st.success(f"✅ {report_type} sent to {target_email}")

            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            st.markdown("""
            <div style="background:rgba(15,14,23,0.6);border:1px solid rgba(99,102,241,0.15);
                border-radius:10px;padding:1rem 1.2rem;">
                <p style="color:#475569;font-size:0.8rem;margin:0;">
                    ⚙️ <strong style="color:#64748b;">Setup required:</strong>
                    Add <code style="color:#a5b4fc;">RESEND_API_KEY</code> to your Streamlit secrets.
                    Get a free key at <a href="https://resend.com" style="color:#6366f1;">resend.com</a> (free tier: 100 emails/day).
                </p>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background:rgba(99,102,241,0.05);border:1px dashed rgba(99,102,241,0.3);
                border-radius:12px;padding:2rem;text-align:center;">
                <div style="font-size:2.5rem;margin-bottom:0.5rem;">📬</div>
                <p style="color:#64748b;margin:0;">Enter your email address above to get started.</p>
            </div>""", unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;color:#334155;font-size:0.78rem;padding:0.5rem 0 1rem 0;">
        Traqify · Built with Streamlit & MySQL
    </div>""", unsafe_allow_html=True)


# ====================================================================
# 7. ROUTER
# ====================================================================
if not st.session_state.logged_in:
    auth_page()
else:
    main_dashboard()
