# Define required helper functions


# Student Categarization System
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




# Recomand learning Materail
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



# Feedback System
def generate_feedback_message(category_number):
    feedback = {
        0: "It’s okay to struggle — the key is to keep going. Let’s review the basics together.",
        1: "You’re making progress. Focus on the foundation, and don’t hesitate to seek help.",
        2: "You’ve got potential. A little more consistent effort will go a long way!",
        3: "Nice work! You’re on track — just refine your skills step by step.",
        4: "Great job! You’ve developed a solid understanding. Keep challenging yourself.",
        5: "Outstanding! You’ve truly mastered the topic. Consider exploring advanced material or helping peers."
    }
    return feedback.get(category_number, "Keep pushing forward — every step counts!")




# learner Profile (Classifies a student into a learner type based on behavioral features.)
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
    
    # Fast but Careless
    if (duration < 1800 and attempt_count < 3 and concentrating < 0.5 and frustrated > 0.3):
        return "Fast but Careless 🐇"
    
    # Slow and Careful
    if (duration > 1800 and hint_count < 5 and concentrating > 0.6 and efficiency > 0.6):
        return "Slow and Careful 🐢"
    
    # Confused Learner
    if (hint_count > 6 and confused > 0.3 and bottom_hint > 5 and confidence_balance < 0.4):
        return "Confused Learner 🤔"
    
    # Focused Performer
    if (concentrating > 0.6 and confidence_balance > 0.6 and hint_dependency < 0.3 and efficiency > 0.6):
        return "Focused Performer 🎯"
    
    # Default
    return "General Learner"




# Combine recommendation System
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
        return "🌟 You’re doing amazing! Dive into advanced modules or explore new areas beyond the curriculum."

    return "📚 Keep practicing and exploring. Consistency is key!"

