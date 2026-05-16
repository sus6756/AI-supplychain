import pandas as pd
import streamlit as st
import plotly.express as px
import mysql.connector
from mysql.connector import Error

st.set_page_config(page_title="Supply Chain AI", layout="wide")
st.title("🚛 AI Supply Chain Dashboard")
st.markdown("**Excel + CSV + MySQL**")

# ====================== DATA SOURCE ======================
option = st.sidebar.radio("Select Data Source", 
                         ["📤 Excel Upload", "📁 CSV Upload", "🗄️ MySQL Database"])

sales_df = products_df = shipments_df = None
data_loaded = False

# ------------------- EXCEL -------------------
if option == "📤 Excel Upload":
    uploaded_file = st.sidebar.file_uploader("Upload supply_chain_dataset.xlsx", type=["xlsx"])
    if uploaded_file:
        products_df = pd.read_excel(uploaded_file, sheet_name='products')
        shipments_df = pd.read_excel(uploaded_file, sheet_name='shipments')
        sales_df = pd.read_excel(uploaded_file, sheet_name='sales')
        data_loaded = True
        st.success("✅ Excel Loaded!")

# ------------------- CSV -------------------
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

# ------------------- MySQL -------------------
elif option == "🗄️ MySQL Database":
    st.sidebar.header("MySQL Connection")
    host = st.sidebar.text_input("Host", "localhost")
    user = st.sidebar.text_input("User", "root")
    password = st.sidebar.text_input("Password", "code_RED", type="password")
    database = st.sidebar.text_input("Database", "supply_chain")

    if st.sidebar.button("🔗 Connect to MySQL"):
        try:
            conn = mysql.connector.connect(
                host=host, user=user, password=password, database=database
            )
            sales_df = pd.read_sql("SELECT * FROM sales", conn)
            products_df = pd.read_sql("SELECT * FROM products", conn)
            shipments_df = pd.read_sql("SELECT * FROM shipments", conn)
            data_loaded = True
            st.session_state.conn = conn
            st.success("✅ Connected to MySQL!")
        except Error as e:
            st.error(f"❌ Connection Failed: {e}")

    # ====================== NEW: LOAD EXCEL TO MYSQL ======================
    st.sidebar.header("📤 Load Excel → MySQL")
    excel_to_db = st.sidebar.file_uploader("Upload Excel to insert into DB", type=["xlsx"], key="to_db")

    if excel_to_db and st.sidebar.button("Insert Data into MySQL"):
        try:
            conn = mysql.connector.connect(
                host=host, user=user, password=password, database=database
            )
            cursor = conn.cursor()

            products = pd.read_excel(excel_to_db, sheet_name='products')
            sales = pd.read_excel(excel_to_db, sheet_name='sales')
            shipments = pd.read_excel(excel_to_db, sheet_name='shipments')

            # Insert Products
            for _, row in products.iterrows():
                cursor.execute("""INSERT IGNORE INTO products VALUES (%s,%s,%s,%s,%s,%s,%s)""", tuple(row))
            
            # Insert Sales
            for _, row in sales.iterrows():
                cursor.execute("""INSERT IGNORE INTO sales VALUES (%s,%s,%s,%s,%s)""", tuple(row))
            
            # Insert Shipments
            for _, row in shipments.iterrows():
                cursor.execute("""INSERT IGNORE INTO shipments VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", tuple(row))

            conn.commit()
            st.success("✅ Data successfully inserted into MySQL!")
            data_loaded = True
        except Exception as e:
            st.error(f"Insert Error: {e}")

if not data_loaded:
    st.warning("Please select a source and upload/connect")
    st.stop()

# ====================== DASHBOARD (Rest same) ======================
sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'], errors='coerce')
shipments_df['expected_delivery'] = pd.to_datetime(shipments_df['expected_delivery'], errors='coerce')
shipments_df['actual_delivery'] = pd.to_datetime(shipments_df['actual_delivery'], errors='coerce')
sales_df['revenue'] = pd.to_numeric(sales_df['revenue'], errors='coerce')

col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"${sales_df['revenue'].sum():,.0f}")
col2.metric("⚠️ Delayed", len(shipments_df[shipments_df['actual_delivery'] > shipments_df['expected_delivery']]))
col3.metric("📉 Low Stock", len(products_df[products_df['stock_quantity'] < products_df['reorder_level']]))
col4.metric("📦 Products", len(products_df))

tab1, tab2, tab3, tab4 = st.tabs(["📊 Sales", "📦 Inventory", "🚚 Shipments", "🔍 SQL Query"])

with tab1: 
    st.subheader("Monthly Revenue")
    sales_df['month'] = sales_df['sale_date'].dt.strftime('%Y-%m')
    monthly = sales_df.groupby('month')['revenue'].sum().reset_index()
    fig = px.bar(monthly, x='month', y='revenue')
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("Custom SQL Query")
    query = st.text_area("Write your SQL", "SELECT * FROM sales LIMIT 10")
    if st.button("Run Query") and 'conn' in st.session_state:
        try:
            result = pd.read_sql(query, st.session_state.conn)
            st.dataframe(result, use_container_width=True)
        except Exception as e:
            st.error(f"Query Error: {e}")

st.caption("Supply Chain Dashboard")
