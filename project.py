import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Supply Chain AI", layout="wide")
st.title("🚛 AI Supply Chain Dashboard")
st.markdown("**Excel + CSV Support**")

# ====================== DATA SOURCE ======================
option = st.sidebar.radio("Select Data Source", ["📤 Excel Upload", "📁 CSV Upload"])

sales_df = products_df = shipments_df = None
data_loaded = False

if option == "📤 Excel Upload":
    uploaded_file = st.sidebar.file_uploader("Upload supply_chain_dataset.xlsx", type=["xlsx"])
    if uploaded_file:
        products_df = pd.read_excel(uploaded_file, sheet_name='products')
        shipments_df = pd.read_excel(uploaded_file, sheet_name='shipments')
        sales_df = pd.read_excel(uploaded_file, sheet_name='sales')
        data_loaded = True
        st.success("✅ Excel Loaded Successfully!")

elif option == "📁 CSV Upload":
    st.sidebar.header("Upload 3 CSVs")
    prod = st.sidebar.file_uploader("products.csv", type=["csv"])
    sale = st.sidebar.file_uploader("sales.csv", type=["csv"])
    ship = st.sidebar.file_uploader("shipments.csv", type=["csv"])

    if prod and sale and ship:
        products_df = pd.read_csv(prod)
        sales_df = pd.read_csv(sale)
        shipments_df = pd.read_csv(ship)
        data_loaded = True
        st.success("✅ CSVs Loaded!")

if not data_loaded:
    st.warning("👈 Please upload your file from sidebar")
    st.stop()

# ====================== CLEANING ======================
sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'], errors='coerce')
shipments_df['expected_delivery'] = pd.to_datetime(shipments_df['expected_delivery'], errors='coerce')
shipments_df['actual_delivery'] = pd.to_datetime(shipments_df['actual_delivery'], errors='coerce')
sales_df['revenue'] = pd.to_numeric(sales_df['revenue'], errors='coerce')

# ====================== METRICS ======================
col1, col2, col3, col4 = st.columns(4)
col1.metric("💰 Total Revenue", f"${sales_df['revenue'].sum():,.0f}")
col2.metric("⚠️ Delayed Shipments", len(shipments_df[shipments_df['actual_delivery'] > shipments_df['expected_delivery']]))
col3.metric("📉 Low Stock", len(products_df[products_df['stock_quantity'] < products_df['reorder_level']]))
col4.metric("📦 Total Products", len(products_df))

# ====================== TABS ======================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Sales", "📦 Inventory", "🚚 Shipments", "📁 Preview"])

with tab1:
    st.subheader("Monthly Revenue")
    sales_df['month'] = sales_df['sale_date'].dt.strftime('%Y-%m')
    monthly = sales_df.groupby('month')['revenue'].sum().reset_index()
    fig = px.bar(monthly, x='month', y='revenue')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.subheader("Low Stock Products")
    low = products_df[products_df['stock_quantity'] < products_df['reorder_level']]
    st.dataframe(low, use_container_width=True)

with tab3:
    st.subheader("🚚 Shipment Delays")
    shipments_df['delay_days'] = (shipments_df['actual_delivery'] - shipments_df['expected_delivery']).dt.days
    st.dataframe(shipments_df[['shipment_id', 'product_id', 'expected_delivery', 
                               'actual_delivery', 'delay_days']], use_container_width=True)

with tab4:
    st.subheader("Raw Data Preview")
    st.dataframe(sales_df.head(), use_container_width=True)

st.caption("Supply Chain Project Dashboard")
