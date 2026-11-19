
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(
    page_title="Global Logistics Intelligence",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------- DESIGN ----------------
st.markdown("""
<style>
.stApp {
    background: #08111f;
    color: #f1f5f9;
}
[data-testid="stSidebar"] {
    background: #101d30;
    border-right: 1px solid #263b56;
}
[data-testid="stMetric"] {
    background: linear-gradient(135deg,#14243b,#1b3150);
    border: 1px solid #294665;
    padding: 18px;
    border-radius: 14px;
}
[data-testid="stMetricLabel"] {
    color: #9db4d0;
}
[data-testid="stMetricValue"] {
    color: #60a5fa;
}
h1, h2, h3 {
    color: #eaf3ff;
}
.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
}
div[data-testid="stPlotlyChart"] {
    background: #101d30;
    padding: 10px;
    border-radius: 14px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    data = pd.read_csv("cargo_data.csv")

    required = [
        "cargo_year", "cargo_month", "carrier_name",
        "origin", "dest", "freight_pounds", "passengers"
    ]

    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

    for col in ["cargo_year", "cargo_month", "freight_pounds", "passengers"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(subset=["cargo_year", "cargo_month"])
    data["cargo_year"] = data["cargo_year"].astype(int)
    data["cargo_month"] = data["cargo_month"].astype(int)

    for col in ["carrier_name", "origin", "dest"]:
        data[col] = data[col].fillna("Unknown").astype(str)

    data["freight_pounds"] = data["freight_pounds"].fillna(0)
    data["passengers"] = data["passengers"].fillna(0)

    data = data[
        (data["cargo_month"].between(1, 12)) &
        (data["freight_pounds"] >= 0) &
        (data["passengers"] >= 0)
    ]

    data = data.drop_duplicates()
    data["route"] = data["origin"] + " → " + data["dest"]
    data["period"] = (
        data["cargo_year"].astype(str) + "-" +
        data["cargo_month"].astype(str).str.zfill(2)
    )
    return data

try:
    df = load_data()
except Exception as e:
    st.error(f"Dataset loading error: {e}")
    st.info("Check that cargo_data.csv is uploaded in the same GitHub repository as app.py.")
    st.stop()

# ---------------- HEADER ----------------
st.title("✈️ GLOBAL SUPPLY CHAIN & LOGISTICS INTELLIGENCE")
st.caption("AIR CARGO ANALYTICS  |  FREIGHT MOVEMENT  |  AIRLINE PERFORMANCE  |  ROUTE INTELLIGENCE")
st.divider()

# ---------------- SIDEBAR ----------------
st.sidebar.title("✈️ LOGISTICS CONTROL")
st.sidebar.caption("Interactive Analytics Platform")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Executive Command Center",
        "Cargo Intelligence",
        "Airline Performance",
        "Route Intelligence",
        "Time & Trend Analysis",
        "Business Insights",
        "Data Explorer"
    ]
)

st.sidebar.divider()
st.sidebar.subheader("DATA FILTERS")

years = sorted(df["cargo_year"].unique().tolist())
selected_years = st.sidebar.multiselect(
    "Select Year",
    years,
    default=years
)

carriers = sorted(df["carrier_name"].unique().tolist())
selected_carriers = st.sidebar.multiselect(
    "Select Airlines",
    carriers,
    default=[]
)

filtered = df[df["cargo_year"].isin(selected_years)].copy()

if selected_carriers:
    filtered = filtered[filtered["carrier_name"].isin(selected_carriers)]

if filtered.empty:
    st.warning("No records match the selected filters. Change the filters.")
    st.stop()

# ---------------- COMMON METRICS ----------------
total_records = len(filtered)
total_freight = filtered["freight_pounds"].sum()
total_passengers = filtered["passengers"].sum()
total_carriers = filtered["carrier_name"].nunique()
total_routes = filtered["route"].nunique()
total_origins = filtered["origin"].nunique()
total_destinations = filtered["dest"].nunique()

def show_kpis():
    a, b, c, d = st.columns(4)
    a.metric("Total Cargo Records", f"{total_records:,}")
    b.metric("Total Freight", f"{total_freight:,.0f} lbs")
    c.metric("Total Passengers", f"{total_passengers:,.0f}")
    d.metric("Active Airlines", f"{total_carriers:,}")

def chart_layout(fig, height=400):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#101d30",
        plot_bgcolor="#101d30",
        font=dict(color="#e5edf8"),
        height=height,
        margin=dict(l=20, r=20, t=65, b=25),
        legend_title_text=""
    )
    return fig

# ==============================
# 1. EXECUTIVE COMMAND CENTER
# ==============================
if page == "Executive Command Center":

    st.header("📊 Executive Command Center")
    st.write("A complete overview of air cargo and logistics performance.")

    show_kpis()

    a, b, c = st.columns(3)
    a.metric("Active Routes", f"{total_routes:,}")
    b.metric("Origin Airports", f"{total_origins:,}")
    c.metric("Destination Airports", f"{total_destinations:,}")

    st.divider()

    monthly = (
        filtered.groupby("period", as_index=False)
        .agg(freight=("freight_pounds", "sum"))
        .sort_values("period")
    )

    fig = px.area(
        monthly,
        x="period",
        y="freight",
        markers=True,
        title="Overall Freight Movement"
    )
    st.plotly_chart(chart_layout(fig, 420), use_container_width=True)

    left, right = st.columns(2)

    top_carriers = (
        filtered.groupby("carrier_name", as_index=False)
        ["freight_pounds"].sum()
        .nlargest(10, "freight_pounds")
    )

    fig = px.bar(
        top_carriers,
        x="freight_pounds",
        y="carrier_name",
        orientation="h",
        title="Top 10 Airlines"
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    left.plotly_chart(chart_layout(fig), use_container_width=True)

    top_routes = (
        filtered.groupby("route", as_index=False)
        ["freight_pounds"].sum()
        .nlargest(10, "freight_pounds")
    )

    fig = px.bar(
        top_routes,
        x="freight_pounds",
        y="route",
        orientation="h",
        title="Top 10 Cargo Routes"
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    right.plotly_chart(chart_layout(fig), use_container_width=True)

# ==============================
# 2. CARGO INTELLIGENCE
# ==============================
elif page == "Cargo Intelligence":

    st.header("📦 Cargo Intelligence")
    st.write("Understand freight volume, passenger movement and cargo distribution.")

    show_kpis()
    st.divider()

    monthly = (
        filtered.groupby(["cargo_year", "cargo_month"], as_index=False)
        .agg(freight=("freight_pounds", "sum"))
    )

    monthly["month_name"] = pd.to_datetime(
        monthly["cargo_month"], format="%m"
    ).dt.strftime("%b")

    fig = px.line(
        monthly,
        x="cargo_month",
        y="freight",
        color="cargo_year",
        markers=True,
        title="Monthly Freight Comparison"
    )
    st.plotly_chart(chart_layout(fig), use_container_width=True)

    left, right = st.columns(2)

    carrier_freight = (
        filtered.groupby("carrier_name", as_index=False)
        ["freight_pounds"].sum()
        .nlargest(10, "freight_pounds")
    )

    fig = px.pie(
        carrier_freight,
        names="carrier_name",
        values="freight_pounds",
        hole=0.5,
        title="Freight Share by Top Airlines"
    )
    left.plotly_chart(chart_layout(fig), use_container_width=True)

    fig = px.histogram(
        filtered,
        x="freight_pounds",
        nbins=30,
        title="Freight Volume Distribution"
    )
    right.plotly_chart(chart_layout(fig), use_container_width=True)

    st.subheader("Cargo Data Summary")
    st.dataframe(
        filtered[["cargo_year", "cargo_month", "carrier_name",
                  "freight_pounds", "passengers"]].describe(),
        use_container_width=True
    )

# ==============================
# 3. AIRLINE PERFORMANCE
# ==============================
elif page == "Airline Performance":

    st.header("✈️ Airline Performance")
    st.write("Compare airline freight and passenger performance.")

    show_kpis()
    st.divider()

    airline = (
        filtered.groupby("carrier_name", as_index=False)
        .agg(
            freight=("freight_pounds", "sum"),
            passengers=("passengers", "sum"),
            records=("carrier_name", "size")
        )
        .sort_values("freight", ascending=False)
    )

    top = airline.head(15)

    fig = px.bar(
        top,
        x="freight",
        y="carrier_name",
        orientation="h",
        color="freight",
        title="Top 15 Airlines by Freight"
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(chart_layout(fig, 500), use_container_width=True)

    left, right = st.columns(2)

    fig = px.pie(
        top.head(10),
        names="carrier_name",
        values="passengers",
        hole=0.45,
        title="Passenger Share - Top 10 Airlines"
    )
    left.plotly_chart(chart_layout(fig), use_container_width=True)

    fig = px.scatter(
        airline,
        x="passengers",
        y="freight",
        hover_name="carrier_name",
        size="records",
        title="Freight vs Passenger Comparison"
    )
    right.plotly_chart(chart_layout(fig), use_container_width=True)

    st.subheader("Airline Ranking Table")
    st.dataframe(airline, use_container_width=True)

# ==============================
# 4. ROUTE INTELLIGENCE
# ==============================
elif page == "Route Intelligence":

    st.header("🌍 Route Intelligence")
    st.write("Explore major air cargo routes and airport activity.")

    show_kpis()
    st.divider()

    routes = (
        filtered.groupby(["origin", "dest", "route"], as_index=False)
        .agg(
            freight=("freight_pounds", "sum"),
            passengers=("passengers", "sum"),
            records=("route", "size")
        )
        .sort_values("freight", ascending=False)
    )

    top_routes = routes.head(20)

    fig = px.bar(
        top_routes,
        x="freight",
        y="route",
        orientation="h",
        color="freight",
        title="Top 20 Routes by Freight"
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(chart_layout(fig, 600), use_container_width=True)

    left, right = st.columns(2)

    origin_data = (
        filtered.groupby("origin", as_index=False)
        ["freight_pounds"].sum()
        .nlargest(10, "freight_pounds")
    )

    fig = px.bar(
        origin_data,
        x="origin",
        y="freight_pounds",
        title="Top 10 Origin Airports"
    )
    left.plotly_chart(chart_layout(fig), use_container_width=True)

    dest_data = (
        filtered.groupby("dest", as_index=False)
        ["freight_pounds"].sum()
        .nlargest(10, "freight_pounds")
    )

    fig = px.bar(
        dest_data,
        x="dest",
        y="freight_pounds",
        title="Top 10 Destination Airports"
    )
    right.plotly_chart(chart_layout(fig), use_container_width=True)

    st.subheader("Route Details")
    st.dataframe(routes, use_container_width=True)

# ==============================
# 5. TIME & TREND ANALYSIS
# ==============================
elif page == "Time & Trend Analysis":

    st.header("📈 Time & Trend Analysis")
    st.write("Analyze historical freight movement and yearly patterns.")

    show_kpis()
    st.divider()

    yearly = (
        filtered.groupby("cargo_year", as_index=False)
        .agg(
            freight=("freight_pounds", "sum"),
            passengers=("passengers", "sum"),
            records=("cargo_year", "size")
        )
    )

    left, right = st.columns(2)

    fig = px.line(
        yearly,
        x="cargo_year",
        y="freight",
        markers=True,
        title="Yearly Freight Trend"
    )
    left.plotly_chart(chart_layout(fig), use_container_width=True)

    fig = px.bar(
        yearly,
        x="cargo_year",
        y="passengers",
        title="Yearly Passenger Movement"
    )
    right.plotly_chart(chart_layout(fig), use_container_width=True)

    monthly = (
        filtered.groupby("cargo_month", as_index=False)
        ["freight_pounds"].sum()
    )

    monthly["month"] = pd.to_datetime(
        monthly["cargo_month"], format="%m"
    ).dt.strftime("%B")

    fig = px.bar(
        monthly,
        x="month",
        y="freight_pounds",
        title="Month-wise Freight Pattern"
    )
    st.plotly_chart(chart_layout(fig), use_container_width=True)

    st.subheader("Year-wise Performance")
    st.dataframe(yearly, use_container_width=True)

# ==============================
# 6. BUSINESS INSIGHTS
# ==============================
elif page == "Business Insights":

    st.header("💡 Business Intelligence & Insights")
    st.write("Automatically generated insights from the selected dataset.")

    show_kpis()
    st.divider()

    carrier = (
        filtered.groupby("carrier_name")["freight_pounds"]
        .sum().sort_values(ascending=False)
    )

    route = (
        filtered.groupby("route")["freight_pounds"]
        .sum().sort_values(ascending=False)
    )

    origin = (
        filtered.groupby("origin")["freight_pounds"]
        .sum().sort_values(ascending=False)
    )

    destination = (
        filtered.groupby("dest")["freight_pounds"]
        .sum().sort_values(ascending=False)
    )

    month = (
        filtered.groupby("cargo_month")["freight_pounds"]
        .sum().sort_values(ascending=False)
    )

    def safe_name(series):
        return str(series.index[0]) if len(series) else "Not available"

    def safe_value(series):
        return float(series.iloc[0]) if len(series) else 0

    a, b = st.columns(2)

    with a:
        st.subheader("🏆 Leading Airline")
        st.metric("Top Airline", safe_name(carrier))
        st.metric("Freight Handled", f"{safe_value(carrier):,.0f} lbs")

        st.subheader("🛫 Leading Origin")
        st.metric("Origin Airport", safe_name(origin))

        st.subheader("📍 Leading Destination")
        st.metric("Destination Airport", safe_name(destination))

    with b:
        st.subheader("🔀 Busiest Cargo Route")
        st.metric("Top Route", safe_name(route))
        st.metric("Route Freight", f"{safe_value(route):,.0f} lbs")

        st.subheader("📅 Highest Freight Month")
        if len(month):
            st.metric(
                "Month",
                pd.to_datetime(int(month.index[0]), format="%m").strftime("%B")
            )

        st.subheader("📊 Average Freight per Record")
        st.metric(
            "Average Freight",
            f"{filtered['freight_pounds'].mean():,.2f} lbs"
        )

    st.divider()
    st.subheader("Business Recommendations")

    st.markdown("""
    - Monitor high-volume routes to improve cargo capacity planning.
    - Compare airline freight performance to identify operational leaders.
    - Study monthly freight patterns for better resource allocation.
    - Monitor airport activity to understand cargo concentration.
    - Use historical trends to support logistics planning decisions.
    """)

    st.caption("Insights are calculated from the selected dataset and filters.")

# ==============================
# 7. DATA EXPLORER
# ==============================
elif page == "Data Explorer":

    st.header("🗂️ Data Explorer")
    st.write("Explore, filter, inspect and download cargo records.")

    st.subheader("Dataset Overview")

    a, b, c, d = st.columns(4)
    a.metric("Rows", f"{len(filtered):,}")
    b.metric("Columns", f"{len(filtered.columns):,}")
    c.metric("Airlines", f"{filtered['carrier_name'].nunique():,}")
    d.metric("Routes", f"{filtered['route'].nunique():,}")

    st.divider()

    st.subheader("Column Information")

    info = pd.DataFrame({
        "Column": filtered.columns,
        "Data Type": [str(x) for x in filtered.dtypes],
        "Missing Values": filtered.isnull().sum().values
    })

    st.dataframe(info, use_container_width=True)

    st.subheader("Filter Records")

    search = st.text_input("Search airline, origin or destination")

    explorer = filtered.copy()

    if search:
        mask = (
            explorer["carrier_name"].str.contains(search, case=False, na=False) |
            explorer["origin"].str.contains(search, case=False, na=False) |
            explorer["dest"].str.contains(search, case=False, na=False)
        )
        explorer = explorer[mask]

    st.caption(f"Showing {len(explorer):,} matching records")

    st.dataframe(explorer, use_container_width=True, height=450)

    st.download_button(
        "⬇️ Download Filtered CSV",
        data=explorer.to_csv(index=False).encode("utf-8"),
        file_name="filtered_air_cargo_data.csv",
        mime="text/csv"
    )

    st.subheader("Upload Compatible Air Cargo CSV")

    uploaded = st.file_uploader(
        "Upload another air cargo CSV for preview",
        type=["csv"]
    )

    if uploaded is not None:
        try:
            new_data = pd.read_csv(uploaded)
            st.success("CSV uploaded successfully!")
            st.write("Rows:", len(new_data))
            st.write("Columns:", len(new_data.columns))
            st.dataframe(new_data.head(100), use_container_width=True)
        except Exception as e:
            st.error(f"Could not read CSV: {e}")

# ---------------- FOOTER ----------------
st.divider()
st.caption(
    "GLOBAL SUPPLY CHAIN & LOGISTICS INTELLIGENCE | "
    "Powered by Python, Streamlit, Pandas and Plotly"
)
