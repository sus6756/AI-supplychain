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
    st.session_state.auth_mode = "login"

# ====================================================================
# 2. MYSQL CONFIG (CLOUD READY)
# ====================================================================
DB_CONFIG = {
    "host": st.secrets["DB_HOST"],
    "user": st.secrets["DB_USER"],
    "password": st.secrets["DB_PASSWORD"],
    "database": st.secrets["DB_NAME"],
    "port": st.secrets["DB_PORT"]
}

# ====================================================================
# 3. DATABASE SETUP
# ====================================================================
def init_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

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
        st.error(f"DB Init Error: {e}")


def init_supply_chain_tables():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INT PRIMARY KEY,
            product_name VARCHAR(100),
            category VARCHAR(50),
            stock_quantity INT,
            reorder_level INT,
            warehouse_location VARCHAR(50),
            unit_price DECIMAL(10,2)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS suppliers (
            supplier_id INT PRIMARY KEY,
            supplier_name VARCHAR(100),
            country VARCHAR(50),
            reliability_score FLOAT
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS shipments (
            shipment_id INT PRIMARY KEY,
            supplier_id INT,
            product_id INT,
            shipment_date DATE,
            expected_delivery DATE,
            actual_delivery DATE,
            quantity INT,
            transport_cost DECIMAL(10,2),
            FOREIGN KEY (supplier_id) REFERENCES suppliers(supplier_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sales (
            sale_id INT PRIMARY KEY,
            product_id INT,
            sale_date DATE,
            quantity_sold INT,
            revenue DECIMAL(10,2),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );
        """)

        conn.commit()
        cursor.close()
        conn.close()

    except Error as e:
        st.error(f"Table Init Error: {e}")


init_db()
init_supply_chain_tables()

# ====================================================================
# 4. AUTH PAGE
# ====================================================================
def auth_page():
    _, center_col, _ = st.columns([1, 1.5, 1])

    with center_col:

        if st.session_state.auth_mode == "login":
            st.markdown("### 🔐 Login")

            with st.form("login"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")

                if submit:
                    conn = mysql.connector.connect(**DB_CONFIG)
                    cursor = conn.cursor()
                    cursor.execute("SELECT password FROM users WHERE username=%s", (username,))
                    row = cursor.fetchone()

                    if row and row[0] == password:
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error("Invalid login")

        else:
            st.markdown("### 📝 Sign Up")

            with st.form("signup"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Create Account")

                if submit:
                    conn = mysql.connector.connect(**DB_CONFIG)
                    cursor = conn.cursor()

                    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
                    if cursor.fetchone():
                        st.error("User exists")
                    else:
                        cursor.execute(
                            "INSERT INTO users (username, password) VALUES (%s, %s)",
                            (username, password)
                        )
                        conn.commit()
                        st.success("Account created")

        if st.button("Switch Mode"):
            st.session_state.auth_mode = "signup" if st.session_state.auth_mode == "login" else "login"
            st.rerun()


# ====================================================================
# 5. DASHBOARD
# ====================================================================
def main_dashboard():
    st.sidebar.title("👾Database Dashboard👾")

    if st.sidebar.button("Logout👈"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("🚛 Supply Chain Dashboard")

    option = st.sidebar.radio("Upload Type", ["Excel", "CSV"])

    products_df = sales_df = shipments_df = None
    data_loaded = False

    if option == "Excel":
        file = st.sidebar.file_uploader("Upload Excel", type=["xlsx"])
        if file:
            products_df = pd.read_excel(file, sheet_name="products")
            shipments_df = pd.read_excel(file, sheet_name="shipments")
            sales_df = pd.read_excel(file, sheet_name="sales")
            data_loaded = True

    else:
        p = st.sidebar.file_uploader("products.csv")
        s = st.sidebar.file_uploader("sales.csv")
        sh = st.sidebar.file_uploader("shipments.csv")

        if p and s and sh:
            products_df = pd.read_csv(p)
            sales_df = pd.read_csv(s)
            shipments_df = pd.read_csv(sh)
            data_loaded = True

    if not data_loaded:
        st.warning("Upload data first")
        st.stop()

    sales_df["revenue"] = pd.to_numeric(sales_df["revenue"], errors="coerce")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Revenue", sales_df["revenue"].sum())
    col2.metric("Delayed Shipments",
                len(shipments_df[shipments_df["actual_delivery"] > shipments_df["expected_delivery"]]))
    col3.metric("Low Stock",
                len(products_df[products_df["stock_quantity"] < products_df["reorder_level"]]))
    col4.metric("Products", len(products_df))

    st.subheader("💰Revenue Trends📊")
    sales_df["sale_date"] = pd.to_datetime(sales_df["sale_date"])
    monthly = sales_df.groupby(sales_df["sale_date"].dt.month)["revenue"].sum().reset_index()
    st.plotly_chart(px.bar(monthly, x="sale_date", y="revenue"))

    st.subheader("💼Inventory")
    st.dataframe(products_df)

    st.subheader("🚚Shipments🚛")
    st.dataframe(shipments_df)

    st.subheader("🗿MySQL Console")

    query = st.text_area("SQL Query", "SELECT * FROM users;")

    if st.button("Run Query"):
        conn = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql(query, conn)
        st.dataframe(df)


# ====================================================================
# 6. ROUTER
# ====================================================================
if not st.session_state.logged_in:
    auth_page()
else:
    main_dashboard()
