import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import os

st.set_page_config(page_title="Medication Adherence — Insights", layout="wide")
st.title("Medication Adherence — Insights Dashboard")

data_path = "data/app_usage_with_clusters.csv"
if not os.path.exists(data_path):
    st.warning("Clustered data not found. Please run: `python src/analysis.py` first.")
    st.stop()

df = pd.read_csv(data_path)

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    personas = st.multiselect("Persona", sorted(df["Persona"].unique().tolist()), default=None)
    clusters = st.multiselect("Cluster Label", sorted(df["Cluster_Label"].unique().tolist()), default=None)
    min_age, max_age = int(df["Age"].min()), int(df["Age"].max())
    age_range = st.slider("Age range", min_value=min_age, max_value=max_age, value=(min_age, max_age), step=1)

mask = (df["Age"].between(age_range[0], age_range[1]))
if personas:
    mask &= df["Persona"].isin(personas)
if clusters:
    mask &= df["Cluster_Label"].isin(clusters)
d = df[mask].copy()

left, mid, right = st.columns(3)
with left:
    st.metric("Users (filtered)", len(d))
with mid:
    st.metric("Avg Retention_30d", f"{d['Retention_30d'].mean():.2f}")
with right:
    st.metric("Avg Sessions/Week", f"{d['Sessions_per_week'].mean():.2f}")

st.markdown("---")

# Chart 1: Top features
feat_counts = d["Feature"].value_counts().sort_values(ascending=False)
fig1 = plt.figure(figsize=(5.5,3.5))
plt.bar(feat_counts.index, feat_counts.values)
plt.title("Top Features (filtered)")
plt.ylabel("Users")
plt.xticks(rotation=20)
st.pyplot(fig1)

# Chart 2: Adoption vs Sessions by Cluster
fig2 = plt.figure(figsize=(5.5,3.5))
for name, grp in d.groupby("Cluster_Label"):
    plt.scatter(grp["Sessions_per_week"], grp["Feature_Adoption"], alpha=0.6, label=name)
plt.xlabel("Sessions per week")
plt.ylabel("Feature Adoption (0..1)")
plt.title("Adoption vs Sessions by Cluster")
plt.legend()
st.pyplot(fig2)

# Chart 3: What-if (demo)
st.subheader("What-if: Increase sessions/week")
inc = st.slider("Increase sessions by (per user):", 0, 3, 1)
ret_gain = np.clip(d["Retention_30d"] + 0.05*inc, 0, 1)
col1, col2 = st.columns(2)
with col1:
    st.write("**Current mean Retention_30d**:", f"{d['Retention_30d'].mean():.3f}")
with col2:
    st.write("**Projected mean Retention_30d**:", f"{ret_gain.mean():.3f}")

st.caption("Note: Simple projection for demo only — not clinical advice.")
st.subheader("Sample rows")
st.dataframe(d.head(20))
