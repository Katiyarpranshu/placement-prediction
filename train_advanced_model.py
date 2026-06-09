import pandas as pd
import numpy as np
import joblib
import json
from sklearn.model_selection import train_test_split, GridSearchCV, cross_val_score
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.feature_selection import SelectKBest, f_classif, RFE
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import warnings
warnings.filterwarnings('ignore')

# Load data
df = pd.read_csv('data/placement_data.csv')

# Feature Engineering
def create_features(df):
    df_copy = df.copy()
    
    # Academic features
    df_copy['total_performance'] = (df_copy['bachelor_percentage'] + df_copy['mca_percentage']) / 2
    df_copy['academic_consistency'] = df_copy['bachelor_percentage'] - df_copy['mca_percentage']
    df_copy['weighted_academic'] = (df_copy['bachelor_percentage'] * 0.4 + df_copy['mca_percentage'] * 0.6)
    
    # Skill features
    df_copy['skill_score'] = (df_copy['communication_score'] + df_copy['aptitude_score'] + df_copy['coding_skills']) / 3
    df_copy['technical_score'] = (df_copy['coding_skills'] + df_copy['aptitude_score']) / 2
    df_copy['soft_skill_score'] = df_copy['communication_score']
    
    # Experience features
    df_copy['experience_score'] = df_copy['internship_done'] * 0.6 + (df_copy['projects_done'] / 10) * 0.4
    df_copy['project_intensity'] = df_copy['projects_done'] / (df_copy['backlogs'] + 1)
    
    # Interaction features
    df_copy['academic_skill'] = df_copy['total_performance'] * df_copy['skill_score'] / 100
    df_copy['placement_readiness'] = (df_copy['skill_score'] * 0.5 + df_copy['experience_score'] * 0.3 + 
                                       df_copy['total_performance'] * 0.2)
    
    return df_copy

df_enhanced = create_features(df)

# Feature selection
feature_columns = [
    'bachelor_percentage', 'mca_percentage', 'backlogs',
    'communication_score', 'aptitude_score', 'coding_skills',
    'internship_done', 'projects_done',
    'total_performance', 'academic_consistency', 'weighted_academic',
    'skill_score', 'technical_score', 'soft_skill_score',
    'experience_score', 'project_intensity', 'academic_skill', 'placement_readiness'
]

X = df_enhanced[feature_columns]
y = df_enhanced['placed']

# Feature selection techniques
print("🔍 Applying Feature Selection Techniques...")

# 1. SelectKBest
selector_kbest = SelectKBest(score_func=f_classif, k=10)
X_kbest = selector_kbest.fit_transform(X, y)
kbest_features = X.columns[selector_kbest.get_support()].tolist()

# 2. RFE with RandomForest
rfe_selector = RFE(RandomForestClassifier(n_estimators=100, random_state=42), n_features_to_select=8)
rfe_selector.fit(X, y)
rfe_features = X.columns[rfe_selector.support_].tolist()

# Use intersection of best features
final_features = list(set(kbest_features[:8] + rfe_features[:8]))
print(f"✅ Selected features: {final_features}")

X_selected = X[final_features]

# Split data
X_train, X_test, y_train, y_test = train_test_split(X_selected, y, test_size=0.2, random_state=42, stratify=y)

# Scale features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Hyperparameter tuning with GridSearchCV
print("\n🎯 Performing Hyperparameter Tuning...")

# Random Forest Tuning
rf_params = {
    'n_estimators': [100, 200, 300],
    'max_depth': [3, 5, 7, 10],
    'min_samples_split': [2, 5, 10],
    'min_samples_leaf': [1, 2, 4]
}

rf_grid = GridSearchCV(
    RandomForestClassifier(random_state=42),
    rf_params,
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    verbose=1
)
rf_grid.fit(X_train_scaled, y_train)

# XGBoost Tuning
xgb_params = {
    'n_estimators': [100, 200],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.01, 0.1, 0.3],
    'subsample': [0.8, 1.0]
}

xgb_grid = GridSearchCV(
    XGBClassifier(random_state=42, use_label_encoder=False, eval_metric='logloss'),
    xgb_params,
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    verbose=1
)
xgb_grid.fit(X_train_scaled, y_train)

# Gradient Boosting Tuning
gb_params = {
    'n_estimators': [100, 200],
    'max_depth': [3, 5, 7],
    'learning_rate': [0.05, 0.1, 0.2],
    'subsample': [0.8, 1.0]
}

gb_grid = GridSearchCV(
    GradientBoostingClassifier(random_state=42),
    gb_params,
    cv=5,
    scoring='accuracy',
    n_jobs=-1,
    verbose=1
)
gb_grid.fit(X_train_scaled, y_train)

# Compare models
models = {
    'Random Forest': rf_grid.best_estimator_,
    'XGBoost': xgb_grid.best_estimator_,
    'Gradient Boosting': gb_grid.best_estimator_
}

best_model = None
best_score = 0
metrics_results = {}

print("\n📊 Model Comparison:")
for name, model in models.items():
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
    
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    roc_auc = roc_auc_score(y_test, y_pred_proba)
    
    metrics_results[name] = {
        'accuracy': accuracy,
        'precision': precision,
        'recall': recall,
        'f1_score': f1,
        'roc_auc': roc_auc,
        'best_params': model.get_params()
    }
    
    print(f"\n{name}:")
    print(f"  Accuracy: {accuracy:.4f}")
    print(f"  Precision: {precision:.4f}")
    print(f"  Recall: {recall:.4f}")
    print(f"  F1-Score: {f1:.4f}")
    print(f"  ROC-AUC: {roc_auc:.4f}")
    
    if accuracy > best_score:
        best_score = accuracy
        best_model = model

print(f"\n🏆 Best Model: {best_model.__class__.__name__} with Accuracy: {best_score:.4f}")

# Save models and artifacts
joblib.dump(best_model, 'models/best_model.pkl')
joblib.dump(scaler, 'models/scaler.pkl')
joblib.dump(selector_kbest, 'models/feature_selector.pkl')
joblib.dump(final_features, 'models/selected_features.pkl')

# Save metrics
with open('models/model_metrics.json', 'w') as f:
    json.dump(metrics_results, f, indent=4)

print("\n✅ Advanced model training completed successfully!")