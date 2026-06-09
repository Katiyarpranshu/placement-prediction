import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="MCA Placement Predictor",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 MCA Placement Prediction System")
st.markdown("*AI-Powered Placement Predictor with 88% Accuracy*")

# Load model
@st.cache_resource
def load_model():
    try:
        model = joblib.load('models/best_model.pkl')
        scaler = joblib.load('models/scaler.pkl')
        features = joblib.load('models/selected_features.pkl')
        return model, scaler, features
    except:
        st.error("⚠️ Model files not found. Please ensure models are uploaded.")
        return None, None, None

model, scaler, features = load_model()

# Input form
col1, col2 = st.columns(2)

with col1:
    st.subheader("📚 Academic Information")
    student_name = st.text_input("Student Name", "Student")
    bachelor_pct = st.slider("Bachelor's Percentage (%)", 40, 100, 70)
    mca_pct = st.slider("MCA Percentage (%)", 40, 100, 75)
    backlogs = st.number_input("Number of Backlogs", 0, 10, 0)

with col2:
    st.subheader("💪 Skills & Experience")
    communication = st.slider("Communication Skills (1-10)", 1, 10, 7)
    aptitude = st.slider("Aptitude Skills (1-10)", 1, 10, 6)
    coding = st.slider("Coding Skills (1-10)", 1, 10, 7)
    internship = st.radio("Internship Experience", ["Yes", "No"], horizontal=True)
    internship_val = 1 if internship == "Yes" else 0
    projects = st.slider("Projects Completed", 0, 10, 3)

if st.button("🔮 Predict Placement", use_container_width=True):
    if model and scaler:
        # Calculate features
        total_performance = (bachelor_pct + mca_pct) / 2
        skill_score = (communication + aptitude + coding) / 3
        experience_score = internship_val * 0.6 + (projects / 10) * 0.4
        placement_readiness = (skill_score * 0.5 + experience_score * 0.3 + total_performance * 0.2)
        
        # Create feature array
        input_data = np.array([[bachelor_pct, mca_pct, backlogs, communication, 
                                aptitude, coding, internship_val, projects,
                                total_performance, skill_score, experience_score, 
                                placement_readiness]])
        
        input_scaled = scaler.transform(input_data)
        probability = model.predict_proba(input_scaled)[0][1]
        
        # Display result
        col_result1, col_result2 = st.columns(2)
        
        with col_result1:
            if probability >= 0.7:
                st.success(f"### ✅ HIGH CHANCE OF PLACEMENT")
            elif probability >= 0.4:
                st.warning(f"### 📊 MODERATE CHANCE OF PLACEMENT")
            else:
                st.error(f"### ⚠️ LOW CHANCE OF PLACEMENT")
            st.metric("Placement Probability", f"{probability*100:.1f}%")
        
        with col_result2:
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=probability*100,
                title={'text': "Placement Score"},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': "#4CAF50"},
                    'steps': [
                        {'range': [0, 40], 'color': "#ffcccc"},
                        {'range': [40, 70], 'color': "#ffffcc"},
                        {'range': [70, 100], 'color': "#ccffcc"}
                    ]
                }
            ))
            fig.update_layout(height=250)
            st.plotly_chart(fig, use_container_width=True)
        
        # Recommendations
        st.subheader("📋 Recommendations")
        recs = []
        if bachelor_pct < 65:
            recs.append("📚 Improve your bachelor's percentage")
        if coding < 7:
            recs.append("💻 Practice coding on LeetCode")
        if projects < 3:
            recs.append("🚀 Build more projects for portfolio")
        if communication < 7:
            recs.append("🗣️ Improve communication skills")
        
        for rec in recs[:3]:
            st.info(rec)

# Footer
st.markdown("---")
st.markdown("🎓 MCA Placement Prediction System | Powered by Machine Learning")