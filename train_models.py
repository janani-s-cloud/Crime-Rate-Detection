import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import r2_score, mean_squared_error

def load_and_preprocess_data(filepath):
    print("Loading data...")
    df = pd.read_csv(filepath)
    
    # Basic cleaning
    df = df.dropna()
    
    # 1. Feature Engineering: Percentage Share of each crime type
    # columns 4 to -1 are crime types (excluding TOTAL IPC CRIMES)
    ignore_cols = ['STATE/UT', 'DISTRICT', 'YEAR', 'TOTAL IPC CRIMES', 'index']
    crime_cols = [col for col in df.columns if col not in ignore_cols]
    
    # Create percentage columns
    for col in crime_cols:
        # Avoid division by zero
        df[f'{col}_PERCENT'] = (df[col] / df['TOTAL IPC CRIMES']) * 100
        # Replace inf with 0
        df[f'{col}_PERCENT'] = df[f'{col}_PERCENT'].replace([np.inf, -np.inf], 0)
        df[f'{col}_PERCENT'] = df[f'{col}_PERCENT'].fillna(0)

    # 2. Feature Engineering: Total Crime Growth Rate
    # Aggregated by Year and State for growth trend
    state_yearly = df.groupby(['STATE/UT', 'YEAR'])['TOTAL IPC CRIMES'].sum().reset_index()
    state_yearly['GROWTH_RATE'] = state_yearly.groupby('STATE/UT')['TOTAL IPC CRIMES'].pct_change() * 100
    state_yearly['GROWTH_RATE'] = state_yearly['GROWTH_RATE'].replace([np.inf, -np.inf], 0)
    state_yearly['GROWTH_RATE'] = state_yearly['GROWTH_RATE'].fillna(0)
    
    return df, state_yearly, crime_cols

def train_growth_model(state_yearly):
    print("\nTraining Growth Model (Linear Regression)...")
    
    # We want to predict Growth Rate based on Year (and maybe State encoded)
    # For simplicity, let's predict general trend based on Year first
    X = state_yearly[['YEAR']]
    y = state_yearly['GROWTH_RATE']
    
    growth_model = LinearRegression()
    growth_model.fit(X, y)
    
    print(f"Growth Model Coefficient: {growth_model.coef_[0]}")
    print(f"Growth Model Intercept: {growth_model.intercept_}")
    
    return growth_model

def train_share_models(df, crime_cols):
    print("\nTraining Share Models (KNN & Random Forest)...")
    
    # Encoders
    le_state = LabelEncoder()
    le_district = LabelEncoder()
    
    df['STATE_ENC'] = le_state.fit_transform(df['STATE/UT'])
    df['DISTRICT_ENC'] = le_district.fit_transform(df['DISTRICT'])
    
    X = df[['STATE_ENC', 'DISTRICT_ENC', 'YEAR']]
    
    models = {}
    
    # We will train a model for EACH crime type percentage? 
    # Or one multi-output model? 
    # Let's try a Random Forest that predicts percentages for all crime types at once if possible,
    # or just keep it simple and train one model per major crime type if performance is bad.
    # For this scale, Random Forest Regressor supports multi-output.
    
    y = df[[f'{col}_PERCENT' for col in crime_cols]]
    
    # Split
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Random Forest
    rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_model.fit(X_train, y_train)
    
    score = rf_model.score(X_test, y_test)
    print(f"Random Forest Multi-output R2 Score: {score:.4f}")
    
    models['share_model'] = rf_model
    models['le_state'] = le_state
    models['le_district'] = le_district
    models['crime_cols'] = crime_cols
    
    return models

def save_artifacts(growth_model, share_models_dict):
    import os
    if not os.path.exists("model"):
        os.makedirs("model")
        
    print("\nSaving models...")
    with open("model/growth_model.pkl", "wb") as f:
        pickle.dump(growth_model, f)
        
    with open("model/share_model_data.pkl", "wb") as f:
        pickle.dump(share_models_dict, f)
        
    print("Models saved to model/ directory.")

if __name__ == "__main__":
    df, state_yearly, crime_cols = load_and_preprocess_data("data/crime_data.csv")
    
    growth_model = train_growth_model(state_yearly)
    share_models_dict = train_share_models(df, crime_cols)
    
    save_artifacts(growth_model, share_models_dict)
