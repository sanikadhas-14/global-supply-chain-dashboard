
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# =====================================================
# PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="Global Logistics Intelligence",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# PROFESSIONAL DASHBOARD DESIGN
# =====================================================
st.markdown("""
<style>
.stApp {
    background: #080f1e;
    color: #f1f5f9;
}
[data-testid="stHeader"] {
    background: #080f1e;
}
[data-testid="stSidebar"] {
    background: #111e32;
    border-right: 1px solid #29415e;
}
[data-testid="stSidebar"] * {
    color: #f1f5f9 !important;
}
.stApp h1, .stApp h2, .stApp h3 {
    color: #f8fafc !important;
}
.stApp p, .stApp label, .stApp li {
    color: #dbeafe;
}
[data-testid="stMetric"] {
    background: linear-gradient(135deg,#142640,#1d3655);
    border: 1px solid #355675;
    padding: 20px;
    border-radius: 15px;
    min-height: 115px;
}
[data-testid="stMetricLabel"] {
    color: #cbd5e1 !important;
}
[data-testid="stMetricValue"] {
    color: #38bdf8 !important;
}
[data-testid="stMetricDelta"] {
    color: #4ade80 !important;
}
div[data-testid="stPlotlyChart"] {
    background: #111e32;
    border: 1px solid #263e5c;
    border-radius: 14px;
    padding: 8px;
}
div[data-testid="stDataFrame"] {
    border: 1px solid #29415e;
    border-radius: 12px;
}
.stButton button, .stDownloadButton button {
    border-radius: 9px;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}
hr {
    border-color: #29415e;
}
</style>
""", unsafe_allow_html=True)

# =====================================================
# LOAD AND CLEAN DATA
# =====================================================
@st.cache_data
def load_data():
    data = pd.read_csv("cargo_data.csv")

    required = [
        "cargo_year", "cargo_month", "carrier_name",
        "origin", "dest", "freight_pounds", "passengers"
    ]

    missing = [c for c in required if c not in data.columns]
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))

    for col in ["cargo_year", "cargo_month",
                "freight_pounds", "passengers"]:
        data[col] = pd.to_numeric(data[col], errors="coerce")

    data = data.dropna(subset=["cargo_year", "cargo_month"])

    data["cargo_year"] = data["cargo_year"].astype(int)
    data["cargo_month"] = data["cargo_month"].astype(int)

    for col in ["carrier_name", "origin", "dest"]:
        data[col] = data[col].fillna("Unknown").astype(str)

    data["freight_pounds"] = data["freight_pounds"].fillna(0)
    data["passengers"] = data["passengers"].fillna(0)

    data = data[
        data["cargo_month"].between(1, 12) &
        (data["freight_pounds"] >= 0) &
        (data["passengers"] >= 0)
    ].drop_duplicates()

    data["route"] = data["origin"] + " → " + data["dest"]
    data["period"] = (
        data["cargo_year"].astype(str) + "-" +
        data["cargo_month"].astype(str).str.zfill(2)
    )

    return data


try:
    df = load_data()
except Exception as e:
    st.error(f"Dataset error: {e}")
    st.info("Make sure cargo_data.csv is present in your GitHub repository.")
    st.stop()

# =====================================================
# SIDEBAR NAVIGATION
# =====================================================
st.sidebar.markdown("# ✈️ LOGISTICS IQ")
st.sidebar.caption("GLOBAL AIR CARGO ANALYTICS")
st.sidebar.divider()

page = st.sidebar.radio(
    "DASHBOARD NAVIGATION",
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
st.sidebar.markdown("### DATA CONTROLS")

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

months = sorted(df["cargo_month"].unique().tolist())

selected_months = st.sidebar.multiselect(
    "Select Months",
    months,
    default=months,
    format_func=lambda x: pd.to_datetime(
        int(x), format="%m"
    ).strftime("%B")
)

filtered = df[
    df["cargo_year"].isin(selected_years) &
    df["cargo_month"].isin(selected_months)
].copy()

if selected_carriers:
    filtered = filtered[
        filtered["carrier_name"].isin(selected_carriers)
    ]

if filtered.empty:
    st.warning("No records found. Please change your filters.")
    st.stop()

# =====================================================
# COMMON FUNCTIONS
# =====================================================
def make_chart(fig, height=400):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#111e32",
        plot_bgcolor="#111e32",
        font=dict(color="#e2e8f0"),
        height=height,
        margin=dict(l=25, r=25, t=65, b=30),
        legend_title_text=""
    )
    return fig


def show_kpis(data):
    a, b, c, d = st.columns(4)

    a.metric("Cargo Records", f"{len(data):,}")
    b.metric("Total Freight", f"{data['freight_pounds'].sum():,.0f} lbs")
    c.metric("Passengers", f"{data['passengers'].sum():,.0f}")
    d.metric("Active Airlines", f"{data['carrier_name'].nunique():,}")


def top_airlines(data, n=10):
    return (
        data.groupby("carrier_name", as_index=False)
        ["freight_pounds"].sum()
        .nlargest(n, "freight_pounds")
    )


def top_routes(data, n=10):
    return (
        data.groupby("route", as_index=False)
        ["freight_pounds"].sum()
        .nlargest(n, "freight_pounds")
    )


# =====================================================
# GLOBAL HEADER
# =====================================================
st.title("✈️ GLOBAL SUPPLY CHAIN & LOGISTICS INTELLIGENCE")
st.caption(
    "AIR CARGO ANALYTICS  |  FREIGHT MOVEMENT  |  "
    "AIRLINE PERFORMANCE  |  ROUTE NETWORK"
)

st.divider()

# =====================================================
# 1. EXECUTIVE COMMAND CENTER
# =====================================================
if page == "Executive Command Center":

    st.header("📊 Executive Command Center")
    st.write("Your complete air cargo business overview.")

    show_kpis(filtered)

    a, b, c = st.columns(3)
    a.metric("Unique Routes", f"{filtered['route'].nunique():,}")
    b.metric("Origin Airports", f"{filtered['origin'].nunique():,}")
    c.metric("Destination Airports", f"{filtered['dest'].nunique():,}")

    st.divider()

    monthly = (
        filtered.groupby("period", as_index=False)
        ["freight_pounds"].sum()
        .sort_values("period")
    )

    fig = px.area(
        monthly,
        x="period",
        y="freight_pounds",
        markers=True,
        title="Total Freight Movement Over Time"
    )
    st.plotly_chart(make_chart(fig, 420), use_container_width=True)

    left, right = st.columns(2)

    airlines = top_airlines(filtered, 10)

    fig = px.bar(
        airlines,
        x="freight_pounds",
        y="carrier_name",
        orientation="h",
        title="Top 10 Airlines by Freight"
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    left.plotly_chart(make_chart(fig), use_container_width=True)

    routes = top_routes(filtered, 10)

    fig = px.bar(
        routes,
        x="freight_pounds",
        y="route",
        orientation="h",
        title="Top 10 Cargo Routes"
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    right.plotly_chart(make_chart(fig), use_container_width=True)

    st.subheader("Quick Business Summary")

    best_airline = airlines.iloc[0]["carrier_name"] if not airlines.empty else "N/A"
    best_route = routes.iloc[0]["route"] if not routes.empty else "N/A"

    st.info(f"Leading airline by freight: {best_airline}")
    st.info(f"Highest freight route: {best_route}")

# =====================================================
# 2. CARGO INTELLIGENCE
# =====================================================
elif page == "Cargo Intelligence":

    st.header("📦 Cargo Intelligence")
    st.write("Understand freight distribution and passenger movement.")

    show_kpis(filtered)
    st.divider()

    left, right = st.columns(2)

    monthly = (
        filtered.groupby(["cargo_year", "cargo_month"], as_index=False)
        ["freight_pounds"].sum()
    )

    fig = px.line(
        monthly,
        x="cargo_month",
        y="freight_pounds",
        color="cargo_year",
        markers=True,
        title="Monthly Freight Comparison by Year"
    )
    left.plotly_chart(make_chart(fig), use_container_width=True)

    airline_share = top_airlines(filtered, 10)

    fig = px.pie(
        airline_share,
        names="carrier_name",
        values="freight_pounds",
        hole=0.5,
        title="Freight Share - Top 10 Airlines"
    )
    right.plotly_chart(make_chart(fig), use_container_width=True)

    st.subheader("Freight Volume Distribution")

    fig = px.histogram(
        filtered,
        x="freight_pounds",
        nbins=35,
        title="Distribution of Freight Records"
    )
    st.plotly_chart(make_chart(fig), use_container_width=True)

    st.subheader("Passenger vs Freight Analysis")

    fig = px.scatter(
        filtered.sample(min(3000, len(filtered)), random_state=42),
        x="passengers",
        y="freight_pounds",
        color="cargo_year",
        hover_data=["carrier_name", "origin", "dest"],
        title="Passenger and Freight Relationship"
    )
    st.plotly_chart(make_chart(fig), use_container_width=True)

# =====================================================
# 3. AIRLINE PERFORMANCE
# =====================================================
elif page == "Airline Performance":

    st.header("✈️ Airline Performance")
    st.write("Compare airline activity and freight contribution.")

    show_kpis(filtered)
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

    fig = px.bar(
        airline.head(15),
        x="freight",
        y="carrier_name",
        orientation="h",
        color="freight",
        title="Top 15 Airlines by Freight"
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(make_chart(fig, 520), use_container_width=True)

    left, right = st.columns(2)

    fig = px.pie(
        airline.head(10),
        names="carrier_name",
        values="passengers",
        hole=0.45,
        title="Passenger Share by Airline"
    )
    left.plotly_chart(make_chart(fig), use_container_width=True)

    fig = px.scatter(
        airline,
        x="passengers",
        y="freight",
        size="records",
        hover_name="carrier_name",
        title="Airline Freight vs Passenger Performance"
    )
    right.plotly_chart(make_chart(fig), use_container_width=True)

    st.subheader("Airline Performance Ranking")
    st.dataframe(airline, use_container_width=True)

# =====================================================
# 4. ROUTE INTELLIGENCE
# =====================================================
elif page == "Route Intelligence":

    st.header("🌍 Route Intelligence")
    st.write("Explore major cargo corridors and airport activity.")

    show_kpis(filtered)
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

    fig = px.bar(
        routes.head(20),
        x="freight",
        y="route",
        orientation="h",
        color="freight",
        title="Top 20 Routes by Freight"
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(make_chart(fig, 620), use_container_width=True)

    left, right = st.columns(2)

    origin = (
        filtered.groupby("origin", as_index=False)
        ["freight_pounds"].sum()
        .nlargest(10, "freight_pounds")
    )

    fig = px.bar(
        origin,
        x="origin",
        y="freight_pounds",
        title="Top 10 Origin Airports"
    )
    left.plotly_chart(make_chart(fig), use_container_width=True)

    destination = (
        filtered.groupby("dest", as_index=False)
        ["freight_pounds"].sum()
        .nlargest(10, "freight_pounds")
    )

    fig = px.bar(
        destination,
        x="dest",
        y="freight_pounds",
        title="Top 10 Destination Airports"
    )
    right.plotly_chart(make_chart(fig), use_container_width=True)

    st.subheader("Complete Route Network Table")
    st.dataframe(routes, use_container_width=True)

# =====================================================
# 5. TIME AND TREND ANALYSIS
# =====================================================
elif page == "Time & Trend Analysis":

    st.header("📈 Time & Trend Analysis")
    st.write("Discover historical patterns and seasonal freight activity.")

    show_kpis(filtered)
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
    left.plotly_chart(make_chart(fig), use_container_width=True)

    fig = px.bar(
        yearly,
        x="cargo_year",
        y="passengers",
        title="Yearly Passenger Movement"
    )
    right.plotly_chart(make_chart(fig), use_container_width=True)

    monthly = (
        filtered.groupby(["cargo_year", "cargo_month"], as_index=False)
        ["freight_pounds"].sum()
    )

    monthly["month_name"] = pd.to_datetime(
        monthly["cargo_month"], format="%m"
    ).dt.strftime("%b")

    heat = monthly.pivot(
        index="cargo_year",
        columns="month_name",
        values="freight_pounds"
    )

    month_order = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    heat = heat.reindex(columns=month_order)

    fig = px.imshow(
        heat,
        aspect="auto",
        color_continuous_scale="Blues",
        title="Seasonality Heatmap: Year vs Month",
        labels=dict(x="Month", y="Year", color="Freight")
    )
    st.plotly_chart(make_chart(fig, 420), use_container_width=True)

    st.subheader("Yearly Performance Table")
    st.dataframe(yearly, use_container_width=True)

# =====================================================
# 6. BUSINESS INSIGHTS
# =====================================================
elif page == "Business Insights":

    st.header("💡 Business Intelligence Center")
    st.write("Automatic findings calculated from the selected cargo data.")

    show_kpis(filtered)
    st.divider()

    airline = (
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

    monthly = (
        filtered.groupby("cargo_month")["freight_pounds"]
        .sum().sort_values(ascending=False)
    )

    a, b = st.columns(2)

    with a:
        st.subheader("🏆 Leading Airline")
        if len(airline):
            st.metric("Top Airline", str(airline.index[0]))
            st.metric("Freight Handled", f"{airline.iloc[0]:,.0f} lbs")

        st.subheader("🛫 Leading Origin")
        if len(origin):
            st.metric("Top Origin", str(origin.index[0]))

        st.subheader("📍 Leading Destination")
        if len(destination):
            st.metric("Top Destination", str(destination.index[0]))

    with b:
        st.subheader("🔀 Busiest Route")
        if len(route):
            st.metric("Top Route", str(route.index[0]))
            st.metric("Route Freight", f"{route.iloc[0]:,.0f} lbs")

        st.subheader("📅 Highest Freight Month")
        if len(monthly):
            month_name = pd.to_datetime(
                int(monthly.index[0]), format="%m"
            ).strftime("%B")
            st.metric("Top Month", month_name)

        st.subheader("📊 Average Freight")
        st.metric(
            "Per Record",
            f"{filtered['freight_pounds'].mean():,.2f} lbs"
        )

    st.divider()

    st.subheader("🚨 Cargo Anomaly Detection")

    # IQR statistical method, not a trained ML model
    q1 = filtered["freight_pounds"].quantile(0.25)
    q3 = filtered["freight_pounds"].quantile(0.75)
    iqr = q3 - q1
    upper_limit = q3 + (1.5 * iqr)
    lower_limit = max(0, q1 - (1.5 * iqr))

    anomalies = filtered[
        (filtered["freight_pounds"] > upper_limit) |
        (filtered["freight_pounds"] < lower_limit)
    ]

    x, y = st.columns(2)
    x.metric("Unusual Records", f"{len(anomalies):,}")
    y.metric(
        "Unusual Record Share",
        f"{len(anomalies) / len(filtered) * 100:.2f}%"
    )

    st.caption(
        "Statistical anomaly screening using the Interquartile Range (IQR) method."
    )

    st.dataframe(
        anomalies[
            ["cargo_year", "cargo_month", "carrier_name",
             "origin", "dest", "freight_pounds"]
        ].head(100),
        use_container_width=True
    )

    st.subheader("Business Recommendations")

    st.markdown("""
    - Monitor high-volume cargo routes for capacity planning.
    - Compare airline freight contribution to understand market concentration.
    - Study seasonal freight patterns for resource planning.
    - Monitor airport activity to identify important cargo hubs.
    - Investigate unusual freight records before making operational decisions.
    """)

# =====================================================
# 7. DATA EXPLORER
# =====================================================
elif page == "Data Explorer":

    st.header("🗂️ Data Explorer")
    st.write("Explore, search, inspect and download air cargo records.")

    a, b, c, d = st.columns(4)

    a.metric("Total Rows", f"{len(filtered):,}")
    b.metric("Total Columns", f"{len(filtered.columns):,}")
    c.metric("Airlines", f"{filtered['carrier_name'].nunique():,}")
    d.metric("Routes", f"{filtered['route'].nunique():,}")

    st.divider()

    st.subheader("Dataset Information")

    info = pd.DataFrame({
        "Column": filtered.columns,
        "Data Type": [str(x) for x in filtered.dtypes],
        "Missing Values": filtered.isnull().sum().values
    })

    st.dataframe(info, use_container_width=True)

    st.subheader("Search Cargo Records")

    search = st.text_input(
        "Search by airline, origin or destination",
        placeholder="Enter airline or airport code..."
    )

    explorer = filtered.copy()

    if search:
        mask = (
            explorer["carrier_name"].str.contains(
                search, case=False, na=False
            ) |
            explorer["origin"].str.contains(
                search, case=False, na=False
            ) |
            explorer["dest"].str.contains(
                search, case=False, na=False
            )
        )
        explorer = explorer[mask]

    st.caption(f"{len(explorer):,} matching records")

    st.dataframe(
        explorer,
        use_container_width=True,
        height=450
    )

    st.download_button(
        "⬇️ Download Filtered Cargo CSV",
        data=explorer.to_csv(index=False).encode("utf-8"),
        file_name="filtered_cargo_data.csv",
        mime="text/csv"
    )

    st.divider()

    st.subheader("Upload Another Compatible Dataset")

    uploaded = st.file_uploader(
        "Upload an air cargo CSV",
        type=["csv"]
    )

    if uploaded is not None:
        try:
            new_data = pd.read_csv(uploaded)
            st.success("File uploaded successfully!")
            st.write("Rows:", len(new_data))
            st.write("Columns:", len(new_data.columns))
            st.dataframe(new_data.head(100), use_container_width=True)
        except Exception as e:
            st.error(f"File reading error: {e}")

# =====================================================
# FOOTER
# =====================================================
st.divider()

st.markdown("""
<center>
<p style="color:#94a3b8;">
GLOBAL SUPPLY CHAIN & LOGISTICS INTELLIGENCE<br>
Data Processing: Apache Spark / PySpark<br>
Dashboard: Python | Streamlit | Pandas | Plotly
</p>
</center>
""", unsafe_allow_html=True)
