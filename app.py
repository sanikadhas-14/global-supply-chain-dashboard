
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Global Logistics Intelligence",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -------------------- DESIGN --------------------

st.markdown("""
<style>
.stApp {
    background: #091323;
    color: #f8fafc;
}
[data-testid="stHeader"] {
    background: #091323;
}
[data-testid="stSidebar"] {
    background: #12233a;
    border-right: 1px solid #294563;
}
[data-testid="stSidebar"] * {
    color: #f1f5f9 !important;
}
h1,h2,h3,h4,p,label {
    color: #f1f5f9 !important;
}
[data-testid="stMetric"] {
    background: linear-gradient(135deg,#183653,#174d67);
    border: 1px solid #34718f;
    border-radius: 15px;
    padding: 18px;
    min-height: 115px;
}
[data-testid="stMetricLabel"] {
    color: #cbd5e1 !important;
}
[data-testid="stMetricValue"] {
    color: #67e8f9 !important;
}
[data-testid="stMetricDelta"] {
    color: #86efac !important;
}
[data-testid="stPlotlyChart"] {
    background: #12233a;
    border: 1px solid #294563;
    border-radius: 14px;
    padding: 8px;
}
div[data-testid="stDataFrame"] {
    border: 1px solid #294563;
    border-radius: 12px;
}
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}
</style>
""", unsafe_allow_html=True)

# -------------------- DATA LOADING --------------------

REQUIRED = [
    "cargo_year", "cargo_month", "carrier_name",
    "origin", "dest", "freight_pounds", "passengers"
]

@st.cache_data
def read_default():
    return pd.read_csv("cargo_data.csv")

def prepare_data(data):
    data = data.copy()

    missing = [c for c in REQUIRED if c not in data.columns]
    if missing:
        raise ValueError("Missing columns: " + ", ".join(missing))

    for c in ["cargo_year", "cargo_month",
              "freight_pounds", "passengers"]:
        data[c] = pd.to_numeric(data[c], errors="coerce")

    data = data.dropna(subset=["cargo_year", "cargo_month"])

    for c in ["carrier_name", "origin", "dest"]:
        data[c] = data[c].fillna("Unknown").astype(str)

    data["freight_pounds"] = data["freight_pounds"].fillna(0)
    data["passengers"] = data["passengers"].fillna(0)

    data = data[
        data["cargo_month"].between(1, 12) &
        (data["freight_pounds"] >= 0) &
        (data["passengers"] >= 0)
    ].drop_duplicates()

    data["cargo_year"] = data["cargo_year"].astype(int)
    data["cargo_month"] = data["cargo_month"].astype(int)
    data["route"] = data["origin"] + " → " + data["dest"]
    data["period"] = (
        data["cargo_year"].astype(str) + "-" +
        data["cargo_month"].astype(str).str.zfill(2)
    )

    return data

# -------------------- SIDEBAR --------------------

st.sidebar.markdown("# ✈️ LOGISTICS IQ")
st.sidebar.caption("AIR CARGO INTELLIGENCE PLATFORM")
st.sidebar.divider()

uploaded = st.sidebar.file_uploader(
    "📂 Upload Air Cargo Dataset",
    type=["csv"],
    help="Upload another CSV containing the required air-cargo columns."
)

try:
    if uploaded is not None:
        source_df = pd.read_csv(uploaded)
        df = prepare_data(source_df)
        st.sidebar.success("Uploaded dataset is active")
    else:
        df = prepare_data(read_default())
        st.sidebar.success("Default dataset loaded")
except Exception as e:
    st.error(f"Dataset could not be loaded: {e}")
    st.info("Check that cargo_data.csv exists and contains the required air-cargo columns.")
    st.stop()

st.sidebar.divider()
st.sidebar.subheader("🎛️ Dashboard Filters")

years = sorted(df["cargo_year"].unique())
selected_years = st.sidebar.multiselect(
    "Select Year",
    years,
    default=years
)

month_labels = {
    m: pd.to_datetime(str(m), format="%m").strftime("%B")
    for m in sorted(df["cargo_month"].unique())
}

month_choice = st.sidebar.selectbox(
    "Select Month",
    ["All Months"] + list(month_labels.values())
)

airline_list = sorted(df["carrier_name"].unique())
selected_airlines = st.sidebar.multiselect(
    "Select Airlines",
    airline_list,
    default=[]
)

filtered = df[df["cargo_year"].isin(selected_years)].copy()

if month_choice != "All Months":
    selected_month_number = [
        m for m, label in month_labels.items()
        if label == month_choice
    ][0]
    filtered = filtered[
        filtered["cargo_month"] == selected_month_number
    ]

if selected_airlines:
    filtered = filtered[
        filtered["carrier_name"].isin(selected_airlines)
    ]

if filtered.empty:
    st.warning("No records match these filters. Please change your selection.")
    st.stop()

# -------------------- COMMON FUNCTIONS --------------------

def chart_style(fig, height=400):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="#12233a",
        plot_bgcolor="#12233a",
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

def get_top_airlines(data, n=10):
    return (
        data.groupby("carrier_name", as_index=False)
        ["freight_pounds"].sum()
        .nlargest(n, "freight_pounds")
    )

def get_top_routes(data, n=10):
    return (
        data.groupby("route", as_index=False)
        ["freight_pounds"].sum()
        .nlargest(n, "freight_pounds")
    )

# -------------------- HEADER --------------------

st.title("✈️ GLOBAL SUPPLY CHAIN")
st.subheader("Logistics Intelligence Dashboard")
st.caption(
    "AIR CARGO ANALYTICS  •  FREIGHT MOVEMENT  •  "
    "AIRLINE PERFORMANCE  •  ROUTE INTELLIGENCE"
)

st.divider()

# -------------------- NAVIGATION --------------------

page = st.sidebar.radio(
    "📌 NAVIGATION",
    [
        "Executive Overview",
        "Cargo Intelligence",
        "Airline Performance",
        "Route Intelligence",
        "Time & Trends",
        "Business Insights",
        "Data Explorer"
    ]
)

# -------------------- EXECUTIVE OVERVIEW --------------------

if page == "Executive Overview":

    st.header("📊 Executive Command Center")
    st.write("A complete overview of air cargo operations.")

    show_kpis(filtered)

    a, b, c = st.columns(3)
    a.metric("Unique Routes", f"{filtered['route'].nunique():,}")
    b.metric("Origin Airports", f"{filtered['origin'].nunique():,}")
    c.metric("Destination Airports", f"{filtered['dest'].nunique():,}")

    st.divider()

    monthly = (
        filtered.groupby("period", as_index=False)
        ["freight_pounds"].sum().sort_values("period")
    )

    fig = px.area(
        monthly,
        x="period",
        y="freight_pounds",
        markers=True,
        title="Freight Movement Over Time"
    )
    st.plotly_chart(chart_style(fig, 420), use_container_width=True)

    left, right = st.columns(2)

    airlines = get_top_airlines(filtered, 10)
    fig = px.bar(
        airlines,
        x="freight_pounds",
        y="carrier_name",
        orientation="h",
        title="Top 10 Airlines by Freight"
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    left.plotly_chart(chart_style(fig), use_container_width=True)

    routes = get_top_routes(filtered, 10)
    fig = px.bar(
        routes,
        x="freight_pounds",
        y="route",
        orientation="h",
        title="Top 10 Cargo Routes"
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    right.plotly_chart(chart_style(fig), use_container_width=True)

    st.subheader("⭐ Quick Business Summary")

    best_airline = airlines.iloc[0]["carrier_name"]
    best_route = routes.iloc[0]["route"]

    st.markdown(f"""
    <div style="background:#164e63;padding:22px;border-radius:14px;
    border:1px solid #38bdf8;margin-bottom:14px;">
    <h4 style="color:#bae6fd;">🏆 Leading Airline by Freight</h4>
    <h2 style="color:#ffffff;">{best_airline}</h2>
    </div>
    <div style="background:#1e3a5f;padding:22px;border-radius:14px;
    border:1px solid #60a5fa;">
    <h4 style="color:#bfdbfe;">✈️ Highest Freight Route</h4>
    <h2 style="color:#ffffff;">{best_route}</h2>
    </div>
    """, unsafe_allow_html=True)

# -------------------- CARGO INTELLIGENCE --------------------

elif page == "Cargo Intelligence":

    st.header("📦 Cargo Intelligence")
    st.write("Analyze freight volume, distribution and passenger activity.")

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
        title="Monthly Freight by Year"
    )
    left.plotly_chart(chart_style(fig), use_container_width=True)

    airline_share = get_top_airlines(filtered, 10)
    fig = px.pie(
        airline_share,
        names="carrier_name",
        values="freight_pounds",
        hole=0.5,
        title="Freight Share of Top Airlines"
    )
    right.plotly_chart(chart_style(fig), use_container_width=True)

    st.subheader("Freight Distribution")
    fig = px.histogram(
        filtered,
        x="freight_pounds",
        nbins=35,
        title="Distribution of Freight Records"
    )
    st.plotly_chart(chart_style(fig), use_container_width=True)

    st.subheader("Passenger vs Freight Relationship")
    sample = filtered.sample(
        min(3000, len(filtered)),
        random_state=42
    )
    fig = px.scatter(
        sample,
        x="passengers",
        y="freight_pounds",
        color="cargo_year",
        hover_data=["carrier_name", "origin", "dest"]
    )
    st.plotly_chart(chart_style(fig), use_container_width=True)

# -------------------- AIRLINE PERFORMANCE --------------------

elif page == "Airline Performance":

    st.header("✈️ Airline Performance")
    st.write("Compare airline freight and passenger contributions.")

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
    st.plotly_chart(chart_style(fig, 520), use_container_width=True)

    left, right = st.columns(2)

    fig = px.pie(
        airline.head(10),
        names="carrier_name",
        values="passengers",
        hole=0.45,
        title="Passenger Share"
    )
    left.plotly_chart(chart_style(fig), use_container_width=True)

    fig = px.scatter(
        airline,
        x="passengers",
        y="freight",
        size="records",
        hover_name="carrier_name",
        title="Airline Freight vs Passenger Performance"
    )
    right.plotly_chart(chart_style(fig), use_container_width=True)

    st.subheader("Airline Ranking")
    st.dataframe(airline, use_container_width=True)

# -------------------- ROUTE INTELLIGENCE --------------------

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
        title="Top 20 Cargo Routes"
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(chart_style(fig, 600), use_container_width=True)

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
        title="Top Origin Airports"
    )
    left.plotly_chart(chart_style(fig), use_container_width=True)

    destination = (
        filtered.groupby("dest", as_index=False)
        ["freight_pounds"].sum()
        .nlargest(10, "freight_pounds")
    )
    fig = px.bar(
        destination,
        x="dest",
        y="freight_pounds",
        title="Top Destination Airports"
    )
    right.plotly_chart(chart_style(fig), use_container_width=True)

    st.subheader("Route Details")
    st.dataframe(routes, use_container_width=True)

# -------------------- TIME & TRENDS --------------------

elif page == "Time & Trends":

    st.header("📈 Time & Trend Analysis")
    st.write("Discover yearly patterns and monthly seasonality.")

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
    left.plotly_chart(chart_style(fig), use_container_width=True)

    fig = px.bar(
        yearly,
        x="cargo_year",
        y="passengers",
        title="Yearly Passenger Movement"
    )
    right.plotly_chart(chart_style(fig), use_container_width=True)

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

    order = [
        "Jan", "Feb", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
    ]
    heat = heat.reindex(columns=order)

    fig = px.imshow(
        heat,
        aspect="auto",
        color_continuous_scale="Blues",
        title="Monthly Freight Seasonality Heatmap",
        labels={"x": "Month", "y": "Year", "color": "Freight"}
    )
    st.plotly_chart(chart_style(fig, 420), use_container_width=True)

    st.subheader("Yearly Summary")
    st.dataframe(yearly, use_container_width=True)

# -------------------- BUSINESS INSIGHTS --------------------

elif page == "Business Insights":

    st.header("💡 Business Intelligence Center")
    st.write("Automatic business findings from the selected dataset.")

    show_kpis(filtered)
    st.divider()

    airline = filtered.groupby("carrier_name")["freight_pounds"].sum().sort_values(ascending=False)
    routes = filtered.groupby("route")["freight_pounds"].sum().sort_values(ascending=False)
    origins = filtered.groupby("origin")["freight_pounds"].sum().sort_values(ascending=False)
    destinations = filtered.groupby("dest")["freight_pounds"].sum().sort_values(ascending=False)
    monthly = filtered.groupby("cargo_month")["freight_pounds"].sum().sort_values(ascending=False)

    a, b = st.columns(2)

    with a:
        st.subheader("🏆 Leading Airline")
        st.metric("Airline", str(airline.index[0]))
        st.metric("Freight Handled", f"{airline.iloc[0]:,.0f} lbs")

        st.subheader("🛫 Leading Origin")
        st.metric("Origin", str(origins.index[0]))

    with b:
        st.subheader("🔀 Busiest Route")
        st.metric("Route", str(routes.index[0]))
        st.metric("Route Freight", f"{routes.iloc[0]:,.0f} lbs")

        st.subheader("📍 Leading Destination")
        st.metric("Destination", str(destinations.index[0]))

    month_name = pd.to_datetime(
        int(monthly.index[0]), format="%m"
    ).strftime("%B")

    st.metric("📅 Highest Freight Month", month_name)

    st.divider()
    st.subheader("🚨 Cargo Anomaly Detection")

    q1 = filtered["freight_pounds"].quantile(0.25)
    q3 = filtered["freight_pounds"].quantile(0.75)
    iqr = q3 - q1
    upper = q3 + 1.5 * iqr
    lower = max(0, q1 - 1.5 * iqr)

    anomalies = filtered[
        (filtered["freight_pounds"] > upper) |
        (filtered["freight_pounds"] < lower)
    ]

    a, b = st.columns(2)
    a.metric("Unusual Records", f"{len(anomalies):,}")
    b.metric(
        "Unusual Record Share",
        f"{len(anomalies) / len(filtered) * 100:.2f}%"
    )

    st.caption("Anomaly screening uses the statistical IQR method; it is not a trained ML model.")

    st.dataframe(
        anomalies[
            ["cargo_year", "cargo_month", "carrier_name",
             "origin", "dest", "freight_pounds"]
        ].head(100),
        use_container_width=True
    )

    st.subheader("Business Recommendations")
    st.markdown("""
    - Monitor high-volume routes for capacity planning.
    - Compare airline freight contribution.
    - Study seasonal freight patterns.
    - Identify important origin and destination airports.
    - Investigate unusually high freight records.
    """)

# -------------------- DATA EXPLORER --------------------

elif page == "Data Explorer":

    st.header("🗂️ Data Explorer")
    st.write("Search, inspect and download cargo records.")

    show_kpis(filtered)
    st.divider()

    info = pd.DataFrame({
        "Column": filtered.columns,
        "Data Type": [str(x) for x in filtered.dtypes],
        "Missing Values": filtered.isnull().sum().values
    })

    st.subheader("Dataset Structure")
    st.dataframe(info, use_container_width=True)

    st.subheader("Search Cargo Records")

    search = st.text_input(
        "Search airline, origin or destination",
        placeholder="Type an airline or airport code..."
    )

    explorer = filtered.copy()

    if search:
        mask = (
            explorer["carrier_name"].str.contains(search, case=False, na=False) |
            explorer["origin"].str.contains(search, case=False, na=False) |
            explorer["dest"].str.contains(search, case=False, na=False)
        )
        explorer = explorer[mask]

    st.caption(f"{len(explorer):,} matching records")
    st.dataframe(explorer, use_container_width=True, height=450)

    st.download_button(
        "⬇️ Download Filtered CSV",
        data=explorer.to_csv(index=False).encode("utf-8"),
        file_name="filtered_cargo_data.csv",
        mime="text/csv"
    )

# -------------------- FOOTER --------------------

st.divider()
st.markdown("""
<div style="text-align:center;padding:15px;color:#94a3b8;">
GLOBAL SUPPLY CHAIN & LOGISTICS INTELLIGENCE<br>
Data Processing: Apache Spark / PySpark<br>
Dashboard: Python • Streamlit • Pandas • Plotly
</div>
""", unsafe_allow_html=True)
