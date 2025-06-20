import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import joblib

st.set_page_config(page_title="CLV Dashboard", layout="wide")

# Load model & data
model = joblib.load("CLV_model.pkl")
rfm = pd.read_csv("predicted_clv.csv")

st.title("📊 Customer Lifetime Value Dashboard")

# Sidebar Filters
with st.sidebar:
    st.header("🔍 Filter")
    segment_filter = st.multiselect("Select Segment", options=rfm["Segment"].unique(), default=rfm["Segment"].unique())

filtered = rfm[rfm["Segment"].isin(segment_filter)]

# Top Summary Metrics
col1, col2, col3 = st.columns(3)
col1.metric("🧑‍🤝‍🧑 Total Customers", len(filtered))
col2.metric("💰 Avg Predicted CLV", round(filtered["Predicted_CLV"].mean(), 2))
col3.metric("📈 Max Predicted CLV", round(filtered["Predicted_CLV"].max(), 2))

# ⬇️ Layout Starts Here

st.subheader("📈 Feature Distributions")
row1_col1, row1_col2, row1_col3,row1_col4 = st.columns(4)
row2_col1, row2_col2, row2_col3, row2_col4 = st.columns(4)
row3_col1 = st.columns(1)[0]
# Histogram 1: Recency
with row1_col1:
    fig1, ax1 = plt.subplots()
    sns.histplot(filtered["Recency"], bins=30, kde=True, ax=ax1)
    ax1.set_title("Distribution: Recency")
    st.pyplot(fig1)

# Histogram 2: Frequency
with row1_col2:
    fig2, ax2 = plt.subplots()
    sns.histplot(filtered["Frequency"], bins=30, kde=True, ax=ax2)
    ax2.set_title("Distribution: Frequency")
    st.pyplot(fig2)

# Histogram 3: AOV
with row2_col1:
    fig3, ax3 = plt.subplots()
    sns.histplot(filtered["AOV"], bins=30, kde=True, ax=ax3)
    ax3.set_title("Distribution: AOV")
    st.pyplot(fig3)

# Histogram 4: Predicted CLV
with row2_col2:
    fig4, ax4 = plt.subplots()
    sns.histplot(filtered["Predicted_CLV"], bins=30, kde=True, ax=ax4)
    ax4.set_title("Distribution: Predicted CLV")
    st.pyplot(fig4)
# Segment Bar Chart in Full Width
with row1_col3:
    fig5, ax5 = plt.subplots()
    sns.countplot(data=filtered, x="Segment", order=sorted(rfm["Segment"].unique()), palette="Set2", ax=ax5)
    ax5.set_title("Customers by Segment")
    st.pyplot(fig5)

with row2_col3:
    fig_corr, ax_corr = plt.subplots(figsize=(10, 4))
    sns.heatmap(filtered[['Recency', 'Frequency', 'AOV', 'Predicted_CLV']].corr(), annot=True, cmap='coolwarm', ax=ax_corr)
    ax_corr.set_title("Correlation Matrix")
    st.pyplot(fig_corr)

with row1_col4:
    fig_scatter, ax_scatter = plt.subplots(figsize=(8, 4))
    sns.scatterplot(data=filtered, x='Frequency', y='AOV', size='Predicted_CLV', hue='Segment', palette='Set2', ax=ax_scatter, sizes=(40, 400), alpha=0.7)
    ax_scatter.set_title("Customer Value Segmentation")
    st.pyplot(fig_scatter)
 
with row2_col4:
    bins = [0, 500, 1000, 2000, 5000, 10000]
    labels = ['<500', '500-1k', '1k-2k', '2k-5k', '5k+']
    filtered['CLV_Tier'] = pd.cut(filtered['Predicted_CLV'], bins=bins, labels=labels)

    fig_tier, ax_tier = plt.subplots()
    sns.countplot(data=filtered, x='CLV_Tier', palette='Set1', ax=ax_tier)
    ax_tier.set_title("Customers by Predicted CLV Tier")
    st.pyplot(fig_tier)

with row3_col1:
    st.subheader("📈 CLV Over Time by Segment")

    clv_seg_month = (
        filtered[['Recency', 'Predicted_CLV', 'Segment']]
        .copy()
        .dropna()
    )
    clv_seg_month['Recency'] = pd.to_datetime(clv_seg_month['Recency'])
    clv_seg_month = clv_seg_month.groupby(
        [pd.Grouper(key='Recency', freq='M'), 'Segment']
    ).mean().reset_index()

    fig_time_seg, ax_time_seg = plt.subplots(figsize=(10, 5))
    sns.lineplot(data=clv_seg_month, x='Recency', y='Predicted_CLV', hue='Segment', marker='o', ax=ax_time_seg)
    ax_time_seg.set_title("Segment-wise CLV Trend Over Time")
    ax_time_seg.tick_params(axis='x', rotation=45)
    st.pyplot(fig_time_seg)



# ✅ NEW ROW: Filtered Data Table
st.subheader("📄 Filtered Customer Data")
with st.expander("Click to View Table"):
    st.dataframe(filtered.reset_index(drop=True))