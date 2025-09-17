import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

os.makedirs("report", exist_ok=True)

df = pd.read_csv("data/app_usage_survey.csv")
print("Shape:", df.shape)
print(df.head())

# 1) Top features
feat_counts = df["Feature"].value_counts().sort_values(ascending=False)
plt.figure(figsize=(7,4))
plt.bar(feat_counts.index, feat_counts.values)
plt.title("Top Features Used")
plt.ylabel("Users")
plt.xticks(rotation=20)
plt.tight_layout()
plt.savefig("report/top_features.png", dpi=180)
plt.close()

# 2) Retention by age
bins = [17,30,40,50,60,70,90]
labels = ["18-30","31-40","41-50","51-60","61-70","71+"]
df["Age_Group"] = pd.cut(df["Age"], bins=bins, labels=labels)
ret_by_age = df.groupby("Age_Group")["Retention_30d"].mean().reindex(labels)
plt.figure(figsize=(6,3.8))
plt.bar(ret_by_age.index.astype(str), ret_by_age.values)
plt.title("Average 30-day Retention by Age Group")
plt.ylabel("Retention_30d (0..1)")
plt.tight_layout()
plt.savefig("report/retention_by_age.png", dpi=180)
plt.close()

# 3) Adoption vs Sessions
plt.figure(figsize=(6.2,4.6))
plt.scatter(df["Sessions_per_week"], df["Feature_Adoption"], alpha=0.6)
plt.title("Feature Adoption vs Sessions/Week")
plt.xlabel("Sessions per week")
plt.ylabel("Feature Adoption (0..1)")
plt.tight_layout()
plt.savefig("report/adoption_vs_sessions_scatter.png", dpi=180)
plt.close()

# 4) KMeans
features_cols = ["Sessions_per_week","DAU_7d","Retention_30d","Feature_Adoption","Satisfaction"]
X = df[features_cols].values
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

kmeans = KMeans(n_clusters=3, random_state=42, n_init=20)
df["Cluster"] = kmeans.fit_predict(X_scaled)

# 5) Summary
cluster_summary = df.groupby("Cluster")[features_cols].mean().round(3)
cluster_counts = df["Cluster"].value_counts().sort_index()
cluster_summary["Count"] = cluster_counts.values
cluster_summary.to_csv("report/cluster_summary.csv")
print("\nCluster summary:\n", cluster_summary)

# 6) Labels
def label_row(row, centers_df):
    c = int(row["Cluster"])
    s = centers_df.loc[c]
    if s["Sessions_per_week"] >= centers_df["Sessions_per_week"].median() and s["Feature_Adoption"] >= centers_df["Feature_Adoption"].median():
        return "Power Users"
    if s["Sessions_per_week"] <= centers_df["Sessions_per_week"].median() and s["Feature_Adoption"] < centers_df["Feature_Adoption"].median()+0.05:
        return "Trial/Low Adoption"
    return "Reminder-focused"

centers = df.groupby("Cluster")[features_cols].mean()
df["Cluster_Label"] = df.apply(label_row, axis=1, centers_df=centers)

# 7) Save clustered dataset
df.to_csv("data/app_usage_with_clusters.csv", index=False)

# 8) Scatter Sessions vs Retention by cluster
plt.figure(figsize=(6.4,4.6))
for c in sorted(df["Cluster"].unique()):
    m = df["Cluster"]==c
    plt.scatter(df.loc[m,"Sessions_per_week"], df.loc[m,"Retention_30d"], alpha=0.6, label=f"Cluster {c}")
plt.xlabel("Sessions per week")
plt.ylabel("Retention_30d")
plt.title("Clusters: Sessions vs Retention")
plt.legend()
plt.tight_layout()
plt.savefig("report/cluster_sessions_retention.png", dpi=180)
plt.close()

print("Analysis complete. See 'report/' and 'data/app_usage_with_clusters.csv'.")
