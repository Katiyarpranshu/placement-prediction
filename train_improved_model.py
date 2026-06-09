import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import warnings
warnings.filterwarnings('ignore')

# Load data (use larger dataset if available)
try:
    df = pd.read_csv('data/placement_data_large.csv')
    print(f"✅ Loaded large dataset: {len(df)} records")
except:
    df = pd.read_csv('data/placement_data.csv')
    print(f"⚠️ Using small dataset: {len(df)} records")

# Enhanced feature engineering
df['total_performance'] = (df['bachelor_percentage'] + df['mca_percentage']) / 2
df['skill_score'] = (df['communication_score'] + df['aptitude_score'] + df['coding_skills']) / 3
df['experience'] = df['internship_done'] * 0.6 + (df['projects_done'] / 10) * 0.4
df['academic_consistency'] = abs(df['bachelor_percentage'] - df['mca_percentage'])
df['weighted_academic'] = df['bachelor_percentage'] * 0.4 + df['mca_percentage'] * 0.6
df['placement_readiness'] = (df['skill_score'] * 0.5 + df['experience'] * 0.3 + df['total_performance'] * 0.2)

# Select features
features = [
    'bachelor_percentage', 'mca_percentage', 'backlogs',
    'communication_score', 'aptitude_score', 'coding_skills',
    'internship_done', 'projects_done', 'total_performance',
    'skill_score', 'experience', 'placement_readiness'
]

X = df[features]
y = df['placed']

# Split and scale
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Try multiple models
models = {
    'Random Forest': RandomForestClassifier(n_estimators=200, max_depth=10, random_state=42),
    'XGBoost': XGBClassifier(n_estimators=200, max_depth=6, learning_rate=0.1, random_state=42),
    'Gradient Boosting': GradientBoostingClassifier(n_estimators=200, max_depth=5, random_state=42),
    'Logistic Regression': LogisticRegression(random_state=42, max_iter=1000)
}

best_model = None
best_score = 0

print("\n📊 Model Performance Comparison:")
print("="*50)

for name, model in models.items():
    # Cross-validation
    cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5)
    
    # Train and test
    model.fit(X_train_scaled, y_train)
    y_pred = model.predict(X_test_scaled)
    test_accuracy = accuracy_score(y_test, y_pred)
    
    print(f"\n{name}:")
    print(f"  CV Score: {cv_scores.mean():.3f} (+/- {cv_scores.std()*2:.3f})")
    print(f"  Test Accuracy: {test_accuracy:.3f}")
    
    if test_accuracy > best_score:
        best_score = test_accuracy
        best_model = model

print(f"\n🏆 Best Model: {best_model.__class__.__name__} (Accuracy: {best_score:.3f})")

# Save the best model
joblib.dump(best_model, 'models/best_model.pkl')
joblib.dump(scaler, 'models/scaler.pkl')
joblib.dump(features, 'models/selected_features.pkl')

print("\n✅ Models saved successfully!")

# Test with different inputs
print("\n🔮 Testing different student profiles:")
test_cases = [
    (90, 92, 0, 9, 9, 9, 1, 5, "Excellent Student"),
    (60, 62, 2, 5, 5, 5, 0, 1, "Poor Student"),
    (75, 78, 0, 7, 7, 8, 1, 3, "Average Student"),
]

for bach, mca, back, comm, apt, code, intern, proj, label in test_cases:
    total_perf = (bach + mca) / 2
    skill = (comm + apt + code) / 3
    exp = intern * 0.6 + (proj / 10) * 0.4
    readiness = (skill * 0.5 + exp * 0.3 + total_perf * 0.2)
    
    input_data = [[bach, mca, back, comm, apt, code, intern, proj, total_perf, skill, exp, readiness]]
    input_scaled = scaler.transform(input_data)
    
    prob = best_model.predict_proba(input_scaled)[0][1]
    pred = best_model.predict(input_scaled)[0]
    
    print(f"\n{label}:")
    print(f"  Probability: {prob*100:.1f}%")
    print(f"  Prediction: {'✅ PLACED' if pred == 1 else '❌ NOT PLACED'}")