# Required libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64
from sklearn.linear_model import LinearRegression
import numpy as np
import plotly.graph_objects as go

# Page configuration
st.set_page_config(page_title="Stock Dashboard", layout="wide")

# Background Image
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def set_background(image_path):
    base64_img = get_base64(image_path)
    st.markdown(
        f"""
        <style>
        .stApp::before {{
            content: "";
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: url("data:image/png;base64,{base64_img}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            z-index: -1;
            filter: blur(8px);     /* this blurs the image only */
            opacity:0.7;
        }}
        .stApp {{
            background: transparent !important;  /* make sure the content sits on top */
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("wall3.png")

# Sidebar background
def sidebar_bg(image_file):
    with open(image_file, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()

    st.markdown(
        f"""
        <style>
        [data-testid="stSidebar"] > div:first-child {{
            position: relative;
            z-index: 0;
        }}
        [data-testid="stSidebar"] > div:first-child::before {{
            content: "";
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            filter: blur(8px);  /* ~25% blur */
            opacity: 0.9;
            z-index: -1;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

sidebar_bg("side bar3.jpg")

# Check if file exists
file_path = "5 days data set.csv"
if not os.path.exists(file_path):
    st.error("Data file not found. Please ensure '5 days data set.csv' is in the app directory.")
    st.stop()

# Load and prepare data
df = pd.read_csv(file_path)
df = df.drop(columns=['Symbol'], errors='ignore')
df.columns = df.columns.str.strip().str.replace(r"[^\w\s]", "", regex=True).str.replace(" ", "_")
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)

# Add main title at the top
st.title("Sri Lankan Stock Market Dashboard")

# KPI Summary
col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
with col_kpi1:
    st.metric("Total Records", f"{len(df):,}")
with col_kpi2:
    st.metric("Avg. % Change", f"{df['Change_'].mean():.2f}%")
with col_kpi3:
    st.metric("Highest Trade Volume", f"{df['Trade_Volume'].max():,}")

# Sidebar Filters
st.sidebar.header("Global Filters")
companies = sorted(df["Company_Name"].unique())
min_volume = int(df["Trade_Volume"].min())
max_volume = int(df["Trade_Volume"].max())
volume_range = st.sidebar.slider("Trade Volume Range", min_value=min_volume, max_value=max_volume, value=(min_volume, max_volume))

# Preset filters
st.sidebar.markdown("### Preset Filters")
preset_filter = st.sidebar.radio("Select a preset view", ["All", "Top Gainers", "High Volume"])
if preset_filter == "Top Gainers":
    companies = df.groupby("Company_Name")["Change_"].mean().sort_values(ascending=False).head(10).index.tolist()
elif preset_filter == "High Volume":
    companies = df.groupby("Company_Name")["Trade_Volume"].mean().sort_values(ascending=False).head(10).index.tolist()

# Tabs
tab1, tab2, tab3 = st.tabs(["Raw Data Viewer", "Data Visualizations", "Insights"])

with tab1:
    st.title("Raw Dataset Viewer")
    selected_companies = st.multiselect("Filter by Companies", companies, default=companies)
    selected_dates = st.date_input("Select Date Range", [df["Date"].min(), df["Date"].max()], key="raw_date_range")

    raw_filtered = df[(df["Company_Name"].isin(selected_companies)) &
                      (df["Date"] >= pd.to_datetime(selected_dates[0])) &
                      (df["Date"] <= pd.to_datetime(selected_dates[1])) &
                      (df["Trade_Volume"] >= volume_range[0]) &
                      (df["Trade_Volume"] <= volume_range[1])]

    st.dataframe(raw_filtered, use_container_width=True)
    csv = raw_filtered.to_csv(index=False).encode('utf-8')
    st.download_button("Download Filtered Data", csv, "filtered_data.csv", "text/csv")

    st.markdown("### Summary Statistics")
    st.dataframe(raw_filtered.describe(include='all'), use_container_width=True)

    st.markdown("---")
    st.markdown("Dashboard built for 5DATA004C.2 Data Science Project Lifecycle (IIT Sri Lanka)")

with tab2:
    selected_company = st.selectbox("Select a Company", companies)
    date_range = st.date_input("Select Date Range", [df["Date"].min(), df["Date"].max()], key="viz_date_range")
    price_metric = st.selectbox("Price Metric to Highlight", ["Open_Rs", "High_Rs", "Low_Rs", "Last_Trade_Rs"])

    filtered_df = df[(df["Company_Name"] == selected_company) &
                     (df["Date"] >= pd.to_datetime(date_range[0])) &
                     (df["Date"] <= pd.to_datetime(date_range[1])) &
                     (df["Trade_Volume"] >= volume_range[0]) &
                     (df["Trade_Volume"] <= volume_range[1])]

    st.markdown(f"### Overview for {selected_company}")

    fig1 = px.line(filtered_df, x="Date", y=["Open_Rs", "High_Rs", "Low_Rs", "Last_Trade_Rs"],
                   title="Stock Prices Over Time", labels={"value": "Price (Rs.)", "variable": "Metric"})
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.line(filtered_df, x="Date", y="Change_", title="Daily % Change Over Time")
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.bar(filtered_df, x="Date", y=["Share_Volume", "Trade_Volume"],
                  title="Share vs Trade Volume", barmode="group")
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("### Candlestick Chart")
    fig_candle = go.Figure(data=[go.Candlestick(
        x=filtered_df['Date'],
        open=filtered_df['Open_Rs'],
        high=filtered_df['High_Rs'],
        low=filtered_df['Low_Rs'],
        close=filtered_df['Last_Trade_Rs']
    )])
    fig_candle.update_layout(title='Candlestick Chart', xaxis_title='Date', yaxis_title='Price (Rs.)')
    st.plotly_chart(fig_candle, use_container_width=True)

    st.markdown("### Rolling Average")
    rolling_df = filtered_df.copy()
    rolling_df["Rolling_Avg"] = rolling_df[price_metric].rolling(window=3).mean()
    fig_roll = px.line(rolling_df, x="Date", y=["Rolling_Avg", price_metric],
                      title=f"Rolling Avg vs {price_metric}", labels={"value": "Price", "variable": "Type"})
    st.plotly_chart(fig_roll, use_container_width=True)

    st.markdown("### Price Feature Correlation Heatmap")
    corr = filtered_df[["Open_Rs", "High_Rs", "Low_Rs", "Last_Trade_Rs", "Change_", "Trade_Volume"]].corr()
    fig_corr = px.imshow(corr, text_auto=True, title="Correlation Matrix")
    st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("### Forecast Next Day's Last Trade Price (Linear Regression)")
    forecast_all = st.checkbox("Run forecast for all companies", key="forecast_all_checkbox")
    if forecast_all:
        predictions = []
    for company in df["Company_Name"].unique():
        company_df = df[df["Company_Name"] == company].copy()
        if len(company_df) >= 2:
            company_df = company_df.sort_values("Date")
            company_df["Day_Num"] = (company_df["Date"] - company_df["Date"].min()).dt.days
            X = company_df[["Day_Num"]]
            y = company_df["Last_Trade_Rs"]
            model = LinearRegression().fit(X, y)
            next_day = company_df["Day_Num"].max() + 1
            pred_price = model.predict([[next_day]])[0]
            forecast_date = company_df["Date"].max() + pd.Timedelta(days=1)
            predictions.append({
                "Company": company,
                "Forecast_Date": forecast_date.strftime("%Y-%m-%d"),
                "Predicted_Last_Trade_Rs": round(pred_price, 2)
            })

    pred_df = pd.DataFrame(predictions).sort_values("Predicted_Last_Trade_Rs", ascending=False)
    st.dataframe(pred_df, use_container_width=True)

    # Download button
    forecast_csv = pred_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download Forecast Data", forecast_csv, file_name="forecast_next_day.csv", mime="text/csv")

    st.markdown("---")
    st.markdown("Dashboard built for 5DATA004C.2 Data Science Project Lifecycle (IIT Sri Lanka)")

with tab3:
    st.markdown("### Company Leaderboard")
    leaderboard_option = st.selectbox("Rank by", ["Average % Gain", "Average Trade Volume"])
    if leaderboard_option == "Average % Gain":
        leader_df = df.groupby("Company_Name")["Change_"].mean().sort_values(ascending=False).head(10)
    else:
        leader_df = df.groupby("Company_Name")["Trade_Volume"].mean().sort_values(ascending=False).head(10)
    fig_leader = px.bar(leader_df, x=leader_df.index, y=leader_df.values,
                        labels={"x": "Company", "y": leaderboard_option}, title=f"Top 10 Companies by {leaderboard_option}")
    st.plotly_chart(fig_leader, use_container_width=True)

    st.markdown("### Volatility Indicator")
    volatility = df.groupby("Company_Name")["Change_"].std().sort_values(ascending=False).head(5)
    fig_vol = px.bar(volatility, x=volatility.index, y=volatility.values,
                     title="Top 5 Most Volatile Companies", labels={"x": "Company", "y": "Std Dev of % Change"})
    st.plotly_chart(fig_vol, use_container_width=True)

    st.markdown("### Heatmap of Daily % Changes")
    heatmap_data = df.pivot_table(index="Company_Name", columns="Date", values="Change_")
    fig_heatmap = px.imshow(heatmap_data,
                            labels=dict(x="Date", y="Company", color="% Change"),
                            title="Heatmap of Daily % Changes",
                            aspect="auto")
    st.plotly_chart(fig_heatmap, use_container_width=True)

    st.markdown("### Trade Volume Trend for Top 5 Companies")
    top5 = df.groupby("Company_Name")["Trade_Volume"].mean().sort_values(ascending=False).head(5).index
    top5_df = df[df["Company_Name"].isin(top5)]
    fig_top5_vol = px.line(top5_df, x="Date", y="Trade_Volume", color="Company_Name")
    st.plotly_chart(fig_top5_vol, use_container_width=True)

    st.markdown("### Total Trade Volume by Company")
    total_volume = df.groupby("Company_Name")["Trade_Volume"].sum().reset_index()
    fig_tree = px.treemap(total_volume, path=["Company_Name"], values="Trade_Volume", title="Company Volume Treemap")
    st.plotly_chart(fig_tree, use_container_width=True)

    st.markdown("### Distribution of Daily % Change")
    fig_box = px.box(df, x="Company_Name", y="Change_", points="all", title="Volatility Distribution by Company")
    st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")
    st.markdown("Dashboard built for 5DATA004C.2 Data Science Project Lifecycle (IIT Sri Lanka)")
