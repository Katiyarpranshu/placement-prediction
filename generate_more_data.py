import pandas as pd
import numpy as np
from datetime import datetime

# Generate 200 synthetic student records
np.random.seed(42)

n_samples = 200

# Generate realistic distributions
bachelor_pct = np.random.normal(70, 12, n_samples).clip(40, 100)
mca_pct = bachelor_pct + np.random.normal(2, 5, n_samples).clip(-15, 15)
mca_pct = mca_pct.clip(40, 100)

backlogs = np.random.poisson(0.8, n_samples).clip(0, 5)

# Skills (correlated with placement success)
communication = (bachelor_pct / 10 + np.random.normal(0, 1, n_samples)).clip(1, 10)
aptitude = (bachelor_pct / 10 + np.random.normal(0, 1, n_samples)).clip(1, 10)
coding = (mca_pct / 10 + np.random.normal(0, 1, n_samples)).clip(1, 10)

internship = np.random.choice([0, 1], n_samples, p=[0.4, 0.6])
projects = np.random.poisson(3, n_samples).clip(0, 8)

# Placement logic (more realistic)
placement_prob = (
    0.3 * (bachelor_pct / 100) +
    0.3 * (mca_pct / 100) +
    0.1 * (1 - backlogs / 6) +
    0.1 * (communication / 10) +
    0.1 * (aptitude / 10) +
    0.05 * (coding / 10) +
    0.03 * internship +
    0.02 * (projects / 8)
)

placement_prob = placement_prob.clip(0, 1)
placed = (np.random.random(n_samples) < placement_prob).astype(int)

# Create DataFrame
df = pd.DataFrame({
    'bachelor_percentage': np.round(bachelor_pct, 1),
    'mca_percentage': np.round(mca_pct, 1),
    'backlogs': backlogs,
    'communication_score': np.round(communication, 1),
    'aptitude_score': np.round(aptitude, 1),
    'coding_skills': np.round(coding, 1),
    'internship_done': internship,
    'projects_done': projects,
    'placed': placed
})

# Save to CSV
df.to_csv('data/placement_data_large.csv', index=False)
print(f"✅ Generated {len(df)} synthetic student records")
print(f"📊 Placement rate: {df['placed'].mean()*100:.1f}%")
print(f"\nSample data:")
print(df.head(10))

# Also create features for training
df['total_performance'] = (df['bachelor_percentage'] + df['mca_percentage']) / 2
df['skill_score'] = (df['communication_score'] + df['aptitude_score'] + df['coding_skills']) / 3

print(f"\n📈 Feature correlations with placement:")
print(df[['bachelor_percentage', 'mca_percentage', 'skill_score', 'projects_done', 'placed']].corr()['placed'].sort_values(ascending=False))