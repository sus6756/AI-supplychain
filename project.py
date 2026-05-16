import pandas as pd
import streamlit as st
import plotly.express as px
import mysql.connector
from mysql.connector import Error

st.set_page_config(page_title="Supply Chain AI", layout="wide")
st.title("🚛 AI Supply Chain Dashboard")
st.markdown("**MySQL + Excel Support**")

# ====================== SIDEBAR ======================
option = st.sidebar.radio("Data Source", ["📤 Excel Upload", "🗄️ MySQL Database"])

data_loaded = False
sales_df = products_df = shipments_df = None

if option == "🗄️ MySQL Database":
    st.sidebar.header("MySQL Connection")
    host = st.sidebar.text_input("Host", "localhost")
    user = st.sidebar.text_input("User", "root")
    password = st.sidebar.text_input("Password", "code_RED", type="password")
    database = st.sidebar.text_input("Database", "supply_chain")

    if st.sidebar.button("Connect to MySQL"):
        try:
            conn = mysql.connector.connect(
                host=host, user=user, password=password, database=database
            )
            st.success("✅ Connected to MySQL!")

            sales_df = pd.read_sql("SELECT * FROM sales", conn)
            products_df = pd.read_sql("SELECT * FROM products", conn)
            shipments_df = pd.read_sql("SELECT * FROM shipments", conn)
            data_loaded = True
            st.session_state.conn = conn
        except Error as e:
            st.error(f"Connection Failed: {e}")
            st.info("💡 Tip: Make sure MySQL server is running (`mysqld` or XAMPP)")

else:
    # Excel Upload
    uploaded_file = st.sidebar.file_uploader("Upload supply_chain_dataset.xlsx", type=["xlsx"])
    if uploaded_file:
        products_df = pd.read_excel(uploaded_file, sheet_name='products')
        shipments_df = pd.read_excel(uploaded_file, sheet_name='shipments')
        sales_df = pd.read_excel(uploaded_file, sheet_name='sales')
        data_loaded = True
        st.success("✅ Excel Loaded!")

# ====================== IF DATA LOADED ======================
if not data_loaded:
    st.warning("Please connect to MySQL or upload Excel file")
    st.stop()

# Data Cleaning
sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'], errors='coerce')
shipments_df['expected_delivery'] = pd.to_datetime(shipments_df['expected_delivery'], errors='coerce')
shipments_df['actual_delivery'] = pd.to_datetime(shipments_df['actual_delivery'], errors='coerce')
sales_df['revenue'] = pd.to_numeric(sales_df['revenue'], errors='coerce')

# ====================== METRICS ======================
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"${sales_df['revenue'].sum():,.0f}")
col2.metric("⚠️ Delayed Shipments", len(shipments_df[shipments_df['actual_delivery'] > shipments_df['expected_delivery']]))
col3.metric("📉 Low Stock", len(products_df[products_df['stock_quantity'] < products_df['reorder_level']]))
col4.metric("📦 Products", len(products_df))

# ====================== TABS ======================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Sales", "📦 Inventory", "🚚 Shipments", "🔍 SQL Query"])

with tab1:
    st.subheader("Monthly Revenue")
    sales_df['month'] = sales_df['sale_date'].dt.strftime('%Y-%m')
    monthly = sales_df.groupby('month')['revenue'].sum().reset_index()
    fig = px.bar(monthly, x='month', y='revenue')
    st.plotly_chart(fig, use_container_width=True, width='stretch')

with tab2:
    st.subheader("Low Stock")
    low = products_df[products_df['stock_quantity'] < products_df['reorder_level']]
    st.dataframe(low, width='stretch')

with tab3:
    st.subheader("Shipment Delays")
    shipments_df['delay_days'] = (shipments_df['actual_delivery'] - shipments_df['expected_delivery']).dt.days
    st.dataframe(shipments_df[['shipment_id','product_id','expected_delivery','actual_delivery','delay_days']], 
                 width='stretch')

with tab4:
    st.subheader("Custom SQL Query")
    query = st.text_area("Write your SQL here:", 
                        "SELECT * FROM sales LIMIT 10", height=120)
    if st.button("Run Query"):
        try:
            if 'conn' in st.session_state:
                result = pd.read_sql(query, st.session_state.conn)
            else:
                st.error("SQL Query only works in MySQL mode")
                result = None
            if result is not None:
                st.dataframe(result, width='stretch')
        except Exception as e:
            st.error(f"Query Error: {e}")

st.caption("Supply Chain Project | MySQL + Excel")
