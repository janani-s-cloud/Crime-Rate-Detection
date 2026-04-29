import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

try:
    df = pd.read_csv("data/crime_data.csv")
    print("Data loaded.")
except Exception as e:
    print(f"Error loading CSV: {e}")
    df = pd.DataFrame()

def test_crime_data(state=None, district=None, crime_type="TOTAL IPC CRIMES"):
    print(f"Testing with State={state}, District={district}, Crime Type={crime_type}")
    
    if df.empty:
        print("DF is empty")
        return

    # Filter data
    filtered_df = df.copy()
    if state:
        filtered_df = filtered_df[filtered_df["STATE/UT"] == state]
    if district:
        filtered_df = filtered_df[filtered_df["DISTRICT"] == district]
    
    # Check if crime_type exists
    if crime_type not in filtered_df.columns:
        print(f"Crime type {crime_type} not found.")
        crime_type = "TOTAL IPC CRIMES"
    
    # Aggregate crime per year
    yearly_crime = filtered_df.groupby("YEAR")[crime_type].sum().reset_index()
    
    if yearly_crime.empty:
        print("Yearly crime is empty")
        return

    print("Yearly Data Head:")
    print(yearly_crime.head())

    # Prepare data for Linear Regression
    X = yearly_crime["YEAR"].values.reshape(-1, 1)
    y = yearly_crime[crime_type].values
    
    print(f"X shape: {X.shape}, y shape: {y.shape}")
    print(f"y values: {y}")

    # Train model
    try:
        model = LinearRegression()
        model.fit(X, y)
        print("Model trained.")
    except Exception as e:
        print(f"Error training model: {e}")
        return
    
    # Predict up to 2025
    last_year = int(yearly_crime["YEAR"].max())
    future_years = np.arange(last_year + 1, 2026).reshape(-1, 1)
    future_predictions = model.predict(future_years)
    
    print("Predictions generated.")
    print(future_predictions)

# Test case that failed
test_crime_data(crime_type="TOTAL IPC CRIMES")
