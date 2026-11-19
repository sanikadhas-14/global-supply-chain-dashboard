
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Global Logistics Intelligence",
    page_icon="✈️",
    layout="wide"
)

st.markdown("""
<style>
.stApp {
    background-color: #0b1120;
    color: white;
}
[data-testid="stMetric"] {
    background: #172238;
    padding: 18px;
    border-radius: 12px;
}
h1, h2, h3 {
    color: #60a5fa;
}
</style>
""", unsafe_allow_html=True)

st.title("✈️ Global Supply Chain & Logistics Intelligence")
st.caption("Air Cargo | Freight | Carrier | Route | Time Analytics")

@st.cache_data
def load_default():
    return pd.read_csv("cargo_data.csv")

uploaded = st.sidebar.file_uploader(
    "Upload your own CSV dataset",
    type=["csv"]
)

if uploaded:
    data = pd.read_csv(uploaded)
    st.sidebar.success("Custom dataset loaded")
else:
    data = load_default()

required = [
    "cargo_year", "cargo_month", "carrier_name",
    "origin", "dest", "freight_pounds", "passengers"
]

if not all(c in data.columns for c in required):
    st.error("This dashboard requires the air-cargo columns. Please upload a compatible dataset.")
    st.stop()

st.sidebar.header("Dashboard Filters")

years = sorted(data["cargo_year"].dropna().unique().tolist())
selected_years = st.sidebar.multiselect(
    "Select Year",
    years,
    default=years
)

carriers = sorted(data["carrier_name"].dropna().unique().tolist())
selected_carriers = st.sidebar.multiselect(
    "Select Carrier",
    carriers
)

filtered = data[data["cargo_year"].isin(selected_years)].copy()

if selected_carriers:
    filtered = filtered[
        filtered["carrier_name"].isin(selected_carriers)
    ]

if filtered.empty:
    st.warning("No data available for these filters.")
    st.stop()

total_freight = filtered["freight_pounds"].sum()
total_passengers = filtered["passengers"].sum()
total_records = len(filtered)
total_carriers = filtered["carrier_name"].nunique()

st.subheader("Executive Overview")

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Records", f"{total_records:,}")
c2.metric("Total Freight", f"{total_freight:,.0f} lbs")
c3.metric("Total Passengers", f"{total_passengers:,.0f}")
c4.metric("Active Carriers", f"{total_carriers:,}")

st.divider()

st.subheader("Freight Analytics")

monthly = (
    filtered.groupby(["cargo_year", "cargo_month"], as_index=False)
    ["freight_pounds"].sum()
)

monthly["Period"] = (
    monthly["cargo_year"].astype(str) + "-" +
    monthly["cargo_month"].astype(str).str.zfill(2)
)

fig1 = px.line(
    monthly,
    x="Period",
    y="freight_pounds",
    markers=True,
    title="Monthly Freight Movement",
    template="plotly_dark"
)
st.plotly_chart(fig1, use_container_width=True)

left, right = st.columns(2)

carrier_data = (
    filtered.groupby("carrier_name", as_index=False)
    ["freight_pounds"].sum()
    .nlargest(10, "freight_pounds")
)

fig2 = px.bar(
    carrier_data,
    x="freight_pounds",
    y="carrier_name",
    orientation="h",
    title="Top 10 Carriers by Freight",
    template="plotly_dark"
)
fig2.update_layout(yaxis={"categoryorder": "total ascending"})

left.plotly_chart(fig2, use_container_width=True)

route_data = (
    filtered.groupby(["origin", "dest"], as_index=False)
    ["freight_pounds"].sum()
    .nlargest(10, "freight_pounds")
)

route_data["Route"] = (
    route_data["origin"].astype(str) + " → " +
    route_data["dest"].astype(str)
)

fig3 = px.bar(
    route_data,
    x="freight_pounds",
    y="Route",
    orientation="h",
    title="Top 10 Freight Routes",
    template="plotly_dark"
)
fig3.update_layout(yaxis={"categoryorder": "total ascending"})

right.plotly_chart(fig3, use_container_width=True)

st.subheader("Passenger Analysis")

passenger_data = (
    filtered.groupby("carrier_name", as_index=False)
    ["passengers"].sum()
    .nlargest(10, "passengers")
)

fig4 = px.pie(
    passenger_data,
    names="carrier_name",
    values="passengers",
    title="Passenger Share by Top Carriers",
    template="plotly_dark"
)
st.plotly_chart(fig4, use_container_width=True)

st.subheader("Detailed Cargo Records")
st.dataframe(filtered.head(1000), use_container_width=True)

st.download_button(
    "Download Filtered Data",
    filtered.to_csv(index=False),
    "filtered_cargo_data.csv",
    "text/csv"
)

st.success("Dashboard analysis completed successfully!")
