import streamlit as st
import pandas as pd
import joblib
import os
from datetime import datetime
import pandas.errors


# Load trained model
model = joblib.load('student_model.pkl')


# Define input feature names
features = [
    'hint_count', 'bottom_hint', 'attempt_count', 'ms_first_response', 'duration',
    'Average_confidence(FRUSTRATED)', 'Average_confidence(CONFUSED)',
    'Average_confidence(CONCENTRATING)', 'Average_confidence(BORED)', 'action_count',
    'hint_dependency', 'response_speed', 'confidence_balance', 'engagement_ratio',
    'efficiency_indicator'
]


# Import helper functions
from helper_functions import (
    categorize_student_performance,
    recommend_learning_material,
    generate_feedback_message,
    generate_learner_profile,
    generate_combined_recommendation
)


# App Interface
st.title("🎓 AI Tutor: Student Performance Predictor")

student_id = st.text_input("Enter Student ID", "")

st.markdown("Enter student behavior data:")

user_input = {}

user_input['hint_count'] = st.slider("hint_count", 0, 20, 5)
user_input['bottom_hint'] = st.slider("bottom_hint", 0, 20, 5)
user_input['attempt_count'] = st.slider("attempt_count", 0, 15, 3)
user_input['ms_first_response'] = st.slider("ms_first_response", 100, 3000, 800)
user_input['duration'] = st.slider("duration", 100, 3000, 1000)

user_input['Average_confidence(FRUSTRATED)'] = st.slider("Frustrated", 0.0, 1.0, 0.2)
user_input['Average_confidence(CONFUSED)'] = st.slider("Confused", 0.0, 1.0, 0.2)
user_input['Average_confidence(CONCENTRATING)'] = st.slider("Concentrating", 0.0, 1.0, 0.6)
user_input['Average_confidence(BORED)'] = st.slider("Bored", 0.0, 1.0, 0.1)

user_input['action_count'] = st.slider("action_count", 0.0, 1.0, 0.5)
user_input['hint_dependency'] = st.slider("hint_dependency", 0.0, 1.0, 0.2)
user_input['response_speed'] = st.slider("response_speed", 100, 3000, 900)
user_input['confidence_balance'] = st.slider("confidence_balance", 0.0, 1.0, 0.5)
user_input['engagement_ratio'] = st.slider("engagement_ratio", 0.0, 1.0, 0.5)
user_input['efficiency_indicator'] = st.slider("efficiency_indicator", 0.0, 1.0, 0.5)



# 🧠 Predict button logic
if st.button("Predict Performance"):
    input_df = pd.DataFrame([user_input])
    predicted_score = model.predict(input_df)[0]
    learner_profile = generate_learner_profile(user_input)


    # Categorize student
    cat_num, cat_name, desc, emoji = categorize_student_performance(predicted_score)
    combined_recommendation = generate_combined_recommendation(cat_name, learner_profile)
    rec = recommend_learning_material(cat_num)
    fb = generate_feedback_message(cat_num)

    # 📊 Display results
    st.subheader("📋 Prediction Result")
    st.write(f"**learner_profile:** {learner_profile}")
    st.write(f"**Predicted Correctness Score:** {predicted_score:.3f}")
    st.write(f"**Category:** {emoji} {cat_name}")
    st.write(f"**Feedback:** {fb}")
    # st.write(f"**Recommendation:** {rec}")
    st.write(f"**Combined Recommendation:** {combined_recommendation}")



    # Add timestamp + user data + result to a row
    log_row = {
        "student_id": student_id,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **user_input,
        "predicted_score": predicted_score,
        "category": cat_name,
        "learner_profile": learner_profile
    }
    
    
    # Create CSV with headers if it doesn't exist or is empty
    log_path = "prediction_log.csv"
    required_columns = ["student_id", "timestamp", *features, "predicted_score", "category", "learner_profile"]

    if not os.path.exists(log_path) or os.path.getsize(log_path) == 0:
        pd.DataFrame(columns=required_columns).to_csv(log_path, index=False)


    # Append to CSV file
    log_df = pd.DataFrame([log_row])
    log_df.to_csv("prediction_log.csv", mode='a', header=not os.path.exists("prediction_log.csv"), index=False)
    
    
    
    st.subheader("📊 Student Progress Over Time")
    # Check if file exists
    if os.path.exists("prediction_log.csv") and student_id:
        try:
            log_data = pd.read_csv("prediction_log.csv")
            log_data['timestamp'] = pd.to_datetime(log_data['timestamp']) # Convert timestamp to datetime


            # student history filter
            student_history = log_data[log_data['student_id'] == student_id]
            
            if not student_history.empty:
                st.subheader(f"📈 Progress for Student: {student_id}")
                st.line_chart(student_history.set_index("timestamp")["predicted_score"])
            else:
                st.subheader(f"📈 First-time Progress for Student: {student_id}")
                # Create a single-point chart to start the graph
                new_entry = pd.DataFrame({
                    "timestamp": [pd.Timestamp.now()],
                    "predicted_score": [predicted_score]
                }).set_index("timestamp")

                st.line_chart(new_entry["predicted_score"])
        except pandas.errors.EmptyDataError:
            st.warning("📁 prediction_log.csv exists but is empty. A new log entry will be added after this prediction.")
            
    else:
        st.info("No prediction history found yet.")
     
     
        
    # 🔍 Show full prediction history for this student
    if os.path.exists("prediction_log.csv") and student_id:
        log_data = pd.read_csv("prediction_log.csv")
        log_data['timestamp'] = pd.to_datetime(log_data['timestamp'])

        student_history = log_data[log_data['student_id'] == student_id]

        if not student_history.empty:
            st.subheader("📋 Prediction History Table")

            # Select only needed columns for display
            display_cols = ["timestamp", "predicted_score", "category", "learner_profile"]
            display_data = student_history[display_cols].sort_values(by="timestamp", ascending=False).reset_index(drop=True)

            st.dataframe(display_data, use_container_width=True)

    
    
st.markdown("---")
st.markdown("---")
st.subheader("🧑‍🏫 Teacher Dashboard: Class Overview")

# Load log file
if os.path.exists("prediction_log.csv"):
    log_data = pd.read_csv("prediction_log.csv")
    log_data['timestamp'] = pd.to_datetime(log_data['timestamp'])

    # Keep only the latest record per student
    latest_by_student = log_data.sort_values("timestamp", ascending=False).drop_duplicates("student_id", keep='first')

    # Optional filters
    selected_category = st.selectbox("Filter by Category", ["All"] + sorted(latest_by_student["category"].unique()))
    selected_profile = st.selectbox("Filter by Profile", ["All"] + sorted(latest_by_student["learner_profile"].unique()))

    filtered_data = latest_by_student.copy()
    if selected_category != "All":
        filtered_data = filtered_data[filtered_data["category"] == selected_category]
    if selected_profile != "All":
        filtered_data = filtered_data[filtered_data["learner_profile"] == selected_profile]

    # Display columns
    display_cols = ["student_id", "timestamp", "predicted_score", "category", "learner_profile"]
    st.dataframe(filtered_data[display_cols].sort_values("timestamp", ascending=False), use_container_width=True)

else:
    st.info("No prediction history available yet.")

