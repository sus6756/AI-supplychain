import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Supply Chain AI", layout="wide")
st.title("🚛 AI Supply Chain Dashboard")
st.markdown("**Upload CSV Files → Live Dashboard**")

# ====================== DATA SOURCE (CSV ONLY) ======================
st.sidebar.header("📤 Upload Files")
products_file = st.sidebar.file_uploader("products.csv", type=["csv"])
sales_file = st.sidebar.file_uploader("sales.csv", type=["csv"])
shipments_file = st.sidebar.file_uploader("shipments.csv", type=["csv"])

if st.sidebar.button("Load CSVs"):
    if products_file and sales_file and shipments_file:
        sales_df = pd.read_csv(sales_file)
        products_df = pd.read_csv(products_file)
        shipments_df = pd.read_csv(shipments_file)

        # Save dataframes into Streamlit Session State
        st.session_state.sales_df = sales_df
        st.session_state.products_df = products_df
        st.session_state.shipments_df = shipments_df
        st.session_state.data_loaded = True
        st.success("✅ CSVs Loaded Successfully!")
    else:
        st.sidebar.error("❌ Please upload all 3 CSV files before clicking Load.")

# ====================== CHECK IF DATA LOADED ======================
if 'data_loaded' not in st.session_state:
    st.warning("Please upload your CSV files in the sidebar to populate the dashboard.")
    st.stop()

# Load data from session state
sales_df = st.session_state.sales_df
products_df = st.session_state.products_df
shipments_df = st.session_state.shipments_df

# ====================== DATA CLEANING ======================
sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'], errors='coerce')
shipments_df['expected_delivery'] = pd.to_datetime(shipments_df['expected_delivery'], errors='coerce')
shipments_df['actual_delivery'] = pd.to_datetime(shipments_df['actual_delivery'], errors='coerce')
sales_df['revenue'] = pd.to_numeric(sales_df['revenue'], errors='coerce')

# ====================== KPI METRICS ======================
col1, col2, col3, col4 = st.columns(4)
total_rev = sales_df['revenue'].sum()
delayed = len(shipments_df[shipments_df['actual_delivery'] > shipments_df['expected_delivery']])
low_stock = len(products_df[products_df['stock_quantity'] < products_df['reorder_level']])

col1.metric("💰 Total Revenue", f"${total_rev:,.0f}")
col2.metric("⚠️ Delayed Shipments", delayed)
col3.metric("📉 Low Stock Items", low_stock)
col4.metric("📦 Total Products", len(products_df))

# ====================== DASHBOARD TABS ======================
tab1, tab2, tab3, tab4 = st.tabs(["📊 Sales", "📦 Inventory", "🚚 Shipments", "📁 Raw Data"])

with tab1:
    st.subheader("Monthly Revenue")
    if not sales_df.empty:
        sales_df['month'] = sales_df['sale_date'].dt.strftime('%Y-%m')
        monthly = sales_df.groupby('month')['revenue'].sum().reset_index()
        fig = px.bar(monthly, x='month', y='revenue', labels={'revenue': 'Revenue ($)', 'month': 'Month'})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sales transactions recorded.")

with tab2:
    st.subheader("Low Stock Products")
    low_df = products_df[products_df['stock_quantity'] < products_df['reorder_level']]
    if not low_df.empty:
        st.dataframe(low_df, use_container_width=True)
    else:
        st.success("✅ Stock levels healthy! No products are below their reorder level.")

with tab3:
    st.subheader("🚚 Shipment Delays")
    shipments_df['delay_days'] = (shipments_df['actual_delivery'] - shipments_df['expected_delivery']).dt.days
    st.dataframe(shipments_df, use_container_width=True)

    total_delayed = len(shipments_df[shipments_df['delay_days'] > 0])
    if total_delayed == 0:
        st.success("✅ No delays! All shipments arrived on or before expected time.")
    else:
        st.warning(f"⚠️ {total_delayed} Delayed Shipments detected.")

with tab4:
    st.subheader("Raw Data Preview")
    st.markdown("### Sales Overview (First 5 Rows)")
    st.dataframe(sales_df.head(), use_container_width=True)

st.caption("Supply Chain Analytics | Powered exclusively by uploaded CSV files")
