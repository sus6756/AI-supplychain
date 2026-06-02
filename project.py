import pandas as pd
import streamlit as st
import plotly.express as px
import mysql.connector
from mysql.connector import Error

# ====================================================================
# 1. PAGE & SESSION STATE INITIALIZATION
# ====================================================================
st.set_page_config(page_title="Supply Chain AI Enterprise", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"  # Default view mode

# --- CRITICAL: Define Your Global MySQL Configuration Here ---
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "code_RED",
    "database": "supply_chain",
    "port": 3306
}


# ====================================================================
# 2. AUTOMATIC DATABASE TABLE SETUP
# ====================================================================
def init_db():
    """Ensures the users authentication table exists in MySQL."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        # Creates user table automatically if missing
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL
            );
        """)
        conn.commit()
        cursor.close()
        conn.close()
    except Error as e:
        st.error(f"⚠️ Core Database Connection failed during init: {e}")


# Run database schema initialization
init_db()


# ====================================================================
# 3. AUTHENTICATION PORTAL GATEWAY
# ====================================================================
def auth_page():
    st.markdown(
        """
        <style>
        .auth-box {
            max-width: 420px;
            padding: 2.5rem;
            margin: auto;
            border-radius: 12px;
            background-color: #f8f9fa;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    _, center_col, _ = st.columns([1, 1.5, 1])

    with center_col:
        # ---------------- VIEW A: LOG IN ----------------
        if st.session_state.auth_mode == "login":
            st.markdown("<h2 style='text-align: center;'>🔐 Secure Portal Log In</h2>", unsafe_allow_html=True)

            with st.form("login_form"):
                username = st.text_input("Username", placeholder="Enter your username")
                password = st.text_input("Password", type="password", placeholder="••••••••")
                submit = st.form_submit_button("LOG IN", use_container_width=True)

                if submit:
                    if username and password:
                        try:
                            conn = mysql.connector.connect(**DB_CONFIG)
                            cursor = conn.cursor()
                            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
                            row = cursor.fetchone()

                            if row and row[0] == password:
                                st.session_state.logged_in = True
                                st.success("✅ Access Granted!")
                                st.rerun()
                            else:
                                st.error("❌ Invalid Username or Password")

                            cursor.close()
                            conn.close()
                        except Error as e:
                            st.error(f"MySQL Error: {e}")
                    else:
                        st.warning("Please fill out all fields.")

            # Action alternative toggle link
            if st.button("New to database? SIGN UP", use_container_width=True):
                st.session_state.auth_mode = "signup"
                st.rerun()

        # ---------------- VIEW B: SIGN UP ----------------
        elif st.session_state.auth_mode == "signup":
            st.markdown("<h2 style='text-align: center;'>📝 Register System Profile</h2>", unsafe_allow_html=True)

            with st.form("signup_form"):
                new_username = st.text_input("Choose Username", placeholder="Create account username")
                new_password = st.text_input("Choose Password", type="password", placeholder="Create secure password")
                submit_signup = st.form_submit_button("SIGN UP", use_container_width=True)

                if submit_signup:
                    if new_username and new_password:
                        try:
                            conn = mysql.connector.connect(**DB_CONFIG)
                            cursor = conn.cursor()

                            # Check if the registration identity already exists
                            cursor.execute("SELECT * FROM users WHERE username = %s", (new_username,))
                            if cursor.fetchone():
                                st.error("⚠️ That username is already registered! Try logging in.")
                            else:
                                # Insert new row into MySQL
                                cursor.execute(
                                    "INSERT INTO users (username, password) VALUES (%s, %s)",
                                    (new_username, new_password)
                                )
                                conn.commit()
                                st.success("🎉 Account created successfully! Please Log In below.")
                                st.session_state.auth_mode = "login"
                                st.rerun()

                            cursor.close()
                            conn.close()
                        except Error as e:
                            st.error(f"MySQL Error: {e}")
                    else:
                        st.warning("Please supply both a registration username and password.")

            # Action alternative toggle link
            if st.button("Already have an account? LOG IN", use_container_width=True):
                st.session_state.auth_mode = "login"
                st.rerun()


# ====================================================================
# 4. MAIN APPLICATION DASHBOARD
# ====================================================================
def main_dashboard():
    st.sidebar.title("🛠️ Control Panel")
    st.sidebar.markdown("**Status:** Connected via MySQL")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.auth_mode = "login"
        st.rerun()

    st.sidebar.markdown("---")

    st.title("🚛 AI Supply Chain Control Center")
    st.markdown("**Unified Corporate Management Interface**")

    option = st.sidebar.radio("Select Dashboard File Source", ["📤 Excel Upload", "📁 CSV Upload"])

    sales_df = products_df = shipments_df = None
    data_loaded = False

    if option == "📤 Excel Upload":
        uploaded_file = st.sidebar.file_uploader("Upload supply_chain_dataset.xlsx", type=["xlsx"])
        if uploaded_file:
            try:
                products_df = pd.read_excel(uploaded_file, sheet_name='products')
                shipments_df = pd.read_excel(uploaded_file, sheet_name='shipments')
                sales_df = pd.read_excel(uploaded_file, sheet_name='sales')
                data_loaded = True
                st.sidebar.success("✅ Excel Metrics Synced!")
            except Exception as e:
                st.sidebar.error(f"Error parsing workbook: {e}")

    elif option == "📁 CSV Upload":
        st.sidebar.header("Upload CSVs")
        p = st.sidebar.file_uploader("products.csv", type=["csv"])
        s = st.sidebar.file_uploader("sales.csv", type=["csv"])
        sh = st.sidebar.file_uploader("shipments.csv", type=["csv"])

        if p and s and sh:
            products_df = pd.read_csv(p)
            sales_df = pd.read_csv(s)
            shipments_df = pd.read_csv(sh)
            data_loaded = True
            st.sidebar.success("✅ CSV Metrics Synced!")

    if not data_loaded:
        st.warning("👈 Complete data file uploads in the sidebar control panel to populate metric engines.")
        st.stop()

    # Data Formatting
    sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'], errors='coerce')
    shipments_df['expected_delivery'] = pd.to_datetime(shipments_df['expected_delivery'], errors='coerce')
    shipments_df['actual_delivery'] = pd.to_datetime(shipments_df['actual_delivery'], errors='coerce')
    sales_df['revenue'] = pd.to_numeric(sales_df['revenue'], errors='coerce')

    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total Revenue", f"${sales_df['revenue'].sum():,.0f}")
    col2.metric("⚠️ Delayed Shipments",
                len(shipments_df[shipments_df['actual_delivery'] > shipments_df['expected_delivery']]))
    col3.metric("📉 Low Stock Alerts", len(products_df[products_df['stock_quantity'] < products_df['reorder_level']]))
    col4.metric("📦 Tracked Products", len(products_df))

    tab1, tab2, tab3, tab4 = st.tabs(
        ["📊 Revenue & Sales", "📦 Inventory Hub", "🚚 Shipment Analytics", "🔍 Live MySQL Workspace"])

    with tab1:
        st.subheader("Monthly Revenue Trends")
        sales_df['month'] = sales_df['sale_date'].dt.strftime('%Y-%m')
        monthly = sales_df.groupby('month')['revenue'].sum().reset_index()
        fig = px.bar(monthly, x='month', y='revenue')
        st.plotly_chart(fig, use_container_width=True)

    with tab2:
        st.subheader("Stock Level Metrics per Product")
        if 'product_name' in products_df.columns and 'stock_quantity' in products_df.columns:
            fig_inv = px.bar(products_df, x='product_name', y=['stock_quantity', 'reorder_level'], barmode='group')
            st.plotly_chart(fig_inv, use_container_width=True)
        else:
            st.dataframe(products_df, use_container_width=True)

    with tab3:
        st.subheader("Shipment Delays Log Table")
        shipments_df['delay_days'] = (shipments_df['actual_delivery'] - shipments_df['expected_delivery']).dt.days
        shipments_df['delay_days'] = shipments_df['delay_days'].apply(lambda x: x if x > 0 else 0)
        st.dataframe(shipments_df[['shipment_id', 'product_id', 'expected_delivery', 'actual_delivery', 'delay_days']],
                     use_container_width=True)

    with tab4:
        st.subheader("💻 Raw MySQL Execution Console")
        st.markdown("Query tables resident inside your active MySQL connection database context (`supply_chain`).")

        default_query = "SELECT * FROM users;"
        query_input = st.text_area("SQL Statement Terminal Entry", value=default_query, height=120)

        if st.button("🚀 Run Database Command"):
            try:
                conn = mysql.connector.connect(**DB_CONFIG)
                query_result = pd.read_sql_query(query_input, conn)
                st.success("Query compiled successfully!")
                st.dataframe(query_result, use_container_width=True)
                conn.close()
            except Error as sql_error:
                st.error(f"❌ Backend MySQL Syntax Error: {sql_error}")

    st.markdown("---")
    st.caption("🔒 Corporate Supply Chain Analytics Application System")


# ====================================================================
# 5. CORE PROGRAM GATE ROUTER
# ====================================================================
if not st.session_state.logged_in:
    auth_page()
else:
    main_dashboard()
