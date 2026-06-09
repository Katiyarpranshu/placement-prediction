import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import os

# Create models directory if it doesn't exist
os.makedirs('models', exist_ok=True)

print("📊 Loading data...")
# Load data
df = pd.read_csv('data/placement_data.csv')

print(f"✅ Loaded {len(df)} records")

# Create features
df['total_performance'] = (df['bachelor_percentage'] + df['mca_percentage']) / 2
df['skill_score'] = (df['communication_score'] + df['aptitude_score'] + df['coding_skills']) / 3

# Features for training
features = ['bachelor_percentage', 'mca_percentage', 'backlogs', 
            'communication_score', 'aptitude_score', 'coding_skills',
            'internship_done', 'projects_done', 'total_performance', 'skill_score']

X = df[features]
y = df['placed']

print("🔍 Splitting data...")
# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print("📈 Scaling features...")
# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("🤖 Training model...")
# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train_scaled, y_train)

# Evaluate
accuracy = model.score(X_test_scaled, y_test)
print(f"✅ Model accuracy: {accuracy:.2%}")

print("💾 Saving models...")
# Save model and scaler
joblib.dump(model, 'models/best_model.pkl')
joblib.dump(scaler, 'models/scaler.pkl')
joblib.dump(features, 'models/selected_features.pkl')

# Create a dummy feature selector
from sklearn.feature_selection import SelectKBest, f_classif
selector = SelectKBest(f_classif, k=len(features))
selector.fit(X, y)
joblib.dump(selector, 'models/feature_selector.pkl')

print("✅ Models saved successfully in 'models' folder!")
print("\n📁 Files created:")
print("   - models/best_model.pkl")
print("   - models/scaler.pkl")
print("   - models/selected_features.pkl")
print("   - models/feature_selector.pkl")