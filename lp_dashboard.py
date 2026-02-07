import streamlit as st
import pandas as pd

# -----------------------------------
# Page configuration
# -----------------------------------
st.set_page_config(
    page_title="LP Performance Dashboard",
    layout="wide"
)

st.title("📊 Liquidity Provider Performance Dashboard")
st.caption("OneZero ARMS – Best / Worst LP Analysis")

# -----------------------------------
# File uploader
# -----------------------------------
uploaded_file = st.file_uploader(
    "Upload OneZero ARMS Report (CSV or Excel)",
    type=["csv", "xlsx"]
)

if uploaded_file is None:
    st.info("Please upload a OneZero ARMS execution statistics file to begin.")
    st.stop()

# -----------------------------------
# Read file
# -----------------------------------
try:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)
except Exception as e:
    st.error(f"Error reading file: {e}")
    st.stop()

st.success("File uploaded successfully")

# -----------------------------------
# Required columns validation
# -----------------------------------
required_columns = [
    "Core Symbol",
    "Maker Stream Name",
    "% Filled Volume",
    "Avg. Fill Latency",
    "Total Filled Volume"
]

missing_columns = [c for c in required_columns if c not in df.columns]

if missing_columns:
    st.error(f"Missing required columns: {missing_columns}")
    st.stop()

# -----------------------------------
# Data cleaning & numeric conversion
# -----------------------------------
df["Filled_Vol_Pct"] = (
    df["% Filled Volume"]
    .astype(str)
    .str.replace("%", "")
    .astype(float)
)

df["Avg_Latency_ms"] = (
    df["Avg. Fill Latency"]
    .astype(str)
    .str.replace("ms", "")
    .astype(float)
)

df["Total_Filled_Vol"] = (
    df["Total Filled Volume"]
    .astype(str)
    .str.replace("$", "", regex=False)
    .str.replace(",", "", regex=False)
    .astype(float)
)

# -----------------------------------
# Filters
# -----------------------------------
st.subheader("🔎 Filters")

col1, col2 = st.columns(2)

with col1:
    selected_symbol = st.selectbox(
        "Select Core Symbol",
        sorted(df["Core Symbol"].unique())
    )

with col2:
    selected_metric = st.selectbox(
        "Select Performance Metric",
        [
            "% Filled Volume",
            "Avg Fill Latency (ms)",
            "Total Filled Volume"
        ]
    )

sym_df = df[df["Core Symbol"] == selected_symbol]

# -----------------------------------
# Best / Worst calculation
# -----------------------------------
if selected_metric == "% Filled Volume":
    best_row = sym_df.loc[sym_df["Filled_Vol_Pct"].idxmax()]
    worst_row = sym_df.loc[sym_df["Filled_Vol_Pct"].idxmin()]
    metric_col = "Filled_Vol_Pct"
    higher_is_better = True

elif selected_metric == "Avg Fill Latency (ms)":
    best_row = sym_df.loc[sym_df["Avg_Latency_ms"].idxmin()]
    worst_row = sym_df.loc[sym_df["Avg_Latency_ms"].idxmax()]
    metric_col = "Avg_Latency_ms"
    higher_is_better = False

else:
    best_row = sym_df.loc[sym_df["Total_Filled_Vol"].idxmax()]
    worst_row = sym_df.loc[sym_df["Total_Filled_Vol"].idxmin()]
    metric_col = "Total_Filled_Vol"
    higher_is_better = True

# -----------------------------------
# KPI Cards
# -----------------------------------
st.subheader("🏆 Best vs Worst LP")

kpi1, kpi2 = st.columns(2)

kpi1.metric(
    label="Best LP",
    value=best_row["Maker Stream Name"],
    delta=f"{best_row[metric_col]:,.2f}"
)

kpi2.metric(
    label="Worst LP",
    value=worst_row["Maker Stream Name"],
    delta=f"{worst_row[metric_col]:,.2f}",
    delta_color="inverse"
)

# -----------------------------------
# Ranking table
# -----------------------------------
st.subheader("📋 LP Ranking Table")

rank_df = sym_df[
    [
        "Maker Stream Name",
        "Filled_Vol_Pct",
        "Avg_Latency_ms",
        "Total_Filled_Vol"
    ]
].rename(columns={
    "Maker Stream Name": "LP Name",
    "Filled_Vol_Pct": "% Filled Volume",
    "Avg_Latency_ms": "Avg Fill Latency (ms)",
    "Total_Filled_Vol": "Total Filled Volume"
})

rank_df = rank_df.sort_values(
    by=rank_df.columns[
        list(rank_df.columns).index(selected_metric)
    ] if selected_metric in rank_df.columns else metric_col,
    ascending=not higher_is_better
)

st.dataframe(rank_df, use_container_width=True)

# -----------------------------------
# Download output
# -----------------------------------
st.download_button(
    label="⬇️ Download LP Ranking (CSV)",
    data=rank_df.to_csv(index=False),
    file_name="LP_Performance_Ranking.csv",
    mime="text/csv"
)
