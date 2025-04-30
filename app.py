# Required libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

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
        .stApp {{
            background-image: url("data:image/png;base64,{base64_img}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("wall.png")


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

# Common Sidebar Filters
st.sidebar.header("Global Filters")
companies = sorted(df["Company_Name"].unique())
min_volume = int(df["Trade_Volume"].min())
max_volume = int(df["Trade_Volume"].max())
volume_range = st.sidebar.slider("Trade Volume Range", min_value=min_volume, max_value=max_volume, value=(min_volume, max_volume))

# Create tabs
tab1, tab2 = st.tabs(["Raw Data Viewer", "Data Visualizations"])

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

with tab2:
    st.title("Sri Lankan Stock Market Dashboard")
    selected_company = st.selectbox("Select a Company", companies)
    date_range = st.date_input("Select Date Range", [df["Date"].min(), df["Date"].max()], key="viz_date_range")
    price_metric = st.selectbox("Price Metric to Highlight", ["Open_Rs", "High_Rs", "Low_Rs", "Last_Trade_Rs"])

    filtered_df = df[(df["Company_Name"] == selected_company) &
                     (df["Date"] >= pd.to_datetime(date_range[0])) &
                     (df["Date"] <= pd.to_datetime(date_range[1])) &
                     (df["Trade_Volume"] >= volume_range[0]) &
                     (df["Trade_Volume"] <= volume_range[1])]

    st.markdown(f"### Overview for {selected_company}")
    
    # 1. Price Trends
    fig1 = px.line(filtered_df, x="Date", y=["Open_Rs", "High_Rs", "Low_Rs", "Last_Trade_Rs"],
                   title="Stock Prices Over Time", labels={"value": "Price (Rs.)", "variable": "Metric"})
    st.plotly_chart(fig1, use_container_width=True)

    # 2. Daily Change %
    fig2 = px.line(filtered_df, x="Date", y="Change_", title="Daily % Change Over Time")
    st.plotly_chart(fig2, use_container_width=True)

    # 3. Volume Comparison
    fig3 = px.bar(filtered_df, x="Date", y=["Share_Volume", "Trade_Volume"],
                  title="Share vs Trade Volume", barmode="group")
    st.plotly_chart(fig3, use_container_width=True)

    # 4. Top Companies by Avg Trade Volume
    avg_volume = df.groupby("Company_Name")["Trade_Volume"].mean().sort_values(ascending=False).head(10)
    fig4 = px.bar(avg_volume, x=avg_volume.index, y=avg_volume.values,
                  title="Top 10 Companies by Avg. Trade Volume", labels={"x": "Company", "y": "Avg Trade Volume"})
    st.plotly_chart(fig4, use_container_width=True)

    # 5. Gainers and Losers
    selected_day = st.date_input("Pick a Day for Gainers/Losers", df["Date"].max())
    daily_df = df[df["Date"] == pd.to_datetime(selected_day)]
    top_gainers = daily_df.sort_values("Change_", ascending=False).head(5)
    top_losers = daily_df.sort_values("Change_", ascending=True).head(5)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Top 5 Gainers")
        st.dataframe(top_gainers[["Company_Name", "Change_"]])
    with col2:
        st.markdown("### Top 5 Losers")
        st.dataframe(top_losers[["Company_Name", "Change_"]])

    # 6. Volume vs Change Scatter
    fig6 = px.scatter(df, x="Trade_Volume", y="Change_", color="Company_Name",
                      title="Volume vs Price Change", hover_data=["Date"])
    st.plotly_chart(fig6, use_container_width=True)

    # 7. Box Plot - Price Distribution
    top_companies = df["Company_Name"].value_counts().head(10).index
    box_df = df[df["Company_Name"].isin(top_companies)]
    fig7 = px.box(box_df, x="Company_Name", y="Last_Trade_Rs", title="Price Distribution - Top Companies")
    st.plotly_chart(fig7, use_container_width=True)

    # 8. Highlighted Metric Chart
    fig8 = px.line(filtered_df, x="Date", y=price_metric,
                   title=f"Selected Price Metric: {price_metric.replace('_', ' ')}")
    st.plotly_chart(fig8, use_container_width=True)

    # 9. Animated Chart - Trade Volume by Company Over Time (Filtered)
    st.markdown("### Animated Trade Volume Over Time")
    animation_companies = st.multiselect("Select Companies for Animation", companies, default=companies[:5])
    animation_df = df[df["Company_Name"].isin(animation_companies)].copy()
    animation_df = animation_df[(animation_df["Trade_Volume"] >= volume_range[0]) & (animation_df["Trade_Volume"] <= volume_range[1])]
    animation_df["Date_str"] = animation_df["Date"].dt.strftime("%Y-%m-%d")
    fig9 = px.bar(
        animation_df,
        x="Company_Name",
        y="Trade_Volume",
        color="Company_Name",
        animation_frame="Date_str",
        range_y=[0, df["Trade_Volume"].max()],
        title="Trade Volume by Company Over Time"
    )
    fig9.update_layout(
        updatemenus=[{
            "type": "buttons",
            "buttons": [
                {
                    "label": "Play",
                    "method": "animate",
                    "args": [None, {"frame": {"duration": 1000, "redraw": True}, "fromcurrent": True}]
                },
                {
                    "label": "Pause",
                    "method": "animate",
                    "args": [[None], {"frame": {"duration": 0}, "mode": "immediate"}]
                }
            ]
        }]
    )
    st.plotly_chart(fig9, use_container_width=True)

    st.markdown("---")
    st.markdown("Dashboard built for 5DATA004W Data Science Project Lifecycle (IIT Sri Lanka)")
