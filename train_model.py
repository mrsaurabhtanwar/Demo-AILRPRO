## FINALLIZATION OF THE MODEL

# load important libraies
import numpy as np
import pandas as pd
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split, GridSearchCV, KFold
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt



# Load and process data
df = pd.read_csv('cleaned_student_data.csv')



# Group by user_id to summarize student behavior
student_df = df.groupby('user_id').agg({
    'correct': 'mean',   # our target
    'hint_count': 'mean',
    'bottom_hint': 'mean',
    'attempt_count': 'mean',
    'ms_first_response': 'mean',
    'duration': 'mean',
    'Average_confidence(FRUSTRATED)': 'mean',
    'Average_confidence(CONFUSED)': 'mean',
    'Average_confidence(CONCENTRATING)': 'mean',
    'Average_confidence(BORED)': 'mean',
    'action_count': 'mean'
}).reset_index()




# Data preprocessing
student_df['duration'] = student_df['duration'].clip(lower=0, upper=10000)
student_df['attempt_count'] = student_df['attempt_count'].clip(upper=7)




# Create behavioral features
student_df['hint_dependency'] = student_df['hint_count'] / (student_df['attempt_count'] + 1)
student_df['response_speed'] = 1 / (student_df['ms_first_response'] + 1)
student_df['confidence_balance'] = (
    student_df['Average_confidence(CONCENTRATING)'] - 
    student_df['Average_confidence(FRUSTRATED)'] - 
    student_df['Average_confidence(CONFUSED)']
)
student_df['engagement_ratio'] = (
    student_df['Average_confidence(CONCENTRATING)'] / 
    (student_df['Average_confidence(BORED)'] + 0.01)
)
student_df['efficiency_indicator'] = student_df['action_count'] / (student_df['attempt_count'] + 1)



# Update X to include new features
X = student_df.drop(columns=['user_id', 'correct'])  # all features without target
y = student_df['correct']  # our target
print("TARGET DISTRIBUTION ANALYSIS:")
print(f"Correctness Range: [{y.min():.3f}, {y.max():.3f}]")
print(f"Mean Correctness: {y.mean():.3f}")
print(f"Std Correctness: {y.std():.3f}")




# Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)




# Optimized Hyperparameter grid for Regression
param_grid = {
    'max_depth': [4, 6],           
    'n_estimators': [200],         
    'learning_rate': [0.1, 0.15],   
    'subsample': [0.9],            
    'colsample_bytree': [0.9],    
    'reg_alpha': [0.1],           
    'reg_lambda': [1]             
}



# XGBoost Regressor
xgb_model = XGBRegressor(
    objective='reg:squarederror',
    eval_metric='rmse',
    random_state=42
)



# Cross-validation for regression
cv = KFold(n_splits=3, shuffle=True, random_state=42)



# Grid search
grid_search = GridSearchCV(
    estimator=xgb_model,
    param_grid=param_grid,
    cv=cv,
    scoring='neg_root_mean_squared_error',
    verbose=1,
    n_jobs=-1
)



# Train the model
grid_search.fit(X_train, y_train)
best_model = grid_search.best_estimator_



# Make predictions
y_pred = best_model.predict(X_test)



# Evaluation metrics
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)




print("REGRESSION MODEL RESULTS")
print(f"Best Parameters: {grid_search.best_params_}")
print(f"Best CV Score (RMSE): {abs(grid_search.best_score_):.4f}")
print("Test Set Performance:")
print(f"RMSE: {rmse:.4f}")
print(f"MAE:  {mae:.4f}")
print(f"R²:   {r2:.4f}")



# Feature importance
feature_importance = pd.DataFrame({
    'feature': X.columns,
    'importance': best_model.feature_importances_
}).sort_values('importance', ascending=False)

print("TOP 10 MOST IMPORTANT FEATURES:")
for i, (_, row) in enumerate(feature_importance.head(10).iterrows(), 1):
    print(f"{i:2d}. {row['feature']:<35} {row['importance']:.4f}")




import joblib

joblib.dump(best_model, 'student_model.pkl')