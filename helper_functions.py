# helper_functions.py - CORRECTED VERSION

import google.generativeai as genai
import pandas as pd
import os
import streamlit as st

# Configure the API key - FIXED VERSION
try:
    # First, try to get from Streamlit secrets (for deployed apps)
    if hasattr(st, 'secrets') and 'GEMINI_API_KEY' in st.secrets:
        api_key = st.secrets['GEMINI_API_KEY']
        genai.configure(api_key=api_key)
        print("✅ API configured from Streamlit secrets")
    # Then try environment variable (consistent naming)
    elif os.getenv('GEMINI_API_KEY'):
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        print("✅ API configured from environment variable")
    # Fallback to GOOGLE_API_KEY if that's what you prefer
    elif os.getenv('GOOGLE_API_KEY'):
        api_key = os.getenv('GOOGLE_API_KEY')
        genai.configure(api_key=api_key)
        print("✅ API configured from GOOGLE_API_KEY environment variable")
    else:
        print("❌ Warning: No API key found. Set GEMINI_API_KEY environment variable or Streamlit secret.")
        api_key = None
except Exception as e:
    print(f"❌ Error configuring Google AI: {e}")
    api_key = None


# Test function to verify API is working
def test_api_connection():
    """Test if the API is properly configured and working"""
    try:
        if not api_key:
            return False, "No API key configured"
        
        # Try different model names that are available in v1beta
        model_names = [
            "gemini-1.5-flash",
            "gemini-1.5-pro", 
            "gemini-2.0-flash-exp",
            "models/gemini-1.5-flash",
            "models/gemini-1.5-pro"
        ]
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Say 'API test successful' if you can read this.")
                
                if response and response.text:
                    return True, f"API connection successful using {model_name}"
            except Exception as e:
                continue  # Try next model
        
        return False, "No working model found. All models failed."
            
    except Exception as e:
        return False, f"API test failed: {str(e)}"


# Your existing helper functions...

def categorize_student_performance(correctness_score):
    if correctness_score < 0.3:
        return (0, "Poor", "Needs immediate intervention and support", "🆘")
    elif correctness_score < 0.45:
        return (1, "Weak", "Requires additional practice and guidance", "⚠️")
    elif correctness_score < 0.6:
        return (2, "Below Average", "Shows potential but needs improvement", "📈")
    elif correctness_score < 0.75:
        return (3, "Average", "Solid understanding with room to grow", "✅")
    elif correctness_score < 0.9:
        return (4, "Strong", "Excellent performance and comprehension", "🌟")
    else:
        return (5, "Outstanding", "Exceptional mastery of the material", "🏆")

def recommend_learning_material(category_number):
    recommendations = {
        0: "🔹 Basics tutorial video + guided beginner-level exercises.",
        1: "🔸 Visual explanation content + step-by-step practice problems.",
        2: "🔹 Practice exercises with hints enabled + instant feedback.",
        3: "✅ Standard module content + end-of-lesson quiz.",
        4: "🌟 Advanced challenge problems + peer group discussion tasks.",
        5: "🏆 Project-based learning module + opportunity to mentor peers."
    }
    return recommendations.get(category_number, "📘 Keep learning and practicing regularly.")

def generate_feedback_message(category_number):
    feedback = {
        0: "It's okay to struggle — the key is to keep going. Let's review the basics together.",
        1: "You're making progress. Focus on the foundation, and don't hesitate to seek help.",
        2: "You've got potential. A little more consistent effort will go a long way!",
        3: "Nice work! You're on track — just refine your skills step by step.",
        4: "Great job! You've developed a solid understanding. Keep challenging yourself.",
        5: "Outstanding! You've truly mastered the topic. Consider exploring advanced material or helping peers."
    }
    return feedback.get(category_number, "Keep pushing forward — every step counts!")

def generate_learner_profile(features):
    duration = features['duration']
    attempt_count = features['attempt_count']
    concentrating = features['Average_confidence(CONCENTRATING)']
    frustrated = features['Average_confidence(FRUSTRATED)']
    confused = features['Average_confidence(CONFUSED)']
    bottom_hint = features['bottom_hint']
    confidence_balance = features['confidence_balance']
    efficiency = features['efficiency_indicator']
    hint_count = features['hint_count']
    hint_dependency = features['hint_dependency']
    
    if (duration < 1800 and attempt_count < 3 and concentrating < 0.5 and frustrated > 0.3):
        return "Fast but Careless 🐇"
    
    if (duration > 1800 and hint_count < 5 and concentrating > 0.6 and efficiency > 0.6):
        return "Slow and Careful 🐢"
    
    if (hint_count > 6 and confused > 0.3 and bottom_hint > 5 and confidence_balance < 0.4):
        return "Confused Learner 🤔"
    
    if (concentrating > 0.6 and confidence_balance > 0.6 and hint_dependency < 0.3 and efficiency > 0.6):
        return "Focused Performer 🎯"
    
    return "General Learner"

def generate_combined_recommendation(category, learner_profile):
    if category == "Poor":
        if "Confused Learner" in learner_profile:
            return "🔁 Start with a short concept video, then move to guided practice with step-by-step hints."
        elif "Slow and Careful" in learner_profile:
            return "🧩 Try scaffolded exercises with feedback after each step to build confidence."
        else:
            return "📘 Begin with foundational videos and low-difficulty exercises."

    elif category == "Weak":
        if "Confused Learner" in learner_profile:
            return "🎥 Rewatch key concepts and then try practice problems with hints enabled."
        elif "Fast but Careless" in learner_profile:
            return "⏳ Try slower-paced problems with explanations after each question."
        else:
            return "📝 Use interactive lessons followed by short quizzes with explanations."

    elif category == "Below Average":
        if "Fast but Careless" in learner_profile:
            return "💡 Focus on accuracy. Try untimed quizzes with instant feedback."
        elif "Focused Performer" in learner_profile:
            return "📚 Review summaries, then solve medium-difficulty problems."
        else:
            return "🛠 Practice mid-level problems with hints disabled, and reflect after each one."

    elif category == "Average":
        if "Focused Performer" in learner_profile:
            return "🎯 Challenge yourself with tougher problems or skip ahead modules."
        elif "Slow and Careful" in learner_profile:
            return "📖 Review notes, then solve a mixed-difficulty quiz to reinforce learning."
        else:
            return "🚀 Stay on track with standard lessons and end-of-module quizzes."

    elif category == "Strong":
        return "🏆 Try optional challenge activities, explore related topics, or help peers."

    elif category == "Outstanding":
        return "🌟 You're doing amazing! Dive into advanced modules or explore new areas beyond the curriculum."

    return "📚 Keep practicing and exploring. Consistency is key!"

def map_difficulty(pred_score, category):
    if category in ["Below Average", "Poor", "Weak"] or pred_score < 0.5:
        return "easy"
    elif pred_score < 0.8:
        return "medium"
    else:
        return "hard"

def load_syllabus_data():
    syllabus_df = {}
    try:
        if os.path.exists("School_Syllabus_Classes1-12.xlsx"):
            syllabus_df = {
                "Class 10": pd.read_excel("School_Syllabus_Classes1-12.xlsx", sheet_name="Class 10 (Core Subjects)"),
                "Class 11": pd.read_excel("School_Syllabus_Classes1-12.xlsx", sheet_name="Class 11 (Core)"),
                "Class 12": pd.read_excel("School_Syllabus_Classes1-12.xlsx", sheet_name="Class 12 (Core)")
            }
        else:
            print("Warning: School_Syllabus_Classes1-12.xlsx not found. Using fallback topics.")
    except Exception as e:
        print(f"Error loading syllabus: {e}")
    return syllabus_df

syllabus_df = load_syllabus_data()

def get_topics_for(grade, subject):
    if isinstance(grade, str) and "Grade" in grade:
        try:
            grade_num = int(grade.split()[-1])
        except:
            grade_num = 1
    else:
        grade_num = grade
    
    if grade_num >= 10 and syllabus_df:
        try:
            df = syllabus_df[f"Class {grade_num}"]
            row = df[df["Subject"].str.contains(subject, case=False)]
            if not row.empty:
                return row.iloc[0]["Topics"]
        except Exception as e:
            print(f"Error accessing syllabus for Grade {grade_num} {subject}: {e}")
    
    fallback_topics = {
        "Math": f"Basic arithmetic, patterns, geometry fundamentals, number operations for Grade {grade_num}",
        "Science": f"Nature observation, basic physics, life science, environmental awareness for Grade {grade_num}",
        "English": f"Reading comprehension, grammar basics, vocabulary building, writing skills for Grade {grade_num}",
        "History": f"Local history, important historical figures, cultural heritage, timeline concepts for Grade {grade_num}"
    }
    return fallback_topics.get(subject, f"Fundamental concepts of {subject} in {grade}")

def generate_quiz(grade, subject, difficulty, num_q=5):
    """Generate a multiple-choice quiz using the LLM with proper error handling."""
    try:
        # Check if API is configured by testing it
        is_working, message = test_api_connection()
        if not is_working:
            return f"❌ Error: API not working properly. {message}"
        
        topics = get_topics_for(grade, subject)
        
        prompt = f"""
You are an experienced teacher creating a {difficulty} level multiple-choice quiz for {grade} {subject}. 

Based on these curriculum topics: {topics}

Please generate {num_q} multiple-choice questions following these requirements:
1. Each question should be appropriate for {grade} level
2. Each question should have exactly 4 options labeled A, B, C, D
3. Clearly indicate the correct answer for each question
4. Questions should be {difficulty} difficulty level
5. Include a mix of conceptual and application-based questions
6. Format each question clearly with the question followed by the four options

Example format:
**Question 1:** [Your question here]
A) Option A
B) Option B  
C) Option C
D) Option D
**Correct Answer:** [Letter]

Please generate the complete quiz now:
"""
        
        # Try different available models
        model_names = [
            "gemini-1.5-flash",
            "gemini-1.5-pro",
            "gemini-2.0-flash-exp"
        ]
        
        for model_name in model_names:
            try:
                model = genai.GenerativeModel(model_name)  
                response = model.generate_content(prompt)
                
                if response and response.text:
                    return response.text
                    
            except Exception as model_error:
                continue  # Try next model
        
        return "❌ Error: All available models failed to generate response."
            
    except Exception as e:
        return f"❌ Error generating quiz: {str(e)}\n\nPlease check:\n1. Your API key is set correctly\n2. You have internet connection\n3. The API key has proper permissions"