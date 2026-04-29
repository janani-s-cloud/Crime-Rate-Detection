from flask import Flask, render_template, request, jsonify
import pickle
import numpy as np
import pandas as pd

app = Flask(__name__)

# -----------------------------
# Load Data
# -----------------------------
try:
    df = pd.read_csv("data/crime_data.csv")
except Exception as e:
    print(f"Error loading CSV: {e}")
    df = pd.DataFrame()

# -----------------------------
# Load trained ML models
# -----------------------------
try:
    with open("model/growth_model.pkl", "rb") as f:
        growth_model = pickle.load(f)
    with open("model/share_model_data.pkl", "rb") as f:
        share_data = pickle.load(f)
        share_model = share_data['share_model']
        le_state = share_data['le_state']
        le_district = share_data['le_district']
        crime_cols = share_data['crime_cols']
except Exception as e:
    print(f"Error loading models: {e}")
    growth_model = None
    share_model = None
    le_state = None
    le_district = None
    crime_cols = []

# -----------------------------
# Home page
# -----------------------------
@app.route("/")
def home():
    return render_template("predict.html")

# -----------------------------
# Prediction route
# -----------------------------
@app.route("/predict", methods=["POST"])
def predict():
    if not growth_model or not share_model:
        return render_template("predict.html", result="Error: Models not loaded.")

    try:
        year = int(request.form["year"])
        state = request.form["state"]
        district = request.form["district"]

        # 1. Predict Growth Rate (Global Trend for now)
        # In a real scenario, this should be state-specific
        growth_pred = growth_model.predict(np.array([[year]]))
        growth_rate = growth_pred[0]

        # 2. Predict Crime Share Percentages
        # Encode inputs
        try:
            state_enc = le_state.transform([state])[0]
            district_enc = le_district.transform([district])[0]
        except ValueError:
            return render_template("predict.html", result="Error: Unknown State or District selected.")

        # inputs: STATE_ENC, DISTRICT_ENC, YEAR
        X_share = np.array([[state_enc, district_enc, year]])
        share_pred = share_model.predict(X_share)[0] # Array of percentages

        # Format Results
        growth_msg = f"Predicted Crime Growth Rate for {year}: {growth_rate:.2f}% (Global Trend)"
        
        share_results = []
        for i, col in enumerate(crime_cols):
            share_results.append({
                "crime": col,
                "percentage": round(share_pred[i], 2)
            })
        
        # Sort by highest percentage
        share_results.sort(key=lambda x: x["percentage"], reverse=True)
        top_shares = share_results[:5] # Top 5 crimes

        return render_template(
            "predict.html",
            growth_result=growth_msg,
            share_results=top_shares,
            selected_year=year,
            selected_state=state,
            selected_district=district
        )

    except Exception as e:
        return render_template("predict.html", result=f"Error making prediction: {e}")

# -----------------------------
# Analysis Page
# -----------------------------
@app.route("/analysis")
def analysis():
    return render_template("analysis.html")

# -----------------------------
# API for Chart Data
# -----------------------------
@app.route("/api/crime_data")
def crime_data():
    if df.empty:
        return jsonify({"labels": [], "historical": [], "projected": []})

    # Get filters
    state = request.args.get("state")
    district = request.args.get("district")
    crime_type = request.args.get("crime_type", "TOTAL IPC CRIMES")

    # Filter data
    filtered_df = df.copy()
    if state:
        filtered_df = filtered_df[filtered_df["STATE/UT"] == state]
    if district:
        filtered_df = filtered_df[filtered_df["DISTRICT"] == district]
    
    # Check if crime_type exists
    if crime_type not in filtered_df.columns:
        crime_type = "TOTAL IPC CRIMES"
    
    try:
        # Aggregate crime per year
        yearly_crime = filtered_df.groupby("YEAR")[crime_type].sum().reset_index()
        
        if yearly_crime.empty:
            return jsonify({"labels": [], "historical": [], "projected": []})

        # Prepare data for Linear Regression
        X = yearly_crime["YEAR"].values.reshape(-1, 1)
        y = yearly_crime[crime_type].values
        
        # Train model
        from sklearn.linear_model import LinearRegression
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict up to 2025
        last_year = int(yearly_crime["YEAR"].max())
        future_years = np.arange(last_year + 1, 2026).reshape(-1, 1)
        future_predictions = model.predict(future_years)
        
        # Format response
        response_data = {
            "labels": yearly_crime["YEAR"].tolist() + future_years.flatten().tolist(),
            "historical": yearly_crime[crime_type].tolist() + [None] * len(future_years),
            "projected": [None] * len(yearly_crime) + future_predictions.tolist()
        }
        
        # Connect the lines: make the first projected point equal to the last historical point
        response_data["projected"][len(yearly_crime)-1] = float(yearly_crime[crime_type].iloc[-1])
        
        return jsonify(response_data)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

# -----------------------------
# API for Helper Data (States, Districts, Crime Types)
# -----------------------------
@app.route("/api/states")
def get_states():
    if df.empty: return jsonify([])
    states = sorted(df["STATE/UT"].unique().tolist())
    return jsonify(states)

@app.route("/api/districts")
def get_districts():
    state = request.args.get("state")
    if df.empty or not state: return jsonify([])
    districts = sorted(df[df["STATE/UT"] == state]["DISTRICT"].unique().tolist())
    return jsonify(districts)

@app.route("/api/crime_types")
def get_crime_types():
    if df.empty: return jsonify([])
    # Exclude non-crime columns
    ignore_cols = ["STATE/UT", "DISTRICT", "YEAR", "TOTAL IPC CRIMES", "index"]
    crime_types = [col for col in df.columns if col not in ignore_cols and "PERCENT" not in col]
    # Add Total back at the top
    crime_types.insert(0, "TOTAL IPC CRIMES")
    return jsonify(crime_types)

# -----------------------------
# Run app
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
