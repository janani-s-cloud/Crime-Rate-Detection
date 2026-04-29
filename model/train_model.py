# model/train_model.py

# Import required libraries
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import pickle

# 1. Load dataset
data = pd.read_csv("data/crime_data.csv")

# 2. Select required columns (simple model)
# NOTE: Column names must match your CSV exactly
df = data[["YEAR", "MURDER", "RAPE", "THEFT"]]

# 3. Create TOTAL_CRIME column
df["TOTAL_CRIME"] = df["MURDER"] + df["RAPE"] + df["THEFT"]

# 4. Features (X) and Target (y)
X = df[["YEAR"]]
y = df["TOTAL_CRIME"]

# 5. Train-test split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 6. Train model
model = LinearRegression()
model.fit(X_train, y_train)

# 7. Save model
with open("crime_model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model trained and saved as crime_model.pkl")
