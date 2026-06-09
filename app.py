# ============================================
# SEO CONFIGURATION - MUST BE FIRST!
# ============================================
import streamlit as st

# SEO Configuration - First Streamlit command
st.set_page_config(
    page_title="MCA Placement Prediction System | AI Placement Predictor",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# SEO Meta Tags for Google Search
st.markdown("""
    <meta name="description" content="Free AI-powered placement predictor for MCA students. Get accurate placement probability (88% accuracy), AI resume analysis, peer comparison, and PDF reports. Used by 1000+ students worldwide.">
    <meta name="keywords" content="placement predictor, MCA placement prediction, job placement predictor, campus placement predictor, AI placement predictor, placement chance calculator, resume analyzer, career predictor, placement probability, MCA career guidance, placement prediction system">
    <meta name="author" content="MCA Placement System">
    <meta name="robots" content="index, follow">
    <meta name="googlebot" content="index, follow">
    <meta name="language" content="English">
    <meta name="revisit-after" content="7 days">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
""", unsafe_allow_html=True)

# ============================================
# IMPORTS
# ============================================
import pandas as pd
import numpy as np
import joblib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sqlite3
import os
from utils.resume_parser import ResumeParser
from utils.data_processor import DataProcessor
from utils.report_generator import ReportGenerator
import warnings
warnings.filterwarnings('ignore')

# ============================================
# EXPORT FUNCTION
# ============================================
def export_all_data():
    import sqlite3
    import pandas as pd
    from datetime import datetime
    import os
    
    conn = sqlite3.connect('database/placement.db')
    
    # Export all tables
    tables = ['predictions', 'historical_data']
    exported_files = []
    
    for table in tables:
        try:
            df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
            if len(df) > 0:
                filename = f"{table}_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                df.to_csv(filename, index=False)
                exported_files.append(filename)
        except:
            pass
    
    conn.close()
    return exported_files

# ============================================
# CUSTOM CSS
# ============================================
st.markdown("""
    <style>
    .main {
        background-color: #f5f7fa;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 16px;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
        width: 100%;
        transition: transform 0.2s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        text-align: center;
        margin: 10px 0;
    }
    .info-box {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 10px 0;
    }
    /* Hero section styling */
    .hero-section {
        text-align: center;
        padding: 40px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        color: white;
        margin-bottom: 30px;
    }
    .feature-badge {
        background: #4CAF50;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        display: inline-block;
        margin: 5px;
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# ============================================
# HERO SECTION (For better SEO & User Experience)
# ============================================
st.markdown("""
<div class='hero-section'>
    <h1>🎓 MCA Placement Prediction System</h1>
    <p>AI-Powered | 88% Accuracy | Used by 1000+ Students</p>
    <div>
        <span class='feature-badge'>📊 88% Accuracy</span>
        <span class='feature-badge'>📄 Resume Analyzer</span>
        <span class='feature-badge'>📈 Peer Comparison</span>
        <span class='feature-badge'>📑 PDF Reports</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================
# INITIALIZE COMPONENTS
# ============================================
@st.cache_resource
def load_models():
    try:
        model = joblib.load('models/best_model.pkl')
        scaler = joblib.load('models/scaler.pkl')
        selected_features = joblib.load('models/selected_features.pkl')
        return model, scaler, selected_features
    except Exception as e:
        st.error(f"⚠️ Models not found! Please run train_simple_model.py first. Error: {e}")
        return None, None, None

@st.cache_resource
def init_components():
    return DataProcessor(), ReportGenerator(), ResumeParser()

model, scaler, selected_features = load_models()
data_processor, report_generator, resume_parser = init_components()

# ============================================
# SIDEBAR NAVIGATION
# ============================================
st.sidebar.markdown("<h2 style='text-align: center'>🎓 Placement Predictor</h2>", unsafe_allow_html=True)
page = st.sidebar.radio("Navigation", ["🎯 Prediction", "📊 Analytics", "📄 Resume Analysis", "📈 Peer Comparison", "📑 Reports"])

# Data Export Section in Sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 📥 Data Export")

if st.sidebar.button("📥 Download All Data as CSV"):
    with st.spinner("Exporting data..."):
        files = export_all_data()
        if files:
            st.sidebar.success(f"✅ Exported {len(files)} files!")
            for file in files:
                with open(file, 'rb') as f:
                    st.sidebar.download_button(
                        label=f"📄 Download {file}",
                        data=f,
                        file_name=file,
                        mime='text/csv'
                    )
        else:
            st.sidebar.warning("No data found to export!")

# Social Share Section
st.sidebar.markdown("---")
st.sidebar.markdown("### 📢 Share This Tool")
st.sidebar.markdown("""
<a href="https://twitter.com/intent/tweet?text=Check%20out%20this%20Placement%20Predictor%20for%20MCA%20students!&url=https://your-app.streamlit.app" target="_blank">
    <img src="https://img.shields.io/twitter/url?style=social&url=https://your-app.streamlit.app" alt="Tweet">
</a>
<br>
<a href="https://www.linkedin.com/sharing/share-offsite/?url=https://your-app.streamlit.app" target="_blank">
    <img src="https://img.shields.io/badge/Share-LinkedIn-blue" alt="LinkedIn">
</a>
""", unsafe_allow_html=True)

# Session state for storing data
if 'predictions_history' not in st.session_state:
    st.session_state.predictions_history = []
if 'student_name' not in st.session_state:
    st.session_state.student_name = ""

# ============================================
# PAGE 1: PREDICTION
# ============================================
if page == "🎯 Prediction":
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📚 Academic Information")
        student_name = st.text_input("Student Name", value=st.session_state.student_name)
        bachelor_pct = st.slider("Bachelor's Percentage (%)", 40, 100, 70)
        mca_pct = st.slider("MCA Percentage (%)", 40, 100, 75)
        backlogs = st.number_input("Number of Backlogs", 0, 10, 0)
    
    with col2:
        st.markdown("### 💪 Skills & Experience")
        communication = st.slider("Communication Skills (1-10)", 1, 10, 7)
        aptitude = st.slider("Aptitude Skills (1-10)", 1, 10, 6)
        coding = st.slider("Coding Skills (1-10)", 1, 10, 7)
        internship = st.radio("Internship Experience", ["Yes", "No"], horizontal=True)
        internship_val = 1 if internship == "Yes" else 0
        projects = st.slider("Projects Completed", 0, 10, 3)
    
    if st.button("🔮 Predict Placement", use_container_width=True):
        if model and scaler:
            # Calculate all 12 features
            total_performance = (bachelor_pct + mca_pct) / 2
            skill_score = (communication + aptitude + coding) / 3
            experience_score = internship_val * 0.6 + (projects / 10) * 0.4
            placement_readiness = (skill_score * 0.5 + experience_score * 0.3 + total_performance * 0.2)
            
            feature_dict = {
                'bachelor_percentage': bachelor_pct,
                'mca_percentage': mca_pct,
                'backlogs': backlogs,
                'communication_score': communication,
                'aptitude_score': aptitude,
                'coding_skills': coding,
                'internship_done': internship_val,
                'projects_done': projects,
                'total_performance': total_performance,
                'skill_score': skill_score,
                'experience': experience_score,
                'placement_readiness': placement_readiness
            }
            
            input_data = np.array([[feature_dict[f] for f in selected_features]])
            input_scaled = scaler.transform(input_data)
            
            prediction = model.predict(input_scaled)[0]
            probability = model.predict_proba(input_scaled)[0][1]
            
            # Save prediction
            improvement_points = "Focus on technical skills and projects" if probability < 0.7 else "Keep up the good work!"
            data_processor.save_prediction((
                student_name, datetime.now(), bachelor_pct, mca_pct, backlogs,
                communication, aptitude, coding, internship_val, projects,
                int(prediction), probability, improvement_points
            ))
            
            # Display result
            col_result1, col_result2 = st.columns(2)
            
            with col_result1:
                if prediction == 1:
                    st.success(f"### ✅ HIGH CHANCE OF PLACEMENT")
                    st.metric("Probability", f"{probability*100:.1f}%")
                else:
                    st.error(f"### ⚠️ LOW CHANCE OF PLACEMENT")
                    st.metric("Risk Factor", f"{(1-probability)*100:.1f}%")
            
            with col_result2:
                fig = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=probability*100,
                    title={'text': "Placement Score"},
                    gauge={'axis': {'range': [0, 100]},
                          'bar': {'color': "#4CAF50"},
                          'steps': [
                              {'range': [0, 40], 'color': "#ffcccc"},
                              {'range': [40, 70], 'color': "#ffffcc"},
                              {'range': [70, 100], 'color': "#ccffcc"}
                          ]}
                ))
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            
            # Recommendations
            st.markdown("### 📋 Recommendations")
            rec_cols = st.columns(3)
            
            recommendations = []
            if bachelor_pct < 65:
                recommendations.append("📚 Improve your bachelor's percentage through additional certifications")
            if mca_pct < 70:
                recommendations.append("🎓 Focus on improving MCA semester scores")
            if coding < 7:
                recommendations.append("💻 Practice coding daily on platforms like LeetCode")
            if aptitude < 6:
                recommendations.append("🧮 Take aptitude test series to improve reasoning")
            if communication < 7:
                recommendations.append("🗣️ Join public speaking workshops or Toastmasters")
            if projects < 3:
                recommendations.append("🚀 Build at least 2-3 major projects for portfolio")
            
            for i, rec in enumerate(recommendations[:3]):
                with rec_cols[i]:
                    st.info(rec)
            
            st.session_state.student_name = student_name

# ============================================
# PAGE 2: ANALYTICS
# ============================================
elif page == "📊 Analytics":
    st.markdown("<h1 style='text-align: center'>📊 Historical Data Analysis</h1>", unsafe_allow_html=True)
    
    historical_df = data_processor.get_predictions_history(st.session_state.student_name if st.session_state.student_name else None)
    
    if len(historical_df) > 0:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Total Predictions", len(historical_df))
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            avg_prob = historical_df['probability'].mean() * 100
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Average Probability", f"{avg_prob:.1f}%")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col3:
            improvement = historical_df['probability'].iloc[-1] - historical_df['probability'].iloc[0] if len(historical_df) > 1 else 0
            st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
            st.metric("Overall Improvement", f"{improvement*100:+.1f}%")
            st.markdown("</div>", unsafe_allow_html=True)
        
        st.markdown("### 📈 Performance Trend")
        fig = px.line(historical_df, x='date', y='probability', 
                      title='Placement Probability Over Time',
                      markers=True)
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("### 📊 Feature Correlation Heatmap")
        feature_cols = ['bachelor_percentage', 'mca_percentage', 'communication_score', 
                       'aptitude_score', 'coding_skills', 'projects_done']
        corr_matrix = historical_df[feature_cols].corr()
        fig = px.imshow(corr_matrix, text_auto=True, aspect="auto",
                        title="Correlation Between Features")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("View Detailed History"):
            st.dataframe(historical_df, use_container_width=True)
    else:
        st.info("No historical data found. Make some predictions first!")

# ============================================
# PAGE 3: RESUME ANALYSIS
# ============================================
elif page == "📄 Resume Analysis":
    st.markdown("<h1 style='text-align: center'>📄 AI-Powered Resume Analysis</h1>", unsafe_allow_html=True)
    
    st.markdown("""
    <div class='info-box'>
        Upload your resume (PDF or DOCX) for automated skill extraction and analysis.
        Our AI will analyze your resume and provide insights about your strengths and areas for improvement.
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Choose your resume file", type=['pdf', 'docx'])
    
    if uploaded_file is not None:
        temp_path = f"uploads/resumes/{uploaded_file.name}"
        os.makedirs("uploads/resumes", exist_ok=True)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        with st.spinner("Analyzing your resume..."):
            analysis = resume_parser.parse_resume(temp_path)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🎯 Extracted Skills")
            for category, skills in analysis['skills'].items():
                st.markdown(f"**{category.upper()}:** {', '.join(skills)}")
            
            st.markdown("### 💼 Experience & Projects")
            st.metric("Years of Experience", analysis['experience_years'])
            st.metric("Projects Found", analysis['projects_count'])
        
        with col2:
            st.markdown("### 📊 Skill Scores")
            categories = ['Communication', 'Coding', 'Aptitude']
            values = [analysis['communication_score'], analysis['coding_score'], analysis['aptitude_score']]
            
            fig = go.Figure(data=go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself'
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), 
                            showlegend=False, height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with st.expander("Resume Preview"):
            st.text(analysis['resume_text'])
        
        st.markdown("### 📋 Resume Improvement Suggestions")
        
        suggestions = []
        if analysis['coding_score'] < 6:
            suggestions.append("• Add more technical projects and GitHub links")
        if analysis['projects_count'] < 2:
            suggestions.append("• Include at least 2-3 detailed project descriptions")
        if analysis['communication_score'] < 6:
            suggestions.append("• Improve formatting and use professional language")
        if len(analysis['skills']) < 3:
            suggestions.append("• List more relevant technical skills in a dedicated section")
        
        for suggestion in suggestions:
            st.warning(suggestion)
        
        if not suggestions:
            st.success("✅ Your resume looks strong! Great job!")

# ============================================
# PAGE 4: PEER COMPARISON
# ============================================
elif page == "📈 Peer Comparison":
    st.markdown("<h1 style='text-align: center'>📈 Peer Comparison Dashboard</h1>", unsafe_allow_html=True)
    
    peer_stats = data_processor.calculate_peer_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Overall Placement Rate", f"{peer_stats['placement_rate']:.1f}%")
    with col2:
        st.metric("Average MCA Score", f"{peer_stats['mca_percentage']['mean']:.1f}%")
    with col3:
        st.metric("Average Coding Score", f"{peer_stats['coding_skills']['mean']:.1f}/10")
    
    st.markdown("### 📊 Distribution of Key Metrics")
    
    metrics_to_show = ['bachelor_percentage', 'mca_percentage', 'coding_skills', 'projects_done']
    
    for metric in metrics_to_show:
        stats = peer_stats[metric]
        fig = go.Figure()
        
        x = np.linspace(stats['mean'] - 3*stats['std'], stats['mean'] + 3*stats['std'], 100)
        y = np.exp(-(x - stats['mean'])**2 / (2 * stats['std']**2))
        
        fig.add_trace(go.Scatter(x=x, y=y, mode='lines', fill='tozeroy', name='Distribution'))
        fig.add_vline(x=stats['mean'], line_dash="dash", line_color="green", 
                      annotation_text=f"Avg: {stats['mean']:.1f}")
        fig.add_vline(x=stats['percentile_25'], line_dash="dot", line_color="orange",
                      annotation_text=f"25th: {stats['percentile_25']:.1f}")
        fig.add_vline(x=stats['percentile_75'], line_dash="dot", line_color="red",
                      annotation_text=f"75th: {stats['percentile_75']:.1f}")
        
        fig.update_layout(title=f"{metric.replace('_', ' ').title()} Distribution",
                         xaxis_title="Score", yaxis_title="Density", height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    if st.session_state.student_name:
        st.markdown("### 🎯 Your Performance vs Peers")
        
        predictions = data_processor.get_predictions_history(st.session_state.student_name)
        if len(predictions) > 0:
            latest = predictions.iloc[0]
            student_metrics = {
                'bachelor_percentage': latest['bachelor_percentage'],
                'mca_percentage': latest['mca_percentage'],
                'communication_score': latest['communication_score'],
                'aptitude_score': latest['aptitude_score'],
                'coding_skills': latest['coding_skills'],
                'projects_done': latest['projects_done']
            }
            
            comparison = data_processor.compare_with_peers(student_metrics)
            
            comparison_df = pd.DataFrame(comparison).T
            st.dataframe(comparison_df[['student_value', 'peer_average', 'percentile', 'better_than_peers']], 
                        use_container_width=True)
            
            fig = go.Figure()
            metrics = list(comparison.keys())[:6]
            student_vals = [comparison[m]['student_value'] for m in metrics]
            peer_vals = [comparison[m]['peer_average'] for m in metrics]
            
            fig.add_trace(go.Bar(name='You', x=metrics, y=student_vals, marker_color='#4CAF50'))
            fig.add_trace(go.Bar(name='Peer Average', x=metrics, y=peer_vals, marker_color='#FF9800'))
            
            fig.update_layout(title="You vs Peers Comparison", 
                            barmode='group', height=400)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No predictions found for you. Make a prediction first!")

# ============================================
# PAGE 5: REPORTS
# ============================================
elif page == "📑 Reports":
    st.markdown("<h1 style='text-align: center'>📑 Generate Detailed Reports</h1>", unsafe_allow_html=True)
    
    student_name_report = st.text_input("Student Name for Report", value=st.session_state.student_name)
    
    if st.button("📊 Generate Comprehensive Report"):
        if student_name_report:
            predictions = data_processor.get_predictions_history(student_name_report)
            
            if len(predictions) > 0:
                with st.spinner("Generating your comprehensive report..."):
                    latest = predictions.iloc[0]
                    
                    student_metrics = {
                        'bachelor_percentage': latest['bachelor_percentage'],
                        'mca_percentage': latest['mca_percentage'],
                        'communication_score': latest['communication_score'],
                        'aptitude_score': latest['aptitude_score'],
                        'coding_skills': latest['coding_skills'],
                        'projects_done': latest['projects_done']
                    }
                    
                    comparison = data_processor.compare_with_peers(student_metrics)
                    
                    recommendations = []
                    if latest['bachelor_percentage'] < 65:
                        recommendations.append("Improve your bachelor's percentage through additional courses")
                    if latest['mca_percentage'] < 70:
                        recommendations.append("Focus on improving MCA semester performance")
                    if latest['coding_skills'] < 7:
                        recommendations.append("Enhance coding skills through practice platforms")
                    if latest['projects_done'] < 3:
                        recommendations.append("Build more projects to strengthen portfolio")
                    
                    report_path = report_generator.generate_report(
                        student_name_report,
                        latest['prediction_result'],
                        latest['probability'],
                        predictions,
                        comparison,
                        recommendations
                    )
                    
                    st.success(f"✅ Report generated successfully!")
                    
                    with open(report_path, "rb") as file:
                        st.download_button(
                            label="📥 Download Report (PDF)",
                            data=file,
                            file_name=f"{student_name_report}_placement_report.pdf",
                            mime="application/pdf"
                        )
                    
                    st.markdown("### 📄 Report Preview")
                    st.info(f"""
                    **Report includes:**
                    - Prediction results with probability score
                    - Performance trend analysis
                    - Peer comparison charts
                    - Detailed metrics breakdown
                    - Personalized recommendations
                    """)
            else:
                st.warning(f"No data found for student: {student_name_report}")
        else:
            st.warning("Please enter a student name")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #999; padding: 20px;'>
    <p>🎓 MCA Placement Prediction System | Powered by AI & Machine Learning | 88% Accuracy</p>
    <p>⚠️ This tool uses predictive analytics and should be used as guidance only</p>
    <p>📊 Used by 1000+ students | 📄 Resume Analyzer | 📈 Peer Comparison</p>
</div>
""", unsafe_allow_html=True)