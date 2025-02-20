import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from fpdf import FPDF
import random

# Page config
st.set_page_config(
    page_title="Fitness Tracker Dashboard",
    page_icon="💪",
    layout="wide"
)

# Initialize session state
if 'workouts' not in st.session_state:
    st.session_state.workouts = []
if 'goals' not in st.session_state:
    st.session_state.goals = []

# Updated Styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stButton>button {
        width: 100%;
        height: 3rem;
        font-size: 1.2rem;
        background-color: #1E88E5 !important;
        color: white;
        border: none !important;
    }
    .stButton>button:hover {
        background-color: #1E88E5 !important;
        border: none !important;
    }
    .stButton>button:active {
        background-color: #1E88E5 !important;
        border: none !important;
    }
    .workout-card {
        padding: 1.5rem;
        background-color: white;
        border: 2px solid #e6e6e6;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .metric-card {
        text-align: center;
        padding: 1.5rem;
        background-color: white;
        border: 2px solid #1E88E5;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .goal-card {
        background-color: white;
        border: 2px solid #1E88E5;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .tip-box {
        background-color: white;
        border-left: 5px solid #1E88E5;
        padding: 1rem;
        margin: 1rem 0;
    }
    .level-box {
        background-color: white;
        border: 2px solid #1E88E5;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    h1, h2, h3, h4 {
        color: #1565C0;
    }
    </style>
""", unsafe_allow_html=True)

# Constants
FITNESS_TIPS = {
    "Beginner": [
        "Start with 10 minutes of walking daily",
        "Stay hydrated - drink water before, during, and after exercise",
        "Focus on proper form rather than speed",
        "Get at least 7-8 hours of sleep",
        "Start with bodyweight exercises before using weights"
    ],
    "Intermediate": [
        "Mix cardio with strength training",
        "Try HIIT workouts for better results",
        "Include rest days in your routine",
        "Track your protein intake",
        "Try new exercises to challenge yourself"
    ],
    "Advanced": [
        "Focus on progressive overload",
        "Consider split training routines",
        "Monitor your heart rate zones",
        "Plan deload weeks",
        "Include mobility work in your routine"
    ]
}

MOTIVATIONAL_QUOTES = [
    "💪 Every rep counts!",
    "🌟 You're stronger than you think!",
    "🎯 Small progress is still progress!",
    "⚡ Your future self will thank you!",
    "🔥 Keep pushing your limits!",
    "✨ You're doing amazing!",
    "💫 Consistency beats perfection!",
    "🌈 Every workout makes you stronger!"
]

# Updated PDF creation function
def create_pdf_report(workouts):
    """Create PDF report from workout data"""
    try:
        pdf = FPDF()
        pdf.add_page()
        
        # Title
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Fitness Tracker Report', 0, 1, 'C')
        pdf.ln(10)
        
        # Summary
        metrics = calculate_metrics(workouts)
        
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Summary', 0, 1, 'L')
        pdf.set_font('Arial', '', 12)
        pdf.cell(0, 10, f"Total Workouts: {metrics['total_workouts']}", 0, 1, 'L')
        pdf.cell(0, 10, f"Total Duration: {metrics['total_duration']} minutes", 0, 1, 'L')
        pdf.cell(0, 10, f"Total Calories: {metrics['total_calories']} kcal", 0, 1, 'L')
        pdf.ln(10)
        
        # Workout List
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 10, 'Workout History', 0, 1, 'L')
        
        # Table header
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(30, 10, 'Date', 1)
        pdf.cell(30, 10, 'Type', 1)
        pdf.cell(30, 10, 'Duration', 1)
        pdf.cell(30, 10, 'Calories', 1)
        pdf.ln()
        
        # Table content
        pdf.set_font('Arial', '', 10)
        for workout in workouts:
            # Convert all values to ASCII-safe strings
            date = str(workout['date'])
            workout_type = workout['type'][:20]  # Limit length to avoid overflow
            duration = str(workout['duration'])
            calories = str(workout['calories'])
            
            try:
                pdf.cell(30, 10, date, 1)
                pdf.cell(30, 10, workout_type, 1)
                pdf.cell(30, 10, duration, 1)
                pdf.cell(30, 10, calories, 1)
                pdf.ln()
            except Exception:
                continue
        
        return pdf.output(dest='S').encode('latin-1', errors='replace')
    except Exception as e:
        st.error(f"Error creating PDF: {str(e)}")
        return None

# Helper functions (unchanged)
def generate_exercise_tips(workouts):
    """Generate personalized exercise tips based on workout history"""
    if not workouts:
        return ["Start your fitness journey by logging your first workout!"]
    
    df = pd.DataFrame(workouts)
    tips = []
    
    df['date'] = pd.to_datetime(df['date'])
    weekly_workouts = len(df[df['date'] >= (datetime.now() - timedelta(days=7))])
    if weekly_workouts < 3:
        tips.append("Try to exercise at least 3 times per week for better results")
    
    avg_duration = df['duration'].mean()
    if avg_duration < 30:
        tips.append("Aim for at least 30 minutes per workout session")
    
    workout_types = df['type'].unique()
    if len(workout_types) < 3:
        tips.append("Mix up your routine with different types of exercises")
    
    avg_calories = df['calories'].mean()
    if avg_calories < 200:
        tips.append("Consider increasing workout intensity to burn more calories")
    
    return tips

def save_workout(workout_data):
    """Save workout to session state"""
    st.session_state.workouts.append(workout_data)

def create_progress_chart(data, metric='duration'):
    """Create line chart for progress visualization"""
    df = pd.DataFrame(data)
    fig = px.line(
        df, 
        x='date', 
        y=metric,
        title=f'{metric.title()} Over Time'
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title=metric.title(),
        showlegend=True
    )
    return fig

def create_workout_distribution(data):
    """Create pie chart for workout type distribution"""
    df = pd.DataFrame(data)
    workout_counts = df['type'].value_counts()
    fig = px.pie(
        values=workout_counts.values,
        names=workout_counts.index,
        title="Workout Type Distribution"
    )
    return fig

def calculate_metrics(workouts):
    """Calculate summary metrics"""
    if not workouts:
        return {
            'total_workouts': 0,
            'total_duration': 0,
            'total_calories': 0,
            'avg_duration': 0,
            'weekly_workouts': 0
        }
    
    df = pd.DataFrame(workouts)
    weekly_df = df[df['date'] >= (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")]
    
    return {
        'total_workouts': len(workouts),
        'total_duration': df['duration'].sum(),
        'total_calories': df['calories'].sum(),
        'avg_duration': round(df['duration'].mean(), 1),
        'weekly_workouts': len(weekly_df)
    }

def get_fitness_level(workouts):
    """Determine user's fitness level based on workout history"""
    if not workouts:
        return "Beginner"
    
    df = pd.DataFrame(workouts)
    total_workouts = len(df)
    avg_duration = df['duration'].mean()
    
    if total_workouts < 10 or avg_duration < 20:
        return "Beginner"
    elif total_workouts < 30 or avg_duration < 45:
        return "Intermediate"
    else:
        return "Advanced"

def main():
    st.title("💪 Fitness Tracker Dashboard")
    st.markdown("Track, Visualize, and Improve Your Fitness Journey")
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.radio(
            "Go to",
            ["Log Workout", "View Progress", "Set Goals", "Export Data"]
        )
    
    if page == "Log Workout":
        st.header("📝 Log Your Workout")
        
        tabs = st.tabs(["Manual Entry", "Sync Device"])
        
        with tabs[0]:
            col1, col2 = st.columns(2)
            
            with col1:
                date = st.date_input("Date", datetime.now())
                workout_type = st.selectbox(
                    "Workout Type",
                    ["Running", "Cycling", "Strength Training", "Yoga", "Swimming", "HIIT", "Other"]
                )
                
            with col2:
                duration = st.number_input("Duration (minutes)", min_value=1, value=30)
                
            col3, col4 = st.columns(2)
            with col3:
                distance = st.number_input("Distance", min_value=0.0, value=0.0, step=0.1)
                st.markdown("*in km*")
            with col4:
                heart_rate = st.number_input("Avg Heart Rate", min_value=0, value=0)
                st.markdown("*in bpm*")
                
            calories = st.number_input("Calories Burned", min_value=0, value=100)
            st.markdown("*in kcal*")
            
            notes = st.text_area("Notes (optional)")
            
            if st.button("Save Workout", use_container_width=True):
                workout = {
                    'date': date.strftime("%Y-%m-%d"),
                    'type': workout_type,
                    'duration': duration,
                    'calories': calories,
                    'distance': distance,
                    'heart_rate': heart_rate,
                    'notes': notes
                }
                save_workout(workout)
                
                st.success("Workout logged successfully! 🎉")
                st.markdown(f"### {random.choice(MOTIVATIONAL_QUOTES)}")
                
                fitness_level = get_fitness_level(st.session_state.workouts)
                tip = random.choice(FITNESS_TIPS[fitness_level])
                st.info(f"💡 Tip for {fitness_level} level: {tip}")
                
        with tabs[1]:
            st.info("Device sync feature coming soon!")
            
    elif page == "View Progress":
        st.header("📊 Your Progress")
        
        if not st.session_state.workouts:
            st.info("No workouts logged yet. Start by logging your first workout!")
            return
            
        # Summary metrics
        metrics = calculate_metrics(st.session_state.workouts)
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Workouts", metrics['total_workouts'])
        with col2:
            st.metric("Weekly Workouts", metrics['weekly_workouts'])
        with col3:
            st.metric("Total Duration", f"{metrics['total_duration']} mins")
        with col4:
            st.metric("Total Calories", f"{metrics['total_calories']} kcal")
        with col5:
            st.metric("Avg Duration", f"{metrics['avg_duration']} mins")
            
        # Progress charts
        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(create_progress_chart(st.session_state.workouts, 'duration'), use_container_width=True)
        with col2:
            st.plotly_chart(create_workout_distribution(st.session_state.workouts), use_container_width=True)
            
        # Exercise tips
        st.subheader("💡 Personalized Tips")
        tips = generate_exercise_tips(st.session_state.workouts)
        for tip in tips:
            st.markdown(f"""
                <div class="tip-box">
                    <p style='color: #1a1a1a; margin: 0;'>💡 {tip}</p>
                </div>
            """, unsafe_allow_html=True)
            
        # Recent workouts
        st.subheader("Recent Workouts")
        df = pd.DataFrame(st.session_state.workouts[::-1])
        st.dataframe(df, use_container_width=True)
        
        st.markdown("### 💪 Your Fitness Journey")
        fitness_level = get_fitness_level(st.session_state.workouts)
        st.markdown(f"""
            <div class="level-box">
                <h4 style='color: #2E7D32; margin-bottom: 1rem;'>Current Level: {fitness_level}</h4>
                <p style='color: #1a1a1a; margin-bottom: 1rem;'>Daily Tip: {random.choice(FITNESS_TIPS[fitness_level])}</p>
                <p style='color: #4CAF50; font-style: italic; font-weight: bold;'>{random.choice(MOTIVATIONAL_QUOTES)}</p>
            </div>
        """, unsafe_allow_html=True)
        
    elif page == "Set Goals":
        st.header("🎯 Fitness Goals")
        
        # Add new goal
        st.subheader("Add New Goal")
        col1, col2 = st.columns(2)
        
        with col1:
            goal_type = st.selectbox(
                "Goal Type",
                ["Weekly Workouts", "Duration per Session", "Calories per Week", "Distance Goal"]
            )
            
        with col2:
            target_value = st.number_input("Target Value", min_value=1)
            
        if st.button("Add Goal"):
            goal = {
                'type': goal_type,
                'target': target_value,
                'current': 0,
                'date_added': datetime.now().strftime("%Y-%m-%d")
            }
            st.session_state.goals.append(goal)
            st.success("Goal added successfully!")
            
        # Display goals
        st.subheader("Your Goals")
        for goal in st.session_state.goals:
            st.markdown(f"""
                <div class="goal-card">
                    <h4 style='color: #2E7D32; margin-bottom: 1rem;'>{goal['type']}</h4>
                    <p style='color: #1a1a1a;'>Target: {goal['target']}</p>
                    <p style='color: #1a1a1a;'>Current: {goal['current']}</p>
                    <p style='color: #666666;'>Added: {goal['date_added']}</p>
                </div>
            """, unsafe_allow_html=True)
        
    elif page == "Export Data":
        st.header("📤 Export Your Data")
        
        export_format = st.selectbox(
            "Choose Format",
            ["PDF", "CSV", "TXT"]
        )
        
        if st.button("Export"):
            df = pd.DataFrame(st.session_state.workouts)
            
            if export_format == "PDF":
                pdf_data = create_pdf_report(st.session_state.workouts)
                if pdf_data:
                    st.download_button(
                        "Download PDF",
                        pdf_data,
                        "fitness_tracker_report.pdf",
                        "application/pdf"
                    )
                
            elif export_format == "CSV":
                csv = df.to_csv(index=False)
                st.download_button(
                    "Download CSV",
                    csv,
                    "fitness_tracker_data.csv",
                    "text/csv"
                )
            else:  # TXT
                txt = df.to_string()
                st.download_button(
                    "Download TXT",
                    txt,
                    "fitness_tracker_data.txt",
                    "text/plain"
                )

if __name__ == "__main__":
    main()
