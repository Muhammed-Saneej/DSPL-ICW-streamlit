# Required libraries
import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Check if file exists
file_path = "5 days data set.csv"

# Load and prepare data
df = pd.read_csv(file_path)
df.columns = df.columns.str.strip().str.replace(r"[^\w\s]", "", regex=True).str.replace(" ", "_")
df["Date"] = pd.to_datetime(df["Date"], dayfirst=True)

# Sidebar filters
st.sidebar.title("Filter Options")
companies = sorted(df["Company_Name"].unique())
selected_company = st.sidebar.selectbox("Select a Company", companies)
date_range = st.sidebar.date_input("Select Date Range", [df["Date"].min(), df["Date"].max()])

# New filters
min_volume = int(df["Trade_Volume"].min())
max_volume = int(df["Trade_Volume"].max())
volume_range = st.sidebar.slider("Trade Volume Range", min_value=min_volume, max_value=max_volume, value=(min_volume, max_volume))

price_metric = st.sidebar.selectbox("Price Metric to Highlight", ["Open_Rs", "High_Rs", "Low_Rs", "Last_Trade_Rs"])

# Apply filters
filtered_df = df[(df["Company_Name"] == selected_company) &
                 (df["Date"] >= pd.to_datetime(date_range[0])) &
                 (df["Date"] <= pd.to_datetime(date_range[1])) &
                 (df["Trade_Volume"] >= volume_range[0]) &
                 (df["Trade_Volume"] <= volume_range[1])]

st.title("Sri Lankan Stock Market Dashboard")
st.markdown(f"### Overview for {selected_company}")

# 1. Price Trends
fig1 = px.line(filtered_df, x="Date", y=["Open_Rs", "High_Rs", "Low_Rs", "Last_Trade_Rs"],
               title="Stock Prices Over Time", labels={"value": "Price (Rs.)", "variable": "Metric"})
st.plotly_chart(fig1)

# 2. Daily Change %
fig2 = px.line(filtered_df, x="Date", y="Change_", title="Daily % Change Over Time")
st.plotly_chart(fig2)

# 3. Volume Comparison
fig3 = px.bar(filtered_df, x="Date", y=["Share_Volume", "Trade_Volume"],
              title="Share vs Trade Volume", barmode="group")
st.plotly_chart(fig3)

# 4. Top Companies by Avg Trade Volume
avg_volume = df.groupby("Company_Name")["Trade_Volume"].mean().sort_values(ascending=False).head(10)
fig4 = px.bar(avg_volume, x=avg_volume.index, y=avg_volume.values,
              title="Top 10 Companies by Avg. Trade Volume", labels={"x": "Company", "y": "Avg Trade Volume"})
st.plotly_chart(fig4)

# 5. Gainers and Losers
selected_day = st.sidebar.date_input("Pick a Day for Gainers/Losers", df["Date"].max())
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
st.plotly_chart(fig6)

# 7. Box Plot - Price Distribution
top_companies = df["Company_Name"].value_counts().head(10).index
box_df = df[df["Company_Name"].isin(top_companies)]
fig7 = px.box(box_df, x="Company_Name", y="Last_Trade_Rs", title="Price Distribution - Top Companies")
st.plotly_chart(fig7)

# 8. Highlighted Metric Chart
fig8 = px.line(filtered_df, x="Date", y=price_metric,
               title=f"Selected Price Metric: {price_metric.replace('_', ' ')}")
st.plotly_chart(fig8)

st.markdown("---")
st.markdown("Dashboard built for 5DATA004W - University of Westminster")
