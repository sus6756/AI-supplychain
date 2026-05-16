import pandas as pd
import streamlit as st
import plotly.express as px
import mysql.connector
from mysql.connector import Error

st.set_page_config(page_title="Supply Chain AI", layout="wide")
st.title("🚛 AI Supply Chain Dashboard")
st.markdown("**Excel + CSV + MySQL Support**")

# ====================== DATA SOURCE ======================
option = st.sidebar.radio("Select Data Source", 
                         ["📤 Excel Upload", "📁 CSV Upload", "🗄️ MySQL Database"])

sales_df = products_df = shipments_df = None
data_loaded = False

# ------------------- EXCEL UPLOAD -------------------
if option == "📤 Excel Upload":
    uploaded_file = st.sidebar.file_uploader("Upload supply_chain_dataset.xlsx", type=["xlsx"])
    if uploaded_file:
        products_df = pd.read_excel(uploaded_file, sheet_name='products')
        shipments_df = pd.read_excel(uploaded_file, sheet_name='shipments')
        sales_df = pd.read_excel(uploaded_file, sheet_name='sales')
        data_loaded = True
        st.sidebar.success("✅ Excel Loaded")

# ------------------- CSV UPLOAD -------------------
elif option == "📁 CSV Upload":
    st.sidebar.header("Upload CSVs")
    products_file = st.sidebar.file_uploader("products.csv", type=["csv"])
    sales_file = st.sidebar.file_uploader("sales.csv", type=["csv"])
    shipments_file = st.sidebar.file_uploader("shipments.csv", type=["csv"])

    if products_file and sales_file and shipments_file:
        products_df = pd.read_csv(products_file)
        sales_df = pd.read_csv(sales_file)
        shipments_df = pd.read_csv(shipments_file)
        data_loaded = True
        st.sidebar.success("✅ All CSVs Loaded!")

# ------------------- MySQL -------------------
elif option == "🗄️ MySQL Database":
    st.sidebar.header("MySQL Login")
    host = st.sidebar.text_input("Host", "localhost")
    user = st.sidebar.text_input("User", "root")
    password = st.sidebar.text_input("Password", "code_RED", type="password")
    database = st.sidebar.text_input("Database", "supply_chain")

    if st.sidebar.button("Connect"):
        try:
            conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
            sales_df = pd.read_sql("SELECT * FROM sales", conn)
            products_df = pd.read_sql("SELECT * FROM products", conn)
            shipments_df = pd.read_sql("SELECT * FROM shipments", conn)
            data_loaded = True
            st.sidebar.success("✅ Connected to MySQL")
            st.session_state.conn = conn
        except Error as e:
            st.error(f"Connection Error: {e}")

# ====================== CHECK DATA ======================
if not data_loaded:
    st.warning("Please select a data source and upload/connect")
    st.stop()

# ====================== CLEANING ======================
sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'], errors='coerce')
shipments_df['expected_delivery'] = pd.to_datetime(shipments_df['expected_delivery'], errors='coerce')
shipments_df['actual_delivery'] = pd.to_datetime(shipments_df['actual_delivery'], errors='coerce')
sales_df['revenue'] = pd.to_numeric(sales_df['revenue'], errors='coerce')

# ====================== METRICS ======================
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"${sales_df['revenue'].sum():,.0f}")
col2.metric("⚠️ Delayed", len(shipments_df[shipments_df['actual_delivery'] > shipments_df['expected_delivery']]))
col3.metric("📉 Low Stock", len(products_df[products_df['stock_quantity'] < products_df['reorder_level']]))
col4.metric("📦 Products", len(products_df))

# ====================== TABS ======================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Sales", "📦 Inventory", "🚚 Shipments", "📁 Preview"])

with tab1:
    st.subheader("Monthly Revenue")
    sales_df['month'] = sales_df['sale_date'].dt.strftime('%Y-%m')
    monthly = sales_df.groupby('month')['revenue'].sum().reset_index()
    fig = px.bar(monthly, x='month', y='revenue')
    st.plotly_chart(fig, use_container_width=True, width='stretch')

with tab2:
    st.subheader("Low Stock Products")
    low = products_df[products_df['stock_quantity'] < products_df['reorder_level']]
    st.dataframe(low, width='stretch')

with tab3:
    st.subheader("Shipment Delays")
    shipments_df['delay_days'] = (shipments_df['actual_delivery'] - shipments_df['expected_delivery']).dt.days
    st.dataframe(shipments_df[['shipment_id', 'product_id', 'expected_delivery', 
                               'actual_delivery', 'delay_days']], width='stretch')

with tab4:
    st.subheader("Data Preview")
    st.write("**Sales**")
    st.dataframe(sales_df.head(), width='stretch')
    st.write("**Products**")
    st.dataframe(products_df.head(), width='stretch')
    st.write("**Shipments**")
    st.dataframe(shipments_df.head(), width='stretch')

st.caption("Supply Chain Dashboard | Excel + CSV + MySQL")
