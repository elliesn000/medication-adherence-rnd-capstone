import os, random, math
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
random.seed(42)

N = 600
personas = ["Senior", "Working_Adult", "Multi_Morbidity"]
genders = ["F", "M", "Other"]
features = ["Reminder", "BP_Log", "Symptom_Diary", "Edu_Content", "Teleconsult", "Refill_Reminder"]

def sample_age(persona):
    if persona == "Senior":
        return int(rng.normal(64, 6))
    elif persona == "Working_Adult":
        return int(rng.normal(40, 7))
    else:
        return int(rng.normal(58, 8))

def base_sessions(persona):
    return {"Senior": 4.5, "Working_Adult": 3.5, "Multi_Morbidity": 5.0}[persona]

def feature_pref(persona):
    if persona == "Senior":
        p = [0.32, 0.22, 0.10, 0.20, 0.06, 0.10]
    elif persona == "Working_Adult":
        p = [0.40, 0.15, 0.08, 0.22, 0.05, 0.10]
    else:
        p = [0.28, 0.25, 0.12, 0.20, 0.07, 0.08]
    return rng.choice(features, p=p)

rows = []
for i in range(N):
    persona = rng.choice(personas, p=[0.35, 0.45, 0.20])
    age = max(18, min(85, sample_age(persona)))
    gender = rng.choice(genders, p=[0.52, 0.46, 0.02])
    core_feature = feature_pref(persona)

    lam = base_sessions(persona)
    sessions = int(max(0, rng.poisson(lam=lam)))
    dau_7d = int(min(7, max(0, sessions - rng.integers(0, 2))))

    base_adopt = 0.55 if core_feature in ("Reminder","BP_Log") else 0.42
    noise = rng.normal(0, 0.12)
    feature_adoption = float(np.clip(base_adopt + 0.05*(sessions>=4) + noise, 0, 1))

    persona_bias = {"Senior": 0.15, "Working_Adult": 0.0, "Multi_Morbidity": 0.20}[persona]
    z = -0.7 + 0.35*sessions + 1.5*feature_adoption + persona_bias + rng.normal(0, 0.5)
    retention_30d = 1/(1+math.exp(-z))

    sat_mu = 2.5 + 1.3*feature_adoption + 1.0*retention_30d
    satisfaction = int(np.clip(round(rng.normal(sat_mu, 0.7)), 1, 5))

    rows.append(dict(
        ID=i+1, Age=age, Gender=gender, Persona=persona, Feature=core_feature,
        Sessions_per_week=sessions, DAU_7d=dau_7d,
        Retention_30d=round(retention_30d, 3), Feature_Adoption=round(feature_adoption, 3),
        Satisfaction=satisfaction
    ))

df = pd.DataFrame(rows)
os.makedirs("data", exist_ok=True)
out = "data/app_usage_survey.csv"
df.to_csv(out, index=False)
print(f"Saved: {out} — rows: {len(df)}")
print(df.head(5))
