import pandas as pd
import streamlit as st
import plotly.express as px
import mysql.connector
from mysql.connector import Error

st.set_page_config(page_title="Supply Chain AI", layout="wide")
st.title("🚛 AI Supply Chain Dashboard")
st.markdown("**Excel + CSV + MySQL**")

option = st.sidebar.radio("Select Data Source", 
                         ["📤 Excel Upload", "📁 CSV Upload", "🗄️ MySQL Database"])

sales_df = products_df = shipments_df = None
data_loaded = False

# ====================== EXCEL ======================
if option == "📤 Excel Upload":
    uploaded_file = st.sidebar.file_uploader("Upload supply_chain_dataset.xlsx", type=["xlsx"])
    if uploaded_file:
        products_df = pd.read_excel(uploaded_file, sheet_name='products')
        shipments_df = pd.read_excel(uploaded_file, sheet_name='shipments')
        sales_df = pd.read_excel(uploaded_file, sheet_name='sales')
        data_loaded = True
        st.success("✅ Excel Loaded!")

# ====================== CSV ======================
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
        st.success("✅ CSVs Loaded!")

# ====================== MySQL ======================
elif option == "🗄️ MySQL Database":
    st.sidebar.header("MySQL Connection")
    host = st.sidebar.text_input("Host", "localhost")
    user = st.sidebar.text_input("User", "root")
    password = st.sidebar.text_input("Password", "code_RED", type="password")
    database = st.sidebar.text_input("Database", "supply_chain")

    if st.sidebar.button("🔗 Connect to MySQL"):
        try:
            mydb = mysql.connector.connect(
                host="localhost",   
                user='root', 
                password='code_RED', 
                database='supply_chain',
                port=3306
            )
            sales_df = pd.read_sql("SELECT * FROM sales", conn)
            products_df = pd.read_sql("SELECT * FROM products", conn)
            shipments_df = pd.read_sql("SELECT * FROM shipments", conn)
            data_loaded = True
            st.session_state.conn = conn
            st.success("✅ Successfully Connected to MySQL!")
        except Error as e:
            st.error(f"❌ MySQL Connection Failed: {e}")
            st.info("💡 Tip: Open XAMPP and start MySQL server")

    # Load Excel to MySQL
    st.sidebar.header("📤 Load Excel → MySQL")
    excel_file = st.sidebar.file_uploader("Upload Excel to insert", type=["xlsx"], key="db_insert")
    if excel_file and st.sidebar.button("Insert Data into MySQL"):
        st.info("Insert feature ready (MySQL must be connected first)")

if not data_loaded:
    st.warning("👈 Please upload file or connect to MySQL")
    st.stop()

# ====================== DASHBOARD ======================
sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'], errors='coerce')
shipments_df['expected_delivery'] = pd.to_datetime(shipments_df['expected_delivery'], errors='coerce')
shipments_df['actual_delivery'] = pd.to_datetime(shipments_df['actual_delivery'], errors='coerce')
sales_df['revenue'] = pd.to_numeric(sales_df['revenue'], errors='coerce')

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"${sales_df['revenue'].sum():,.0f}")
col2.metric("⚠️ Delayed Shipments", len(shipments_df[shipments_df['actual_delivery'] > shipments_df['expected_delivery']]))
col3.metric("📉 Low Stock", len(products_df[products_df['stock_quantity'] < products_df['reorder_level']]))
col4.metric("📦 Products", len(products_df))

tab1, tab2, tab3, tab4 = st.tabs(["📊 Sales", "📦 Inventory", "🚚 Shipments", "🔍 SQL Query"])

with tab1:
    st.subheader("Monthly Revenue")
    sales_df['month'] = sales_df['sale_date'].dt.strftime('%Y-%m')
    monthly = sales_df.groupby('month')['revenue'].sum().reset_index()
    fig = px.bar(monthly, x='month', y='revenue')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Shipment Delays")
    shipments_df['delay_days'] = (shipments_df['actual_delivery'] - shipments_df['expected_delivery']).dt.days
    st.dataframe(
        shipments_df[['shipment_id', 'product_id', 'expected_delivery', 'actual_delivery', 'delay_days']], 
        use_container_width=True
    )

st.caption("Supply Chain Project Dashboard")            st.info("💡 Tip: Open XAMPP and start MySQL server")

    # Load Excel to MySQL
    st.sidebar.header("📤 Load Excel → MySQL")
    excel_file = st.sidebar.file_uploader("Upload Excel to insert", type=["xlsx"], key="db_insert")
    if excel_file and st.sidebar.button("Insert Data into MySQL"):
        st.info("Insert feature ready (MySQL must be connected first)")

if not data_loaded:
    st.warning("👈 Please upload file or connect to MySQL")
    st.stop()

# ====================== DASHBOARD ======================
sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'], errors='coerce')
shipments_df['expected_delivery'] = pd.to_datetime(shipments_df['expected_delivery'], errors='coerce')
shipments_df['actual_delivery'] = pd.to_datetime(shipments_df['actual_delivery'], errors='coerce')
sales_df['revenue'] = pd.to_numeric(sales_df['revenue'], errors='coerce')

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"${sales_df['revenue'].sum():,.0f}")
col2.metric("⚠️ Delayed Shipments", len(shipments_df[shipments_df['actual_delivery'] > shipments_df['expected_delivery']]))
col3.metric("📉 Low Stock", len(products_df[products_df['stock_quantity'] < products_df['reorder_level']]))
col4.metric("📦 Products", len(products_df))

tab1, tab2, tab3, tab4 = st.tabs(["📊 Sales", "📦 Inventory", "🚚 Shipments", "🔍 SQL Query"])

with tab1:
    st.subheader("Monthly Revenue")
    sales_df['month'] = sales_df['sale_date'].dt.strftime('%Y-%m')
    monthly = sales_df.groupby('month')['revenue'].sum().reset_index()
    fig = px.bar(monthly, x='month', y='revenue')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Shipment Delays")
    shipments_df['delay_days'] = (shipments_df['actual_delivery'] - shipments_df['expected_delivery']).dt.days
    st.dataframe(
        shipments_df[['shipment_id', 'product_id', 'expected_delivery', 'actual_delivery', 'delay_days']], 
        use_container_width=True
    )

st.caption("Supply Chain Project Dashboard")            st.info("💡 Tip: Open XAMPP and start MySQL server")

if not data_loaded:
    st.warning("👈 Please upload file or connect to MySQL")
    st.stop()

# ====================== DASHBOARD ======================
sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'], errors='coerce')
shipments_df['expected_delivery'] = pd.to_datetime(shipments_df['expected_delivery'], errors='coerce')
shipments_df['actual_delivery'] = pd.to_datetime(shipments_df['actual_delivery'], errors='coerce')
sales_df['revenue'] = pd.to_numeric(sales_df['revenue'], errors='coerce')

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"${sales_df['revenue'].sum():,.0f}")
col2.metric("⚠️ Delayed Shipments", len(shipments_df[shipments_df['actual_delivery'] > shipments_df['expected_delivery']]))
col3.metric("📉 Low Stock", len(products_df[products_df['stock_quantity'] < products_df['reorder_level']]))
col4.metric("📦 Products", len(products_df))

tab1, tab2, tab3 = st.tabs(["📊 Sales", "📦 Inventory", "🚚 Shipments"])

with tab1:
    st.subheader("Monthly Revenue")
    sales_df['month'] = sales_df['sale_date'].dt.strftime('%Y-%m')
    monthly = sales_df.groupby('month')['revenue'].sum().reset_index()
    fig = px.bar(monthly, x='month', y='revenue')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Shipment Delays")
    shipments_df['delay_days'] = (shipments_df['actual_delivery'] - shipments_df['expected_delivery']).dt.days
    st.dataframe(shipments_df[['shipment_id', 'product_id', 'expected_delivery', 'actual_delivery', 'delay_days']], 
                 use_container_width=True)

st.caption("Supply Chain Project Dashboard")            st.info("💡 Make sure MySQL server is running (XAMPP / Homebrew)")

if not data_loaded:
    st.warning("👈 Please upload file or connect to MySQL")
    st.stop()

# ====================== DASHBOARD ======================
sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'], errors='coerce')
shipments_df['expected_delivery'] = pd.to_datetime(shipments_df['expected_delivery'], errors='coerce')
shipments_df['actual_delivery'] = pd.to_datetime(shipments_df['actual_delivery'], errors='coerce')
sales_df['revenue'] = pd.to_numeric(sales_df['revenue'], errors='coerce')

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"${sales_df['revenue'].sum():,.0f}")
col2.metric("⚠️ Delayed Shipments", len(shipments_df[shipments_df['actual_delivery'] > shipments_df['expected_delivery']]))
col3.metric("📉 Low Stock", len(products_df[products_df['stock_quantity'] < products_df['reorder_level']]))
col4.metric("📦 Products", len(products_df))

tab1, tab2, tab3 = st.tabs(["📊 Sales", "📦 Inventory", "🚚 Shipments"])

with tab1:
    st.subheader("Monthly Revenue")
    sales_df['month'] = sales_df['sale_date'].dt.strftime('%Y-%m')
    monthly = sales_df.groupby('month')['revenue'].sum().reset_index()
    fig = px.bar(monthly, x='month', y='revenue')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Shipment Delays")
    shipments_df['delay_days'] = (shipments_df['actual_delivery'] - shipments_df['expected_delivery']).dt.days
    st.dataframe(shipments_df[['shipment_id', 'product_id', 'expected_delivery', 'actual_delivery', 'delay_days']], 
                 use_container_width=True)

st.caption("Supply Chain Project Dashboard")            st.info("💡 Tip: Open XAMPP and start MySQL server")

    # Load Excel to MySQL
    st.sidebar.header("📤 Load Excel → MySQL")
    excel_file = st.sidebar.file_uploader("Upload Excel to insert", type=["xlsx"], key="db_insert")
    if excel_file and st.sidebar.button("Insert Data into MySQL"):
        st.info("Insert feature ready (MySQL must be connected first)")

if not data_loaded:
    st.warning("👈 Please upload file or connect to MySQL")
    st.stop()

# ====================== DASHBOARD ======================
sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'], errors='coerce')
shipments_df['expected_delivery'] = pd.to_datetime(shipments_df['expected_delivery'], errors='coerce')
shipments_df['actual_delivery'] = pd.to_datetime(shipments_df['actual_delivery'], errors='coerce')
sales_df['revenue'] = pd.to_numeric(sales_df['revenue'], errors='coerce')

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"${sales_df['revenue'].sum():,.0f}")
col2.metric("⚠️ Delayed Shipments", len(shipments_df[shipments_df['actual_delivery'] > shipments_df['expected_delivery']]))
col3.metric("📉 Low Stock", len(products_df[products_df['stock_quantity'] < products_df['reorder_level']]))
col4.metric("📦 Products", len(products_df))

tab1, tab2, tab3, tab4 = st.tabs(["📊 Sales", "📦 Inventory", "🚚 Shipments", "🔍 SQL Query"])

with tab1:
    st.subheader("Monthly Revenue")
    sales_df['month'] = sales_df['sale_date'].dt.strftime('%Y-%m')
    monthly = sales_df.groupby('month')['revenue'].sum().reset_index()
    fig = px.bar(monthly, x='month', y='revenue')
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Shipment Delays")
    shipments_df['delay_days'] = (shipments_df['actual_delivery'] - shipments_df['expected_delivery']).dt.days
    st.dataframe(
        shipments_df[['shipment_id', 'product_id', 'expected_delivery', 'actual_delivery', 'delay_days']], 
        use_container_width=True
    )

st.caption("Supply Chain Project Dashboard")
