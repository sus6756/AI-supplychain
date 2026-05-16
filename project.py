import pandas as pd
import streamlit as st
import plotly.express as px
import mysql.connector
from mysql.connector import Error

st.set_page_config(page_title="Supply Chain AI", layout="wide")
st.title("🚛 AI Supply Chain Dashboard")
st.markdown("**MySQL or CSV Upload → Live Dashboard**")

# ====================== DATA SOURCE ======================
mode = st.sidebar.radio("Select Data Source", ["📤 CSV Upload", "🗄️ MySQL Database"])

if mode == "🗄️ MySQL Database":
    st.sidebar.header("MySQL Login")
    host = st.sidebar.text_input("Host", "localhost")
    user = st.sidebar.text_input("Username", "root")
    password = st.sidebar.text_input("Password", "code_RED", type="password")
    db_name = st.sidebar.text_input("Database", "supply_chain")

    if st.sidebar.button("🔗 Connect to MySQL"):
        try:
            conn = mysql.connector.connect(
                host=host, user=user, password=password, database=db_name
            )
            st.success("✅ Connected to MySQL!")

            # Load from DB
            sales_df = pd.read_sql("SELECT * FROM sales", conn)
            products_df = pd.read_sql("SELECT * FROM products", conn)
            shipments_df = pd.read_sql("SELECT * FROM shipments", conn)

            st.session_state.sales_df = sales_df
            st.session_state.products_df = products_df
            st.session_state.shipments_df = shipments_df
            st.session_state.data_loaded = True
            st.success("Data loaded from MySQL!")
        except Error as e:
            st.error(f"❌ Connection Error: {e}")

else:
    # CSV Upload Mode
    st.sidebar.header("📤 Upload Files")
    products_file = st.sidebar.file_uploader("products.csv", type=["csv"])
    sales_file = st.sidebar.file_uploader("sales.csv", type=["csv"])
    shipments_file = st.sidebar.file_uploader("shipments.csv", type=["csv"])

    if st.sidebar.button("Load CSVs") and products_file and sales_file and shipments_file:
        sales_df = pd.read_csv(sales_file)
        products_df = pd.read_csv(products_file)
        shipments_df = pd.read_csv(shipments_file)

        st.session_state.sales_df = sales_df
        st.session_state.products_df = products_df
        st.session_state.shipments_df = shipments_df
        st.session_state.data_loaded = True
        st.success("✅ CSVs Loaded Successfully!")

# ====================== CHECK IF DATA LOADED ======================
if 'data_loaded' not in st.session_state:
    st.warning("Please connect to MySQL or upload CSVs")
    st.stop()

# Load data from session
sales_df = st.session_state.sales_df
products_df = st.session_state.products_df
shipments_df = st.session_state.shipments_df

# ====================== DATA CLEANING ======================
sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'], errors='coerce')
shipments_df['expected_delivery'] = pd.to_datetime(shipments_df['expected_delivery'], errors='coerce')
shipments_df['actual_delivery'] = pd.to_datetime(shipments_df['actual_delivery'], errors='coerce')
sales_df['revenue'] = pd.to_numeric(sales_df['revenue'], errors='coerce')

# ====================== DASHBOARD ======================
col1, col2, col3, col4 = st.columns(4)
total_rev = sales_df['revenue'].sum()
delayed = len(shipments_df[shipments_df['actual_delivery'] > shipments_df['expected_delivery']])
low_stock = len(products_df[products_df['stock_quantity'] < products_df['reorder_level']])

col1.metric("💰 Total Revenue", f"${total_rev:,.0f}")
col2.metric("⚠️ Delayed Shipments", delayed)
col3.metric("📉 Low Stock", low_stock)
col4.metric("📦 Total Products", len(products_df))

tab1, tab2, tab3, tab4 = st.tabs(["📊 Sales", "📦 Inventory", "🚚 Shipments", "📁 Raw Data"])

with tab1:
    st.subheader("Monthly Revenue")
    sales_df['month'] = sales_df['sale_date'].dt.strftime('%Y-%m')
    monthly = sales_df.groupby('month')['revenue'].sum().reset_index()
    fig = px.bar(monthly, x='month', y='revenue')
    st.plotly_chart(fig, use_container_width=True, width='stretch')

with tab2:
    st.subheader("Low Stock Products")
    low_df = products_df[products_df['stock_quantity'] < products_df['reorder_level']]
    st.dataframe(low_df, width='stretch')

with tab3:
    st.subheader("🚚 Shipment Delays")
    shipments_df['delay_days'] = (shipments_df['actual_delivery'] - shipments_df['expected_delivery']).dt.days
    st.dataframe(shipments_df, width='stretch')

    total_delayed = len(shipments_df[shipments_df['delay_days'] > 0])
    if total_delayed == 0:
        st.success("✅ No delays! All shipments on time.")
    else:
        st.warning(f"⚠️ {total_delayed} Delayed Shipments")

with tab4:
    st.subheader("Raw Data")
    st.dataframe(sales_df.head(), width='stretch')

st.caption("Hybrid Dashboard | MySQL + CSV Support")