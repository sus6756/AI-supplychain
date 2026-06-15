# Traqify v3.1 - clean
import io
import time
import datetime
import smtplib
import requests
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sklearn.linear_model import LinearRegression
import mysql.connector
from mysql.connector import Error

# ====================================================================
# 1. PAGE & SESSION STATE INITIALIZATION
# ====================================================================
st.set_page_config(page_title="Supply Chain AI Enterprise", layout="wide", page_icon="🚛")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "username" not in st.session_state:
    st.session_state.username = ""
if "notif_unlocked" not in st.session_state:
    st.session_state.notif_unlocked = False
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
            password VARCHAR(255) NOT NULL);""")
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

# ====================================================================
# 3b. ACTIVITY LOG & PDF & GSHEET HELPERS
# ====================================================================

def init_activity_log():
    """Create activity_log and email_schedules tables if they don't exist."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("""CREATE TABLE IF NOT EXISTS activity_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255),
            action TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP);""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            sender VARCHAR(255),
            message TEXT,
            reply TEXT DEFAULT NULL,
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            replied_at TIMESTAMP NULL
        );""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS email_schedules (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) UNIQUE,
            email VARCHAR(255),
            day_of_week VARCHAR(20));""")
        conn.commit(); cursor.close(); conn.close()
    except Error:
        pass  # silently skip if DB unavailable at startup


def log_activity(username: str, action: str):
    """Insert a row into the activity_log table."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO activity_log (username, action) VALUES (%s, %s)", (username, action))
        conn.commit(); cursor.close(); conn.close()
    except Exception:
        pass  # non-critical — never break the UI


def get_activity_log(limit: int = 200) -> pd.DataFrame:
    """Return the latest `limit` rows from activity_log as a DataFrame."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql(
            "SELECT username, action, timestamp FROM activity_log ORDER BY timestamp DESC LIMIT %s",
            conn,
            params=(limit,),
        )
        conn.close()
        return df
    except Exception:
        return pd.DataFrame(columns=["username", "action", "timestamp"])


def generate_pdf_report(total_rev, delayed, low_stock, products, username: str):
    """Generate a PDF summary report using fpdf2. Returns bytes or None."""
    try:
        from fpdf import FPDF  # fpdf2
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(0, 12, "Supply Chain AI - Dashboard Report", ln=True, align="C")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}   User: {username}", ln=True, align="C")
        pdf.ln(6)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 10, "KPI Summary", ln=True)
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, f"Total Revenue:        ${total_rev:,.2f}", ln=True)
        pdf.cell(0, 8, f"Delayed Shipments:    {delayed}", ln=True)
        pdf.cell(0, 8, f"Low Stock Items:      {low_stock}", ln=True)
        pdf.cell(0, 8, f"Total Products:       {products}", ln=True)
        pdf.ln(4)
        pdf.set_font("Helvetica", "I", 9)
        pdf.cell(0, 8, "Supply Chain AI Enterprise · Built with Streamlit & MySQL", ln=True, align="C")
        return pdf.output()
    except ImportError:
        return None
    except Exception:
        return None


def load_from_gsheet(url: str):
    """Fetch a public Google Sheet as CSV and return (DataFrame, 'ok') or (None, error_msg)."""
    try:
        if not url:
            return None, "No URL provided."
        # Convert /edit or /pub URL to CSV export URL
        if "/edit" in url or "/pub" in url:
            base = url.split("/edit")[0].split("/pub")[0]
            csv_url = base + "/export?format=csv"
        elif "spreadsheets/d/" in url:
            csv_url = url.rstrip("/") + "/export?format=csv"
        else:
            csv_url = url
        resp = requests.get(csv_url, timeout=15)
        resp.raise_for_status()
        df = pd.read_csv(io.StringIO(resp.text))
        return df, "ok"
    except Exception as e:
        return None, str(e)


# ====================================================================
# 3c. EMAIL HELPERS
# ====================================================================

def email_template(title: str, body_html: str) -> str:
    return f"""
    <html><body style="background:#0f0e17;font-family:Inter,sans-serif;padding:2rem;">
    <div style="max-width:600px;margin:auto;background:#1e1b4b;border-radius:14px;padding:2rem;">
      <h2 style="color:#a5b4fc;margin-top:0;">{title}</h2>
      {body_html}
      <hr style="border-color:#334155;margin:1.5rem 0;">
      <p style="color:#475569;font-size:0.78rem;margin:0;">Supply Chain AI Enterprise · Traqify</p>
    </div></body></html>"""


def send_email(to: str, subject: str, html: str) -> bool:
    try:
        sender = st.secrets.get("EMAIL_SENDER", "")
        app_pw = st.secrets.get("EMAIL_APP_PASSWORD", "")
        if not sender or not app_pw:
            return False
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = sender
        msg["To"]      = to
        msg.attach(MIMEText(html, "html"))
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, app_pw)
            server.sendmail(sender, to, msg.as_string())
        return True
    except Exception:
        return False


def send_low_stock_alert(to: str, df: pd.DataFrame) -> bool:
    rows = "".join(
        f"<tr><td style='padding:6px 12px;color:#e2e8f0;'>{r.get('product_name','?')}</td>"
        f"<td style='padding:6px 12px;color:#f87171;text-align:right;'>{r.get('stock_quantity','?')}</td>"
        f"<td style='padding:6px 12px;color:#94a3b8;text-align:right;'>{r.get('reorder_level','?')}</td></tr>"
        for _, r in df.iterrows()
    )
    body = f"""
    <p style='color:#94a3b8;'>The following items are below reorder level:</p>
    <table style='width:100%;border-collapse:collapse;'>
      <thead><tr>
        <th style='padding:6px 12px;color:#a5b4fc;text-align:left;'>Product</th>
        <th style='padding:6px 12px;color:#a5b4fc;text-align:right;'>Stock</th>
        <th style='padding:6px 12px;color:#a5b4fc;text-align:right;'>Reorder Level</th>
      </tr></thead><tbody>{rows}</tbody>
    </table>"""
    return send_email(to, "⚠️ Low Stock Alert — Supply Chain AI", email_template("⚠️ Low Stock Alert", body))


def send_delay_alert(to: str, df: pd.DataFrame) -> bool:
    rows = "".join(
        f"<tr><td style='padding:6px 12px;color:#e2e8f0;'>{r.get('shipment_id','?')}</td>"
        f"<td style='padding:6px 12px;color:#fb923c;text-align:right;'>{r.get('delay_days','?')} days</td></tr>"
        for _, r in df.iterrows()
    )
    body = f"""
    <p style='color:#94a3b8;'>The following shipments are delayed:</p>
    <table style='width:100%;border-collapse:collapse;'>
      <thead><tr>
        <th style='padding:6px 12px;color:#a5b4fc;text-align:left;'>Shipment ID</th>
        <th style='padding:6px 12px;color:#a5b4fc;text-align:right;'>Delay</th>
      </tr></thead><tbody>{rows}</tbody>
    </table>"""
    return send_email(to, "🚚 Shipment Delay Alert — Supply Chain AI", email_template("🚚 Delay Alert", body))


def send_summary_email(to: str, total_rev, delayed, low_stock, products) -> bool:
    body = f"""
    <p style='color:#94a3b8;'>Here is your dashboard summary:</p>
    <table style='width:100%;'>
      <tr><td style='color:#94a3b8;padding:6px 0;'>💰 Total Revenue</td>
          <td style='color:#a5b4fc;text-align:right;font-weight:600;'>${total_rev:,.2f}</td></tr>
      <tr><td style='color:#94a3b8;padding:6px 0;'>⚠️ Delayed Shipments</td>
          <td style='color:#f87171;text-align:right;font-weight:600;'>{delayed}</td></tr>
      <tr><td style='color:#94a3b8;padding:6px 0;'>📉 Low Stock Items</td>
          <td style='color:#fb923c;text-align:right;font-weight:600;'>{low_stock}</td></tr>
      <tr><td style='color:#94a3b8;padding:6px 0;'>📦 Total Products</td>
          <td style='color:#34d399;text-align:right;font-weight:600;'>{products}</td></tr>
    </table>"""
    return send_email(to, "📊 Dashboard Summary — Supply Chain AI", email_template("📊 Dashboard Summary", body))



# ====================================================================
# 3d. INIT CALLS
# ====================================================================
init_db()
init_supply_chain_tables()
init_activity_log()

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


def detect_anomalies(sales_df, threshold=2.0):
    df = sales_df.copy()
    df["month_dt"] = df["sale_date"].dt.to_period("M").dt.to_timestamp()
    monthly = df.groupby("month_dt")["revenue"].sum().reset_index()
    mean, std = monthly["revenue"].mean(), monthly["revenue"].std()
    monthly["z_score"] = (monthly["revenue"] - mean) / std if std else 0.0
    monthly["anomaly"] = monthly["z_score"].abs() > threshold
    monthly["type"] = monthly.apply(
        lambda r: "Spike" if r["z_score"] > threshold
                  else ("Drop" if r["z_score"] < -threshold else "Normal"), axis=1)
    return monthly

def detect_delay_anomalies(shipments_df, threshold=2.0):
    if "supplier_id" not in shipments_df.columns:
        return pd.DataFrame()
    sup = shipments_df.groupby("supplier_id")["delay_days"].mean().reset_index()
    sup.columns = ["supplier_id","avg_delay"]
    mean, std = sup["avg_delay"].mean(), sup["avg_delay"].std()
    sup["z_score"] = (sup["avg_delay"] - mean) / std if std else 0.0
    sup["flag"] = sup["z_score"].apply(
        lambda z: "Critical" if z > threshold else ("Watch" if z > 1 else "Normal"))
    return sup.sort_values("avg_delay", ascending=False)

def smart_reorder(products_df, sales_df, days_ahead=30):
    if "product_id" not in sales_df.columns or "quantity_sold" not in sales_df.columns:
        return pd.DataFrame()
    date_range = max((sales_df["sale_date"].max() - sales_df["sale_date"].min()).days, 1)
    velocity = (sales_df.groupby("product_id")["quantity_sold"].sum() / date_range).reset_index()
    velocity.columns = ["product_id","daily_sales"]
    m = products_df.merge(velocity, on="product_id", how="left")
    m["daily_sales"] = m["daily_sales"].fillna(0)
    m["days_until_out"] = m.apply(
        lambda r: round(r["stock_quantity"] / r["daily_sales"]) if r["daily_sales"] > 0 else 9999, axis=1)
    m["urgency"] = m["days_until_out"].apply(
        lambda d: "Order Now" if d <= 7 else ("Soon" if d <= days_ahead else ("Watch" if d <= days_ahead*2 else "OK")))
    m["units_to_order"] = m.apply(
        lambda r: max(0, int(r["daily_sales"]*days_ahead*1.2) - r["stock_quantity"]) if r["daily_sales"] > 0 else 0, axis=1)
    cols = ["product_id"] + (["product_name"] if "product_name" in m.columns else []) + ["stock_quantity","daily_sales","days_until_out","urgency","units_to_order"]
    return m[cols].sort_values("days_until_out")


# ====================================================================
# 5. AUTH PAGE
# ====================================================================
def auth_page():
    st.markdown("""
    <div style="text-align:center; animation:fadeInDown 0.8s ease both; padding:2rem 0 1rem 0;">
        <div style="font-size:3.5rem;">🚛</div>
        <h1 style="font-size:2.4rem; margin:0.3rem 0;">Supply Chain AI</h1>
        <p style="color:#94a3b8; font-size:1rem; margin:0;">Enterprise Intelligence Platform</p>
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
                        cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
                        row = cursor.fetchone(); cursor.close(); conn.close()
                    if row and row[0] == password:
                        st.success("✅ Login successful! Loading dashboard...")
                        time.sleep(0.6)
                        st.session_state.logged_in = True
                        st.session_state.username = username
                        st.session_state.notif_unlocked = False
                        log_activity(username, "Login")
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
                if st.form_submit_button("Create Account →", use_container_width=True):
                    with st.spinner("Creating account..."):
                        conn   = mysql.connector.connect(**DB_CONFIG)
                        cursor = conn.cursor()
                        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
                        exists = cursor.fetchone()
                        if exists:
                            st.error("⚠️ Username already exists")
                        else:
                            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
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
        <div style="font-size:2.5rem;">🚛</div>
        <h3 style="color:#a5b4fc;margin:0.3rem 0;font-size:1.4rem;font-weight:800;letter-spacing:1px;">Traqify</h3>
        <p style="color:#6366f1;font-size:0.78rem;margin:0;font-weight:600;letter-spacing:2px;text-transform:uppercase;">Dashboard</p>
    </div>
    <hr style="border-color:rgba(99,102,241,0.3);margin:0.8rem 0;">
    """, unsafe_allow_html=True)

    if st.sidebar.button("🚪 Logout", use_container_width=True):
        log_activity(st.session_state.get("username", "?"), "Logout")
        st.session_state.logged_in = False
        st.rerun()

    st.sidebar.markdown("---")
    option = st.sidebar.radio("📂 Upload Type", ["Excel", "CSV"])

    # ── Hero Banner ───────────────────────────────────────────────────
    st.markdown("""
    <div class="hero-banner">
        <h2>🚛 Supply Chain Intelligence Dashboard</h2>
        <p>Real-time analytics · Inventory management · Shipment tracking · Demand forecasting</p>
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
            log_activity(st.session_state.get("username", "?"), "Uploaded Excel file")
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
            log_activity(st.session_state.get("username", "?"), "Uploaded CSV files")

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
        "📧 Hub",
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
        fig_bar.update_layout(**CHART_LAYOUT)
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
            fig_fc.update_layout(**CHART_LAYOUT, showlegend=True)
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
            fig_stock.update_layout(**CHART_LAYOUT, margin=dict(l=10,r=10,t=40,b=80))
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
                fig_donut.update_layout(**CHART_LAYOUT, showlegend=True)
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
            fig_scatter.update_layout(**CHART_LAYOUT)
            st.plotly_chart(fig_scatter, use_container_width=True)
        with c_b:
            delay_hist = px.histogram(
                shipments_df[shipments_df["delay_days"].notna()],
                x="delay_days", nbins=20,
                color_discrete_sequence=["#6366f1"],
                template="plotly_dark", title="Delay Days Distribution",
                labels={"delay_days":"Delay (days)"},
            )
            delay_hist.update_layout(**CHART_LAYOUT)
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
            fig_score.update_layout(**CHART_LAYOUT)
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
        if st.session_state.get("username","") == "lunalupa":
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
        else:
            st.markdown("""
            <div style="background:rgba(99,102,241,0.05);border:1px dashed rgba(99,102,241,0.3);
                border-radius:12px;padding:2rem;text-align:center;">
                <div style="font-size:2.5rem;">🔒</div>
                <p style="color:#64748b;margin:0.5rem 0 0;">SQL Console is restricted to admin only.</p>
            </div>""", unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;color:#334155;font-size:0.78rem;padding:0.5rem 0 1rem 0;">
        Supply Chain AI Enterprise · Built with Streamlit & MySQL
    </div>""", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────
    # TAB 7 — HUB
    # ─────────────────────────────────────────────────────────────────
    with tab7:
        # Admin password gate (only for lunalupa)
        if "notif_unlocked" not in st.session_state:
            st.session_state.notif_unlocked = False

        _is_admin_check = st.session_state.get("username", "") == "lunalupa"
        if _is_admin_check and not st.session_state.notif_unlocked:
            st.markdown("#### 🔒 Admin Access")
            notif_pass = st.text_input("Admin password", type="password", key="notif_pass_input")
            col_unlock, col_req = st.columns([1, 2])
            with col_unlock:
                if st.button("🔓 Unlock", key="notif_unlock_btn"):
                    secret_pw = st.secrets.get("NOTIF_PASSWORD", "")
                    if notif_pass == secret_pw:
                        st.session_state.notif_unlocked = True
                        st.success("✅ Unlocked!")
                        st.rerun()
                    else:
                        st.error("❌ Wrong password.")
            with col_req:
                if st.button("📨 Request Admin Access", key="notif_req_access_btn"):
                    req_user = st.session_state.get("username", "Unknown")
                    body = f"<p style='color:#94a3b8;'>User <strong>{req_user}</strong> is requesting admin access to the Hub.</p>"
                    html = email_template("🔒 Admin Access Request", body)
                    send_email("sashankmidhun@gmail.com", f"Admin Access Request from {req_user}", html)
                    st.info("📨 Request sent to admin.")

        st.markdown("### 📧 Email Notifications")
        st.markdown("<p style='color:#94a3b8;'>Save your email to receive alerts and request reports.</p>", unsafe_allow_html=True)

        saved_email = st.session_state.get("user_email", "")
        email_input = st.text_input("📬 Your Email Address", value=saved_email, placeholder="you@example.com")

        save_col, _ = st.columns([1, 3])
        with save_col:
            if st.button("💾 Save Email", key="save_email_btn"):
                if email_input:
                    try:
                        conn = mysql.connector.connect(**DB_CONFIG)
                        cursor = conn.cursor()
                        cursor.execute("UPDATE users SET email=%s WHERE username=%s", (email_input, st.session_state.username))
                        conn.commit(); cursor.close(); conn.close()
                        st.session_state.user_email = email_input
                        st.success("✅ Email saved!")
                        log_activity(st.session_state.get("username", "?"), f"Saved email: {email_input}")
                    except Exception as e:
                        st.error(f"Could not save: {e}")
                else:
                    st.warning("Enter an email first.")

        active_email = email_input or st.session_state.get("user_email", "")

        if active_email:
            st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
            is_admin = st.session_state.get("username", "") == "lunalupa"

            if not is_admin:
                st.markdown("#### 📩 Send Yourself a Report")
                st.markdown("<p style='color:#64748b;font-size:0.85rem;margin-bottom:1rem;'>Send yourself a report or request all reports from the admin.</p>", unsafe_allow_html=True)
                st.markdown("---")
                u_col1, u_col2, u_col3 = st.columns(3)
                with u_col1:
                    if st.button("📤 My Low Stock Report", use_container_width=True, key="u_btn_stock"):
                        ls_df = products_df[products_df["stock_quantity"] < products_df["reorder_level"]]
                        if ls_df.empty:
                            st.info("No low stock items.")
                        else:
                            with st.spinner("Sending..."):
                                ok = send_low_stock_alert(active_email, ls_df)
                            if ok:
                                st.success(f"✅ Sent to {active_email}")
                with u_col2:
                    if st.button("📤 My Delay Report", use_container_width=True, key="u_btn_delay"):
                        dl_df = shipments_df[shipments_df["delay_days"] > 0]
                        if dl_df.empty:
                            st.info("No delays.")
                        else:
                            with st.spinner("Sending..."):
                                ok = send_delay_alert(active_email, dl_df)
                            if ok:
                                st.success(f"✅ Sent to {active_email}")
                with u_col3:
                    if st.button("📤 My Summary Report", use_container_width=True, key="u_btn_summary"):
                        with st.spinner("Sending..."):
                            ok = send_summary_email(active_email, total_rev, delayed_count, low_stock, product_count)
                        if ok:
                            st.success(f"✅ Sent to {active_email}")

            if is_admin and not st.session_state.notif_unlocked:
                st.markdown("""<div style="background:rgba(99,102,241,0.08);border:1px dashed rgba(99,102,241,0.3);border-radius:12px;padding:1.2rem;text-align:center;"><div style="font-size:1.5rem;">🔒</div><p style="color:#64748b;margin:0.4rem 0 0;font-size:0.85rem;">Enter the admin password above to access the admin panel.</p></div>""", unsafe_allow_html=True)
            elif is_admin:
                st.markdown("#### Choose what to send:")
                col_n1, col_n2, col_n3 = st.columns(3)
                with col_n1:
                    low_stock_df = products_df[products_df["stock_quantity"] < products_df["reorder_level"]]
                    if st.button("📤 Send Low Stock Alert", use_container_width=True, key="btn_stock"):
                        if low_stock_df.empty:
                            st.info("No low stock items.")
                        else:
                            with st.spinner("Sending..."):
                                ok = send_low_stock_alert(active_email, low_stock_df)
                            if ok:
                                st.success(f"✅ Sent to {active_email}")
                with col_n2:
                    delayed_df = shipments_df[shipments_df["delay_days"] > 0]
                    if st.button("📤 Send Delay Alert", use_container_width=True, key="btn_delay"):
                        if delayed_df.empty:
                            st.info("No delays.")
                        else:
                            with st.spinner("Sending..."):
                                ok = send_delay_alert(active_email, delayed_df)
                            if ok:
                                st.success(f"✅ Sent to {active_email}")
                with col_n3:
                    if st.button("📤 Send Summary Report", use_container_width=True, key="btn_summary"):
                        with st.spinner("Sending..."):
                            ok = send_summary_email(active_email, total_rev, delayed_count, low_stock, product_count)
                        if ok:
                            st.success(f"✅ Sent to {active_email}")

                # Send to specific user (admin only)
                if st.session_state.get("username", "") == "lunalupa":
                    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                    st.markdown("#### 📤 Send Report to a Specific User")
                    try:
                        conn_u = mysql.connector.connect(**DB_CONFIG)
                        users_df_notif = pd.read_sql("SELECT username, email FROM users WHERE email IS NOT NULL AND email != ''", conn_u)
                        conn_u.close()
                    except Exception:
                        users_df_notif = pd.DataFrame(columns=["username", "email"])
                    if not users_df_notif.empty:
                        user_options = {f"{row.username} ({row.email})": row.email for _, row in users_df_notif.iterrows()}
                        selected_user = st.selectbox("👤 Select User", list(user_options.keys()), key="admin_user_select")
                        target_email = user_options[selected_user]
                        report_type = st.selectbox("📊 Report Type", ["Low Stock Alert", "Shipment Delay Alert", "Summary Report"], key="admin_report_type")
                        if st.button("📤 Send to User", key="admin_send_btn"):
                            with st.spinner(f"Sending {report_type} to {target_email}..."):
                                if report_type == "Low Stock Alert":
                                    ls_df = products_df[products_df["stock_quantity"] < products_df["reorder_level"]]
                                    ok = send_low_stock_alert(target_email, ls_df) if not ls_df.empty else False
                                elif report_type == "Shipment Delay Alert":
                                    dl_df = shipments_df[shipments_df["delay_days"] > 0]
                                    ok = send_delay_alert(target_email, dl_df) if not dl_df.empty else False
                                else:
                                    ok = send_summary_email(target_email, total_rev, delayed_count, low_stock, product_count)
                            if ok:
                                st.success(f"✅ {report_type} sent to {target_email}")
                            log_activity(st.session_state.get("username", "?"), f"Sent {report_type} to {target_email}")


                st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
                st.markdown("#### 👥 User Management")
                try:
                    conn_um = mysql.connector.connect(**DB_CONFIG)
                    um_df = pd.read_sql("SELECT id, username, email FROM users ORDER BY id", conn_um)
                    conn_um.close()
                except Exception as e:
                    um_df = pd.DataFrame()
                    st.error(f"Could not load users: {e}")
                if not um_df.empty:
                    st.dataframe(um_df, use_container_width=True, hide_index=True)
                    st.markdown("---")
                    col_um1, col_um2 = st.columns(2)
                    with col_um1:
                        st.markdown("**🗑️ Delete User**")
                        del_options = [u for u in um_df["username"].tolist() if u != "lunalupa"]
                        if del_options:
                            del_user = st.selectbox("Select user to delete", del_options, key="del_user_select")
                            if st.button("🗑️ Delete", key="del_user_btn"):
                                try:
                                    conn_d = mysql.connector.connect(**DB_CONFIG)
                                    cursor_d = conn_d.cursor()
                                    cursor_d.execute("DELETE FROM users WHERE username=%s", (del_user,))
                                    conn_d.commit(); cursor_d.close(); conn_d.close()
                                    log_activity("lunalupa", f"Deleted user: {del_user}")
                                    st.success(f"✅ Deleted {del_user}")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")
                        else:
                            st.info("No other users to delete.")
                    with col_um2:
                        st.markdown("**🔑 Reset Password**")
                        reset_user = st.selectbox("Select user", um_df["username"].tolist(), key="reset_user_select")
                        new_pw = st.text_input("New Password", type="password", key="reset_pw")
                        if st.button("🔑 Reset Password", key="reset_pw_btn"):
                            if new_pw:
                                try:
                                    conn_r = mysql.connector.connect(**DB_CONFIG)
                                    cursor_r = conn_r.cursor()
                                    cursor_r.execute("UPDATE users SET password=%s WHERE username=%s", (new_pw, reset_user))
                                    conn_r.commit(); cursor_r.close(); conn_r.close()
                                    log_activity("lunalupa", f"Reset password for: {reset_user}")
                                    st.success(f"✅ Password reset for {reset_user}")
                                except Exception as e:
                                    st.error(f"Error: {e}")
                            else:
                                st.warning("Enter a new password first.")

        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

        with st.expander("📑 PDF Export & Google Sheets", expanded=False):
            col_pdf, col_sheets = st.columns(2)
            with col_pdf:
                st.markdown("#### 📄 Download PDF Report")
                pdf_bytes = generate_pdf_report(total_rev, delayed_count, low_stock, product_count, st.session_state.get("username", "user"))
                if pdf_bytes:
                    st.download_button("📥 Download PDF", data=bytes(pdf_bytes), file_name=f"traqify_{datetime.date.today()}.pdf", mime="application/pdf", use_container_width=True)
                else:
                    st.warning("fpdf2 not installed. Add fpdf2>=2.7.0 to requirements.txt")
            with col_sheets:
                st.markdown("#### 📊 Load from Google Sheets")
                sheet_url = st.text_input("📎 Sheet URL (public)", placeholder="https://docs.google.com/spreadsheets/d/...", key="gsheet_url")
                sheet_type = st.selectbox("Load as", ["Sales", "Products", "Shipments"], key="gsheet_type")
                if st.button("🔄 Load from Google Sheets", key="load_gsheet"):
                    with st.spinner("Fetching..."):
                        df_gs, msg = load_from_gsheet(sheet_url)
                    if msg == "ok":
                        st.success(f"✅ Loaded {len(df_gs)} rows")
                        st.dataframe(df_gs, use_container_width=True, height=200)
                        log_activity(st.session_state.get("username", "?"), f"Loaded {sheet_type} from Google Sheets")
                    else:
                        st.error(f"❌ {msg}")

        with st.expander("📅 Schedule Weekly Email Report", expanded=False):
            sched_col1, sched_col2 = st.columns(2)
            with sched_col1:
                sched_day = st.selectbox("📆 Send every", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"], key="sched_day")
            with sched_col2:
                sched_email = st.text_input("📬 Send to", value=st.session_state.get("user_email", ""), key="sched_email")
            if st.button("💾 Save Schedule", key="save_schedule"):
                if sched_email:
                    try:
                        conn = mysql.connector.connect(**DB_CONFIG)
                        cursor = conn.cursor()
                        cursor.execute("""CREATE TABLE IF NOT EXISTS email_schedules (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            username VARCHAR(255) UNIQUE,
                            email VARCHAR(255),
                            day_of_week VARCHAR(20));""")
                        cursor.execute(
                            "INSERT INTO email_schedules (username, email, day_of_week) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE email=%s, day_of_week=%s",
                            (st.session_state.get("username", "?"), sched_email, sched_day, sched_email, sched_day),
                        )
                        conn.commit(); cursor.close(); conn.close()
                        log_activity(st.session_state.get("username", "?"), f"Scheduled weekly report: {sched_day} to {sched_email}")
                        st.success(f"✅ Scheduled every {sched_day} → {sched_email}")
                    except Exception as e:
                        st.error(f"Could not save: {e}")
                else:
                    st.warning("Enter an email first.")
            if st.session_state.get("username", "") == "lunalupa":
                try:
                    conn = mysql.connector.connect(**DB_CONFIG)
                    sched_df = pd.read_sql("SELECT username, email, day_of_week FROM email_schedules", conn)
                    conn.close()
                    if not sched_df.empty:
                        st.dataframe(sched_df, use_container_width=True, hide_index=True)
                        if st.button("📤 Send Now to All Scheduled Users", key="send_all_sched"):
                            sent = 0
                            for _, row in sched_df.iterrows():
                                ok = send_summary_email(row["email"], total_rev, delayed_count, low_stock, product_count)
                                if ok:
                                    sent += 1
                            st.success(f"✅ Sent to {sent} users")
                except Exception as e:
                    st.info(f"No schedules yet: {e}")

        with st.expander("📋 Activity Log", expanded=False):
            if st.session_state.get("username", "") == "lunalupa":
                log_df = get_activity_log(200)
                if log_df.empty:
                    st.info("No activity yet.")
                else:
                    log_search = st.text_input("🔍 Search", key="log_search")
                    if log_search:
                        mask = log_df.apply(lambda r: r.astype(str).str.contains(log_search, case=False).any(), axis=1)
                        log_df = log_df[mask]
                    st.dataframe(log_df, use_container_width=True, height=400, hide_index=True)
                    st.download_button("📥 Export Log (CSV)", data=log_df.to_csv(index=False).encode(), file_name=f"activity_{datetime.date.today()}.csv", mime="text/csv")
            else:
                st.markdown("""<div style="background:rgba(99,102,241,0.05);border:1px dashed rgba(99,102,241,0.3);border-radius:12px;padding:2rem;text-align:center;"><div style="font-size:2.5rem;">🔒</div><p style="color:#64748b;margin:0.5rem 0 0;">Activity log is admin-only.</p></div>""", unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────

        with st.expander("🤖 AI Insights", expanded=False):
            st.markdown("#### 🤖 AI-Powered Supply Chain Insights")
            ai_t1, ai_t2, ai_t3 = st.tabs(["📈 Revenue Anomalies","🚚 Delay Anomalies","🔮 Smart Reorder"])

            with ai_t1:
                st.markdown("##### Revenue Anomaly Detection")
                thresh = st.slider("Sensitivity (Z-score)", 1.0, 3.0, 2.0, 0.1, key="rev_thresh")
                adf = detect_anomalies(sales_df, thresh)
                color_map = {"Spike":"#22c55e","Drop":"#ef4444","Normal":"#6366f1"}
                fig_a = px.bar(adf, x="month_dt", y="revenue", color="type",
                               color_discrete_map=color_map, template="plotly_dark",
                               title="Monthly Revenue — Anomalies Highlighted",
                               labels={"month_dt":"Month","revenue":"Revenue ($)","type":"Status"})
                fig_a.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                    plot_bgcolor="rgba(15,14,23,0.6)",
                                    font=dict(family="Inter",color="#e2e8f0"),
                                    margin=dict(l=10,r=10,t=40,b=10), showlegend=True)
                st.plotly_chart(fig_a, use_container_width=True)
                flagged = adf[adf["anomaly"]][["month_dt","revenue","z_score","type"]].copy()
                flagged["revenue"] = flagged["revenue"].map("${:,.0f}".format)
                flagged["z_score"] = flagged["z_score"].round(2)
                if not flagged.empty:
                    st.markdown("**🚨 Flagged Months:**")
                    st.dataframe(flagged, use_container_width=True, hide_index=True)
                else:
                    st.success("✅ No anomalies detected.")

            with ai_t2:
                st.markdown("##### Supplier Delay Anomaly Detection")
                d_thresh = st.slider("Sensitivity (Z-score)", 1.0, 3.0, 2.0, 0.1, key="del_thresh")
                ddf = detect_delay_anomalies(shipments_df, d_thresh)
                if ddf.empty:
                    st.info("Need a supplier_id column in shipments data.")
                else:
                    cmap = {"Critical":"#ef4444","Watch":"#f59e0b","Normal":"#22c55e"}
                    fig_d = px.bar(ddf, x="supplier_id", y="avg_delay", color="flag",
                                   color_discrete_map=cmap, template="plotly_dark",
                                   title="Average Delay by Supplier",
                                   text="avg_delay",
                                   labels={"supplier_id":"Supplier","avg_delay":"Avg Delay (days)","flag":"Status"})
                    fig_d.update_traces(texttemplate="%{text:.1f}d", textposition="outside")
                    fig_d.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                        plot_bgcolor="rgba(15,14,23,0.6)",
                                        font=dict(family="Inter",color="#e2e8f0"),
                                        margin=dict(l=10,r=10,t=40,b=10), showlegend=True)
                    st.plotly_chart(fig_d, use_container_width=True)
                    crit = ddf[ddf["flag"]=="Critical"]
                    if not crit.empty:
                        st.markdown("**🚨 Critical Suppliers:**")
                        st.dataframe(crit, use_container_width=True, hide_index=True)
                    else:
                        st.success("✅ No critical suppliers.")

            with ai_t3:
                st.markdown("##### Smart Reorder Predictions")
                days_ahead = st.slider("Planning horizon (days)", 7, 90, 30, key="reorder_days")
                rdf = smart_reorder(products_df, sales_df, days_ahead)
                if rdf.empty:
                    st.info("Need product_id and quantity_sold columns in sales data.")
                else:
                    r1,r2,r3 = st.columns(3)
                    r1.metric("🔴 Order Now", len(rdf[rdf["urgency"]=="Order Now"]))
                    r2.metric("🟠 Soon",      len(rdf[rdf["urgency"]=="Soon"]))
                    r3.metric("🟢 OK",        len(rdf[rdf["urgency"].isin(["Watch","OK"])]))
                    name_c = "product_name" if "product_name" in rdf.columns else "product_id"
                    cmap2 = {"Order Now":"#ef4444","Soon":"#f59e0b","Watch":"#eab308","OK":"#22c55e"}
                    fig_r = px.bar(rdf.head(20), x=name_c, y="days_until_out",
                                   color="urgency", color_discrete_map=cmap2,
                                   template="plotly_dark",
                                   title="Days Until Stock Runs Out (Top 20)",
                                   labels={name_c:"Product","days_until_out":"Days Until Out","urgency":"Status"})
                    fig_r.add_hline(y=days_ahead, line_dash="dash", line_color="#6366f1",
                                    annotation_text=f"Horizon ({days_ahead}d)")
                    fig_r.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                                        plot_bgcolor="rgba(15,14,23,0.6)",
                                        font=dict(family="Inter",color="#e2e8f0"),
                                        margin=dict(l=10,r=10,t=40,b=80), showlegend=True)
                    st.plotly_chart(fig_r, use_container_width=True)
                    uf = st.selectbox("Filter urgency",["All","Order Now","Soon","Watch","OK"],key="urg_filter")
                    show = rdf if uf=="All" else rdf[rdf["urgency"]==uf]
                    st.dataframe(show, use_container_width=True, hide_index=True)
                    st.download_button("📥 Reorder Plan CSV",
                        data=rdf.to_csv(index=False).encode(),
                        file_name=f"reorder_{datetime.date.today()}.csv", mime="text/csv")


        # Message Admin inside Hub
        with st.expander("💬 Message Admin", expanded=False):
        st.markdown("### 💬 Message Admin")
        curr_user = st.session_state.get("username", "")
        st.markdown("<p style='color:#94a3b8;margin-bottom:1rem;'>Send a direct message to the admin. You will receive a reply to your saved email.</p>", unsafe_allow_html=True)
        with st.form("msg_form"):
            msg_text = st.text_area("Your Message", placeholder="Describe your issue, query or feedback...", height=130)
            if st.form_submit_button("📤 Send Message", use_container_width=True):
                if msg_text.strip():
                    try:
                        conn_m = mysql.connector.connect(**DB_CONFIG)
                        cursor_m = conn_m.cursor()
                        cursor_m.execute("INSERT INTO messages (sender, message) VALUES (%s, %s)", (curr_user, msg_text.strip()))
                        conn_m.commit(); cursor_m.close(); conn_m.close()
                        notify_body = f"<p style='color:#94a3b8;'>New message from <strong style='color:#a5b4fc;'>{curr_user}</strong>:</p><p style='color:#e2e8f0;border-left:3px solid #6366f1;padding-left:1rem;'>{msg_text}</p>"
                        send_email("sashankmidhun@gmail.com", f"New Message from {curr_user} — Traqify", email_template("New Message", notify_body))
                        log_activity(curr_user, "Sent message to admin")
                        st.success("Message sent! The admin will reply to your email.")
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.warning("Write a message first.")
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        st.markdown("#### 📬 Your Conversation History")
        try:
            conn_mh = mysql.connector.connect(**DB_CONFIG)
            mh_df = pd.read_sql("SELECT message, reply, status, created_at FROM messages WHERE sender=%s ORDER BY created_at DESC", conn_mh, params=(curr_user,))
            conn_mh.close()
        except Exception:
            mh_df = pd.DataFrame()
        if mh_df.empty:
            st.info("No messages yet.")
        else:
            for _, row in mh_df.iterrows():
                is_resolved = row["status"] == "resolved"
                st.markdown(f"**{str(row['created_at'])[:16]}** &nbsp; {'✅ Resolved' if is_resolved else '⏳ Pending reply'}", unsafe_allow_html=True)
                st.markdown(f"📤 **You:** {row['message']}")
                if row["reply"]:
                    st.success(f"📥 Admin: {row['reply']}")
                else:
                    st.caption("Waiting for admin reply...")
                st.markdown("---")

    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;color:#334155;font-size:0.78rem;padding:0.5rem 0 1rem 0;">
        Supply Chain AI Enterprise · Built with Streamlit & MySQL
    </div>""", unsafe_allow_html=True)



# ====================================================================
# 6b. ADMIN DASHBOARD
# ====================================================================
def admin_dashboard():
    # ── Sidebar ──
    st.sidebar.markdown("""
    <div style="text-align:center;padding:1rem 0 0.5rem 0;">
        <div style="font-size:3rem;filter:drop-shadow(0 0 8px rgba(99,102,241,0.6));">⚙️</div>
        <h3 style="color:#a5b4fc;margin:0.4rem 0;font-size:1.4rem;font-weight:800;letter-spacing:1px;">Traqify</h3>
        <p style="color:#6366f1;font-size:0.78rem;margin:0;font-weight:600;letter-spacing:2px;text-transform:uppercase;">Admin Panel</p>
    </div>
    <hr style="border-color:rgba(99,102,241,0.3);margin:0.8rem 0;">
    """, unsafe_allow_html=True)

    if st.sidebar.button("�� Logout", use_container_width=True):
        log_activity("lunalupa", "Admin Logout")
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

    # ── Hero Banner ──
    st.markdown("""
    <div class="hero-banner">
        <h2>⚙️ Traqify Admin Panel</h2>
        <p>User management · Activity monitoring · Broadcast updates · SQL access</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Quick Stats ──
    try:
        conn_s = mysql.connector.connect(**DB_CONFIG)
        total_users = pd.read_sql("SELECT COUNT(*) as cnt FROM users", conn_s).iloc[0, 0]
        total_logs  = pd.read_sql("SELECT COUNT(*) as cnt FROM activity_log", conn_s).iloc[0, 0]
        conn_s.close()
    except Exception:
        total_users = total_logs = "N/A"

    s1, s2 = st.columns(2)
    s1.metric("👥 Total Users", total_users)
    s2.metric("📋 Activity Events", total_logs)
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)

    # ── Tabs ──
    a1, a2, a3, a4 = st.tabs(["👥 Users", "📢 Broadcast", "📥 Inbox & Logs", "🗿 SQL Console"])

    # ── TAB 1: User Management ──
    with a1:
        st.markdown("### 👥 User Management")
        try:
            conn_u = mysql.connector.connect(**DB_CONFIG)
            um_df = pd.read_sql("SELECT id, username, email FROM users ORDER BY id", conn_u)
            conn_u.close()
        except Exception as e:
            um_df = pd.DataFrame()
            st.error(f"Error: {e}")

        if not um_df.empty:
            st.dataframe(um_df, use_container_width=True, hide_index=True)
            st.markdown("---")
            col_del, col_reset = st.columns(2)

            with col_del:
                st.markdown("#### 🗑️ Remove User")
                del_options = [u for u in um_df["username"].tolist() if u != "lunalupa"]
                if del_options:
                    del_user = st.selectbox("Select user", del_options, key="admin_del_user")
                    if st.button("🗑️ Delete User", key="admin_del_btn", use_container_width=True):
                        try:
                            conn_d = mysql.connector.connect(**DB_CONFIG)
                            cursor_d = conn_d.cursor()
                            cursor_d.execute("DELETE FROM users WHERE username=%s", (del_user,))
                            conn_d.commit(); cursor_d.close(); conn_d.close()
                            log_activity("lunalupa", f"Deleted user: {del_user}")
                            st.success(f"✅ Deleted {del_user}")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {e}")
                else:
                    st.info("No other users.")

            with col_reset:
                st.markdown("#### 🔑 Reset Password")
                reset_user = st.selectbox("Select user", um_df["username"].tolist(), key="admin_reset_user")
                new_pw = st.text_input("New Password", type="password", key="admin_new_pw")
                if st.button("🔑 Reset", key="admin_reset_btn", use_container_width=True):
                    if new_pw:
                        try:
                            conn_r = mysql.connector.connect(**DB_CONFIG)
                            cursor_r = conn_r.cursor()
                            cursor_r.execute("UPDATE users SET password=%s WHERE username=%s", (new_pw, reset_user))
                            conn_r.commit(); cursor_r.close(); conn_r.close()
                            log_activity("lunalupa", f"Reset password: {reset_user}")
                            st.success(f"✅ Password reset for {reset_user}")
                        except Exception as e:
                            st.error(f"Error: {e}")
                    else:
                        st.warning("Enter a new password.")

    # ── TAB 2: Broadcast ──
    with a2:
        st.markdown("### 📢 Broadcast Update to All Users")
        st.markdown("<p style='color:#94a3b8;'>Type an update message and send it to all users who have saved their email.</p>", unsafe_allow_html=True)

        broadcast_subject = st.text_input("📌 Subject", placeholder="e.g. New feature released!", key="broadcast_subject")
        broadcast_msg = st.text_area("✉️ Message", placeholder="Write your update here...", height=150, key="broadcast_msg")

        if st.button("📤 Send to All Users", use_container_width=False, key="broadcast_send"):
            if broadcast_msg and broadcast_subject:
                try:
                    conn_b = mysql.connector.connect(**DB_CONFIG)
                    emails_df = pd.read_sql("SELECT email FROM users WHERE email IS NOT NULL AND email != ''", conn_b)
                    conn_b.close()
                except Exception:
                    emails_df = pd.DataFrame()

                if emails_df.empty:
                    st.warning("No users have saved their email yet.")
                else:
                    body = f"""
                    <p style="color:#94a3b8;font-size:1rem;">{broadcast_msg.replace(chr(10), "<br>")}</p>
                    <hr style="border-color:#334155;margin:1.5rem 0;">
                    <p style="color:#475569;font-size:0.8rem;">This is an official update from the Traqify admin team.</p>"""
                    html = email_template(f"📢 {broadcast_subject}", body)
                    sent = 0
                    for email in emails_df["email"]:
                        ok = send_email(email, f"📢 {broadcast_subject} — Traqify", html)
                        if ok: sent += 1
                    log_activity("lunalupa", f"Broadcast sent to {sent} users: {broadcast_subject}")
                    st.success(f"✅ Sent to {sent} users!")
            else:
                st.warning("Fill in both subject and message.")

        # Preview
        if broadcast_msg:
            st.markdown("#### 👁️ Preview")
            st.markdown(f"""
            <div style="background:rgba(99,102,241,0.08);border:1px solid rgba(99,102,241,0.3);
                border-radius:12px;padding:1.5rem;">
                <h4 style="color:#a5b4fc;margin:0 0 0.8rem;">📢 {broadcast_subject or "Subject..."}</h4>
                <p style="color:#94a3b8;">{broadcast_msg}</p>
            </div>""", unsafe_allow_html=True)


    # ADMIN TAB 3: INBOX
    with a3:
        st.markdown("### 📥 User Messages Inbox")
        try:
            conn_i = mysql.connector.connect(**DB_CONFIG)
            inbox_df = pd.read_sql("SELECT id, sender, message, reply, status, created_at FROM messages ORDER BY created_at DESC", conn_i)
            conn_i.close()
        except Exception as e:
            inbox_df = pd.DataFrame()
            st.error(f"Error: {e}")

        if inbox_df.empty:
            st.info("No messages yet.")
        else:
            pending = inbox_df[inbox_df["status"] == "pending"]
            st.metric("�� Pending Messages", len(pending))
            st.markdown("---")
            for _, row in inbox_df.iterrows():
                is_pending = row["status"] == "pending"
                with st.expander(f"{'🔴' if is_pending else '✅'} From: {row['sender']} — {str(row['created_at'])[:16]}", expanded=is_pending):
                    st.markdown(f"**Message:** {row['message']}")
                    if row["reply"]:
                        st.success(f"Your reply: {row['reply']}")
                    else:
                        reply_text = st.text_area("Reply", key=f"reply_{row['id']}", placeholder="Type your reply...")
                        col_r1, col_r2 = st.columns(2)
                        with col_r1:
                            if st.button("📤 Send Reply", key=f"send_reply_{row['id']}", use_container_width=True):
                                if reply_text.strip():
                                    try:
                                        conn_reply = mysql.connector.connect(**DB_CONFIG)
                                        cursor_reply = conn_reply.cursor()
                                        cursor_reply.execute("UPDATE messages SET reply=%s, status='resolved', replied_at=NOW() WHERE id=%s", (reply_text.strip(), int(row["id"])))
                                        conn_reply.commit(); cursor_reply.close(); conn_reply.close()
                                        # Email the user
                                        try:
                                            conn_email = mysql.connector.connect(**DB_CONFIG)
                                            user_email_row = pd.read_sql("SELECT email FROM users WHERE username=%s", conn_email, params=(row["sender"],))
                                            conn_email.close()
                                            if not user_email_row.empty and user_email_row.iloc[0,0]:
                                                body = f"<p style='color:#94a3b8;'>Your message has been replied to:</p><p style='color:#e2e8f0;border-left:3px solid #6366f1;padding-left:1rem;'><strong>Your message:</strong> {row['message']}</p><p style='color:#e2e8f0;border-left:3px solid #22c55e;padding-left:1rem;'><strong>Admin reply:</strong> {reply_text}</p>"
                                                send_email(user_email_row.iloc[0,0], "Admin replied to your message — Traqify", email_template("Reply from Admin", body))
                                        except Exception:
                                            pass
                                        log_activity("lunalupa", f"Replied to {row['sender']}")
                                        st.success("Reply sent!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"Error: {e}")
                                else:
                                    st.warning("Write a reply first.")
                        with col_r2:
                            if st.button("🗑️ Delete", key=f"del_msg_{row['id']}", use_container_width=True):
                                try:
                                    conn_del = mysql.connector.connect(**DB_CONFIG)
                                    cursor_del = conn_del.cursor()
                                    cursor_del.execute("DELETE FROM messages WHERE id=%s", (int(row["id"]),))
                                    conn_del.commit(); cursor_del.close(); conn_del.close()
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"Error: {e}")

    # ── TAB 3: Inbox & Logs ──
    with a3:
        st.markdown("### 📋 User Activity Log")
        log_df = get_activity_log(500)
        if log_df.empty:
            st.info("No activity recorded yet.")
        else:
            log_search = st.text_input("🔍 Search", placeholder="username or action", key="admin_log_search")
            if log_search:
                mask = log_df.apply(lambda r: r.astype(str).str.contains(log_search, case=False).any(), axis=1)
                log_df = log_df[mask]
            st.dataframe(log_df, use_container_width=True, height=450, hide_index=True)
            st.download_button("📥 Export CSV", data=log_df.to_csv(index=False).encode(),
                               file_name=f"activity_{datetime.date.today()}.csv", mime="text/csv")

    # ── TAB 4: SQL Console ──
    with a4:
        st.markdown("### 🗿 MySQL Console")
        query = st.text_area("SQL Query", "SELECT * FROM users;", height=140, key="admin_sql_query")
        if st.button("▶ Run Query", key="admin_run_query"):
            with st.spinner("Executing..."):
                try:
                    conn_sql = mysql.connector.connect(**DB_CONFIG)
                    df_sql = pd.read_sql(query, conn_sql)
                    conn_sql.close()
                    st.success(f"✅ Returned {len(df_sql)} rows")
                    st.dataframe(df_sql, use_container_width=True)
                    log_activity("lunalupa", f"SQL: {query[:80]}")
                except Error as e:
                    st.error(f"❌ {e}")

    # ── Footer ──
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    st.markdown("""<div style="text-align:center;color:#334155;font-size:0.78rem;padding:0.5rem 0 1rem 0;">
        Traqify Admin Panel · Built with Streamlit & MySQL</div>""", unsafe_allow_html=True)

# ====================================================================
# 7. ROUTER
# ====================================================================
if not st.session_state.logged_in:
    auth_page()
elif st.session_state.get("username","") == "lunalupa":
    admin_dashboard()
else:
    main_dashboard()
