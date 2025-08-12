import streamlit as st
import pandas as pd
import joblib
import os
from datetime import datetime
import pandas.errors

# Import helper functions
try:
    from helper_functions import (
        categorize_student_performance,
        recommend_learning_material,
        generate_feedback_message,
        generate_learner_profile,
        generate_combined_recommendation,
        map_difficulty,
        generate_quiz,
        test_api_connection
    )
    
    # Test API connection at startup
    api_working, api_message = test_api_connection()
    api_status = "✅" if api_working else "❌"
    
except ImportError as e:
    st.error(f"❌ Error importing helper functions: {e}")
    st.stop()

# Load trained model
try:
    model = joblib.load('student_model.pkl')
    if hasattr(model, 'feature_names_in_'):
        model_features = list(model.feature_names_in_)
    else:
        model_features = None
except FileNotFoundError:
    st.error("❌ Model file 'student_model.pkl' not found. Please ensure the model file is in the correct directory.")
    st.stop()

# Define input feature names (must match training)
features = [
    'hint_count', 'bottom_hint', 'attempt_count', 'ms_first_response', 'duration',
    'Average_confidence(FRUSTRATED)', 'Average_confidence(CONFUSED)',
    'Average_confidence(CONCENTRATING)', 'Average_confidence(BORED)', 'action_count',
    'hint_dependency', 'response_speed', 'confidence_balance', 'engagement_ratio',
    'efficiency_indicator'
]

# Initialize session state for quiz
if 'quiz_generated' not in st.session_state:
    st.session_state.quiz_generated = False
    st.session_state.quiz_text = ""
    st.session_state.prediction_made = False
    st.session_state.prediction_data = {}

# 🌐 Streamlit App Interface
st.title("🎓 AI Tutor: Student Performance Predictor")

# API Status in header
st.markdown(f"**API Status:** {api_status} {api_message}")

student_id = st.text_input("Enter Student ID", "")
grade = st.selectbox("Select Grade", ["Grade 1", "Grade 2", "Grade 3", "Grade 4", "Grade 5", "Grade 6", "Grade 7", "Grade 8", "Grade 9", "Grade 10", "Grade 11", "Grade 12"])
subject = st.selectbox("Select Subject", ["Math", "Science", "English", "History"])

st.markdown("### Enter student behavior data:")

user_input = {}

# Group related inputs for better organization
col1, col2 = st.columns(2)

with col1:
    user_input['hint_count'] = st.slider("Hint Count", 0, 20, 5)
    user_input['bottom_hint'] = st.slider("Bottom Hint", 0, 20, 5)
    user_input['attempt_count'] = st.slider("Attempt Count", 0, 15, 3)
    user_input['ms_first_response'] = st.slider("First Response Time (ms)", 100, 3000, 800)
    user_input['duration'] = st.slider("Duration", 100, 3000, 1000)
    user_input['action_count'] = st.slider("Action Count", 0.0, 1.0, 0.5)
    user_input['response_speed'] = st.slider("Response Speed", 100, 3000, 900)
    user_input['engagement_ratio'] = st.slider("Engagement Ratio", 0.0, 1.0, 0.5)

with col2:
    user_input['Average_confidence(FRUSTRATED)'] = st.slider("Frustrated Level", 0.0, 1.0, 0.2)
    user_input['Average_confidence(CONFUSED)'] = st.slider("Confused Level", 0.0, 1.0, 0.2)
    user_input['Average_confidence(CONCENTRATING)'] = st.slider("Concentrating Level", 0.0, 1.0, 0.6)
    user_input['Average_confidence(BORED)'] = st.slider("Bored Level", 0.0, 1.0, 0.1)
    user_input['hint_dependency'] = st.slider("Hint Dependency", 0.0, 1.0, 0.2)
    user_input['confidence_balance'] = st.slider("Confidence Balance", 0.0, 1.0, 0.5)
    user_input['efficiency_indicator'] = st.slider("Efficiency Indicator", 0.0, 1.0, 0.5)

# Function to prepare data for model prediction
def prepare_model_input(user_data):
    expected_features = model_features if model_features else features
    input_data = []
    missing_features = []
    
    for feature in expected_features:
        if feature in user_data:
            input_data.append(user_data[feature])
        else:
            missing_features.append(feature)
            input_data.append(0.0)
    
    if missing_features:
        st.warning(f"⚠️ Missing features filled with default values: {missing_features}")
    
    input_df = pd.DataFrame([input_data], columns=expected_features)
    return input_df

# 🧠 Predict button logic
if st.button("🔮 Predict Performance"):
    if not student_id.strip():
        st.warning("⚠️ Please enter a Student ID before making predictions.")
    else:
        with st.spinner("Analyzing student performance..."):
            try:
                input_df = prepare_model_input(user_input)
                predicted_score = model.predict(input_df)[0]
                learner_profile = generate_learner_profile(user_input)

                # Categorize student
                cat_num, cat_name, desc, emoji = categorize_student_performance(predicted_score)
                combined_recommendation = generate_combined_recommendation(cat_name, learner_profile)
                rec = recommend_learning_material(cat_num)
                fb = generate_feedback_message(cat_num)

                # Store prediction data for quiz generation
                st.session_state.prediction_data = {
                    'predicted_score': predicted_score,
                    'cat_name': cat_name,
                    'cat_num': cat_num,
                    'emoji': emoji,
                    'learner_profile': learner_profile,
                    'combined_recommendation': combined_recommendation,
                    'feedback': fb,
                    'description': desc
                }
                st.session_state.prediction_made = True

                # 📊 Display results
                st.subheader("📋 Prediction Result")
                
                results_col1, results_col2 = st.columns([1, 2])
                
                with results_col1:
                    st.metric("Predicted Score", f"{predicted_score:.3f}")
                    st.metric("Performance Category", f"{emoji} {cat_name}")
                
                with results_col2:
                    st.write(f"**Learner Profile:** {learner_profile}")
                    st.write(f"**Description:** {desc}")
                    st.write(f"**Feedback:** {fb}")
                    st.write(f"**Combined Recommendation:** {combined_recommendation}")

                # Create CSV with headers if it doesn't exist or is empty
                log_path = "prediction_log.csv"
                required_columns = ["student_id", "timestamp", "grade", "subject", *features, "predicted_score", "category", "learner_profile"]

                # Better CSV file handling
                if not os.path.exists(log_path) or os.path.getsize(log_path) == 0:
                    # Create new file with proper headers
                    pd.DataFrame(columns=required_columns).to_csv(log_path, index=False)
                    file_exists = False
                else:
                    file_exists = True

                # Prepare log row with all required columns
                log_row = {}
                for col in required_columns:
                    if col == "student_id":
                        log_row[col] = student_id
                    elif col == "timestamp":
                        log_row[col] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    elif col == "grade":
                        log_row[col] = grade
                    elif col == "subject":
                        log_row[col] = subject
                    elif col == "predicted_score":
                        log_row[col] = predicted_score
                    elif col == "category":
                        log_row[col] = cat_name
                    elif col == "learner_profile":
                        log_row[col] = learner_profile
                    elif col in user_input:
                        log_row[col] = user_input[col]
                    else:
                        log_row[col] = 0.0  # Default value for missing features

                # Append to CSV file with consistent structure
                log_df = pd.DataFrame([log_row])
                
                try:
                    log_df.to_csv(log_path, mode='a', header=not file_exists, index=False)
                    st.success("✅ Prediction saved to history!")
                except Exception as csv_error:
                    st.warning(f"⚠️ Could not save to history: {csv_error}")
                    # Continue without saving to CSV

            except Exception as e:
                st.error(f"❌ Error during prediction: {e}")
                st.session_state.prediction_made = False

# Quiz Generation Section
if st.session_state.prediction_made:
    st.markdown("---")
    st.subheader("📝 Generate Practice Quiz")
    
    quiz_col1, quiz_col2 = st.columns([1, 3])
    
    with quiz_col1:
        if st.button("🎯 Generate Quiz"):
            if not api_working:
                st.error(f"❌ Cannot generate quiz: {api_message}")
            else:
                with st.spinner("Generating personalized quiz..."):
                    try:
                        pred_data = st.session_state.prediction_data
                        difficulty = map_difficulty(pred_data['predicted_score'], pred_data['cat_name'])
                        
                        quiz_text = generate_quiz(grade, subject, difficulty, num_q=5)
                        st.session_state.quiz_text = quiz_text
                        st.session_state.quiz_generated = True
                        
                    except Exception as e:
                        st.error(f"❌ Error generating quiz: {e}")
                        st.session_state.quiz_generated = False
    
    with quiz_col2:
        pred_data = st.session_state.prediction_data
        difficulty = map_difficulty(pred_data['predicted_score'], pred_data['cat_name'])
        st.info(f"📊 Quiz will be generated at **{difficulty}** difficulty level based on your performance prediction.")

    # Display generated quiz
    if st.session_state.quiz_generated and st.session_state.quiz_text:
        st.subheader(f"📋 {subject} Quiz for {grade} - {difficulty.title()} Level")
        
        if st.session_state.quiz_text.startswith("❌"):
            st.error(st.session_state.quiz_text)
        else:
            st.markdown(st.session_state.quiz_text)
            
            if st.button("🗑️ Clear Quiz"):
                st.session_state.quiz_generated = False
                st.session_state.quiz_text = ""
                st.rerun()

# Student Progress Section
if student_id:
    st.markdown("---")
    st.subheader("📊 Student Progress Over Time")
    
    if os.path.exists("prediction_log.csv"):
        try:
            # Robust CSV reading with error handling
            log_data = pd.read_csv("prediction_log.csv", on_bad_lines='skip', encoding='utf-8')
            
            # Check if the dataframe is empty after skipping bad lines
            if log_data.empty:
                st.warning("📁 CSV file exists but contains no valid data.")
            else:
                # Ensure timestamp column exists and convert
                if 'timestamp' in log_data.columns:
                    log_data['timestamp'] = pd.to_datetime(log_data['timestamp'], errors='coerce')
                    
                    # Filter student history
                    student_history = log_data[log_data['student_id'] == student_id]
                    
                    if not student_history.empty:
                        st.subheader(f"📈 Progress for Student: {student_id}")
                        
                        # Check if predicted_score column exists
                        if 'predicted_score' in student_history.columns:
                            # Remove rows with invalid timestamps or scores
                            valid_history = student_history.dropna(subset=['timestamp', 'predicted_score'])
                            
                            if not valid_history.empty:
                                st.line_chart(valid_history.set_index("timestamp")["predicted_score"])
                                
                                # Show full prediction history for this student
                                st.subheader("📋 Prediction History Table")
                                available_cols = [col for col in ["timestamp", "grade", "subject", "predicted_score", "category", "learner_profile"] if col in student_history.columns]
                                display_data = student_history[available_cols].sort_values(by="timestamp", ascending=False).reset_index(drop=True)
                                st.dataframe(display_data, use_container_width=True)
                            else:
                                st.warning("No valid prediction data found for this student.")
                        else:
                            st.warning("Predicted score column not found in history data.")
                            
                    elif st.session_state.prediction_made:
                        st.subheader(f"📈 First-time Progress for Student: {student_id}")
                        # Create a single-point chart to start the graph
                        new_entry = pd.DataFrame({
                            "timestamp": [pd.Timestamp.now()],
                            "predicted_score": [st.session_state.prediction_data['predicted_score']]
                        }).set_index("timestamp")
                        st.line_chart(new_entry["predicted_score"])
                    else:
                        st.info("No prediction history found for this student yet.")
                else:
                    st.error("Timestamp column not found in CSV file.")
                    
        except pd.errors.ParserError as e:
            st.error(f"❌ CSV file is corrupted. Error: {e}")
            st.info("💡 **Solution**: Delete 'prediction_log.csv' file and make a new prediction to recreate it.")
            if st.button("🗑️ Reset CSV File"):
                try:
                    os.remove("prediction_log.csv")
                    st.success("✅ CSV file deleted. Make a new prediction to start fresh.")
                    st.rerun()
                except Exception as del_error:
                    st.error(f"Error deleting file: {del_error}")
                    
        except pandas.errors.EmptyDataError:
            st.warning("📁 prediction_log.csv exists but is empty. A new log entry will be added after this prediction.")
        except Exception as e:
            st.error(f"❌ Unexpected error reading CSV: {e}")
            
    else:
        st.info("No prediction history found yet.")

# Teacher Dashboard
st.markdown("---")
st.markdown("---")
st.subheader("🧑‍🏫 Teacher Dashboard: Class Overview")

if os.path.exists("prediction_log.csv"):
    try:
        # Robust CSV reading for teacher dashboard
        log_data = pd.read_csv("prediction_log.csv", on_bad_lines='skip', encoding='utf-8')
        
        if log_data.empty:
            st.warning("📁 CSV file exists but contains no valid data.")
        elif 'timestamp' not in log_data.columns:
            st.error("❌ CSV file format is incorrect. Missing required columns.")
        else:
            log_data['timestamp'] = pd.to_datetime(log_data['timestamp'], errors='coerce')
            
            # Remove rows with invalid timestamps
            log_data = log_data.dropna(subset=['timestamp'])

            if not log_data.empty:
                # Keep only the latest record per student
                latest_by_student = log_data.sort_values("timestamp", ascending=False).drop_duplicates("student_id", keep='first')

                # Optional filters - only show options that exist in data
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if 'category' in latest_by_student.columns:
                        categories = ["All"] + sorted(latest_by_student["category"].dropna().unique())
                        selected_category = st.selectbox("Filter by Category", categories)
                    else:
                        selected_category = "All"
                        
                with col2:
                    if 'learner_profile' in latest_by_student.columns:
                        profiles = ["All"] + sorted(latest_by_student["learner_profile"].dropna().unique())
                        selected_profile = st.selectbox("Filter by Profile", profiles)
                    else:
                        selected_profile = "All"
                        
                with col3:
                    if 'subject' in latest_by_student.columns:
                        subjects = ["All"] + sorted(latest_by_student["subject"].dropna().unique())
                        selected_subject = st.selectbox("Filter by Subject", subjects)
                    else:
                        selected_subject = "All"

                filtered_data = latest_by_student.copy()
                
                # Apply filters only if columns exist
                if selected_category != "All" and 'category' in filtered_data.columns:
                    filtered_data = filtered_data[filtered_data["category"] == selected_category]
                if selected_profile != "All" and 'learner_profile' in filtered_data.columns:
                    filtered_data = filtered_data[filtered_data["learner_profile"] == selected_profile]
                if selected_subject != "All" and 'subject' in filtered_data.columns:
                    filtered_data = filtered_data[filtered_data["subject"] == selected_subject]

                # Display columns - only show what exists
                potential_cols = ["student_id", "timestamp", "grade", "subject", "predicted_score", "category", "learner_profile"]
                display_cols = [col for col in potential_cols if col in filtered_data.columns]
                
                if display_cols:
                    st.dataframe(filtered_data[display_cols].sort_values("timestamp", ascending=False), use_container_width=True)

                    # Summary statistics
                    st.markdown("### 📈 Class Summary")
                    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
                    
                    with summary_col1:
                        st.metric("Total Students", len(filtered_data))
                    with summary_col2:
                        if 'predicted_score' in filtered_data.columns:
                            avg_score = filtered_data['predicted_score'].mean()
                            st.metric("Average Score", f"{avg_score:.3f}" if not pd.isna(avg_score) else "N/A")
                        else:
                            st.metric("Average Score", "N/A")
                    with summary_col3:
                        if 'category' in filtered_data.columns:
                            top_category = filtered_data['category'].mode()
                            st.metric("Most Common Category", top_category[0] if len(top_category) > 0 else "N/A")
                        else:
                            st.metric("Most Common Category", "N/A")
                    with summary_col4:
                        if 'learner_profile' in filtered_data.columns:
                            top_profile = filtered_data['learner_profile'].mode()
                            st.metric("Most Common Profile", top_profile[0] if len(top_profile) > 0 else "N/A")
                        else:
                            st.metric("Most Common Profile", "N/A")
                else:
                    st.error("No valid columns found for display.")
            else:
                st.warning("No valid data found after cleaning.")

    except pd.errors.ParserError as e:
        st.error(f"❌ CSV file is corrupted. Error: {e}")
        st.info("💡 **Solution**: Delete 'prediction_log.csv' file and make new predictions to recreate it.")
        if st.button("🗑️ Reset CSV File (Dashboard)"):
            try:
                os.remove("prediction_log.csv")
                st.success("✅ CSV file deleted. Make new predictions to start fresh.")
                st.rerun()
            except Exception as del_error:
                st.error(f"Error deleting file: {del_error}")
                
    except Exception as e:
        st.error(f"Error loading dashboard data: {e}")
        st.info("💡 Try refreshing the page or resetting the CSV file.")
else:
    st.info("No prediction history available yet.")

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** Enter a Student ID and make predictions to track progress over time.")
# st.markdown("📧 For technical support, please contact your system administrator.")