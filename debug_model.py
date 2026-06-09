import joblib
import numpy as np

# Load model
model = joblib.load('models/best_model.pkl')
scaler = joblib.load('models/scaler.pkl')
features = joblib.load('models/selected_features.pkl')

print("="*60)
print("MODEL INFORMATION")
print("="*60)
print(f"Model expects {len(features)} features:")
for i, f in enumerate(features, 1):
    print(f"  {i}. {f}")
print()

# Function to calculate all 12 features from basic inputs
def prepare_features(bach, mca, backlogs, comm, apt, coding, internship, projects):
    """Convert basic inputs to all 12 features the model expects"""
    
    # Calculate derived features
    total_performance = (bach + mca) / 2
    skill_score = (comm + apt + coding) / 3
    experience = internship * 0.6 + (projects / 10) * 0.4
    placement_readiness = (skill_score * 0.5 + experience * 0.3 + total_performance * 0.2)
    
    # Return all 12 features in the exact order
    return [
        bach,                    # bachelor_percentage
        mca,                     # mca_percentage
        backlogs,                # backlogs
        comm,                    # communication_score
        apt,                     # aptitude_score
        coding,                  # coding_skills
        internship,              # internship_done
        projects,                # projects_done
        total_performance,       # total_performance
        skill_score,             # skill_score
        experience,              # experience
        placement_readiness      # placement_readiness
    ]

# Test different student profiles
test_cases = [
    {
        'name': '🌟 EXCELLENT STUDENT',
        'bach': 92, 'mca': 94, 'backlogs': 0,
        'comm': 9, 'apt': 9, 'coding': 9,
        'internship': 1, 'projects': 5
    },
    {
        'name': '👍 GOOD STUDENT',
        'bach': 78, 'mca': 82, 'backlogs': 0,
        'comm': 8, 'apt': 7, 'coding': 8,
        'internship': 1, 'projects': 3
    },
    {
        'name': '📊 AVERAGE STUDENT',
        'bach': 65, 'mca': 68, 'backlogs': 1,
        'comm': 6, 'apt': 6, 'coding': 6,
        'internship': 0, 'projects': 2
    },
    {
        'name': '⚠️ BELOW AVERAGE',
        'bach': 55, 'mca': 58, 'backlogs': 2,
        'comm': 5, 'apt': 4, 'coding': 5,
        'internship': 0, 'projects': 1
    },
    {
        'name': '❌ POOR STUDENT',
        'bach': 42, 'mca': 45, 'backlogs': 4,
        'comm': 3, 'apt': 3, 'coding': 2,
        'internship': 0, 'projects': 0
    },
    {
        'name': '💪 SKILLED BUT LOW ACADEMICS',
        'bach': 48, 'mca': 52, 'backlogs': 2,
        'comm': 9, 'apt': 8, 'coding': 9,
        'internship': 1, 'projects': 4
    },
    {
        'name': '🎓 HIGH ACADEMICS LOW SKILLS',
        'bach': 88, 'mca': 85, 'backlogs': 0,
        'comm': 4, 'apt': 4, 'coding': 4,
        'internship': 0, 'projects': 1
    }
]

print("="*60)
print("📊 PREDICTION RESULTS FOR DIFFERENT PROFILES")
print("="*60)

results = []
for test in test_cases:
    # Prepare 12 features
    features_list = prepare_features(
        test['bach'], test['mca'], test['backlogs'],
        test['comm'], test['apt'], test['coding'],
        test['internship'], test['projects']
    )
    
    # Convert to numpy array and scale
    input_array = np.array([features_list])
    input_scaled = scaler.transform(pd.DataFrame(input_array, columns=features))
    
    # Predict
    prediction = model.predict(input_scaled)[0]
    probability = model.predict_proba(input_scaled)[0][1]
    
    # Store result
    result = {
        'name': test['name'],
        'probability': probability,
        'prediction': prediction,
        'details': test
    }
    results.append(result)
    
    # Display
    status_icon = "✅" if prediction == 1 else "❌"
    status_text = "PLACED" if prediction == 1 else "NOT PLACED"
    
    # Color based on probability
    if probability >= 0.7:
        bar = "🟢🟢🟢🟢🟢🟢🟢🟢🟢🟢"
    elif probability >= 0.5:
        bar = "🟡🟡🟡🟡🟡⚪⚪⚪⚪⚪"
    else:
        bar = "🔴🔴🔴🔴🔴🔴🔴⚪⚪⚪"
    
    print(f"\n{test['name']}")
    print(f"  Academics: {test['bach']}% (Bach) | {test['mca']}% (MCA) | Backlogs: {test['backlogs']}")
    print(f"  Skills: Comm={test['comm']} | Apt={test['apt']} | Coding={test['coding']}")
    print(f"  Experience: {'Yes' if test['internship'] else 'No'} Internship | {test['projects']} Projects")
    print(f"  {bar} {probability*100:.1f}%")
    print(f"  Result: {status_icon} {status_text}")

# Summary
print("\n" + "="*60)
print("📈 SUMMARY ANALYSIS")
print("="*60)

# Check if model is differentiating
probs = [r['probability'] for r in results]
print(f"Probability range: {min(probs)*100:.1f}% - {max(probs)*100:.1f}%")
print(f"Probability variance: {np.var(probs):.4f}")

if max(probs) - min(probs) < 0.2:
    print("\n⚠️ WARNING: Model is NOT differentiating well!")
    print("   All probabilities are too similar.")
    print("   Solution: Need more diverse training data.")
else:
    print("\n✅ Model is differentiating between students!")
    print("   High performers show high probability, low performers show low probability.")

print("\n" + "="*60)