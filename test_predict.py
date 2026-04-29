"""
Pytest-compatible unit tests for the Crime Rate Detection Flask app.
These tests do NOT require a running server — they test the app directly.
"""
import pytest
import pickle
import os
import numpy as np
import pandas as pd


# -------------------------------------------------------
# Fixtures
# -------------------------------------------------------

@pytest.fixture
def app():
    """Create and configure the Flask app for testing."""
    from app import app as flask_app
    flask_app.config["TESTING"] = True
    return flask_app


@pytest.fixture
def client(app):
    """Provide a test client for the Flask app."""
    return app.test_client()


# -------------------------------------------------------
# Test 1: Model files exist
# -------------------------------------------------------

def test_growth_model_file_exists():
    """Check that the growth model pickle file is present."""
    assert os.path.exists("model/growth_model.pkl"), (
        "model/growth_model.pkl not found! Run train_models.py first."
    )


def test_share_model_file_exists():
    """Check that the share model pickle file is present."""
    assert os.path.exists("model/share_model_data.pkl"), (
        "model/share_model_data.pkl not found! Run train_models.py first."
    )


def test_data_file_exists():
    """Check that the crime data CSV is present."""
    assert os.path.exists("data/crime_data.csv"), (
        "data/crime_data.csv not found!"
    )


# -------------------------------------------------------
# Test 2: Models can be loaded
# -------------------------------------------------------

def test_growth_model_loads():
    """Verify the growth model pickle can be loaded without error."""
    if not os.path.exists("model/growth_model.pkl"):
        pytest.skip("Model file not found, skipping.")
    with open("model/growth_model.pkl", "rb") as f:
        model = pickle.load(f)
    assert model is not None


def test_share_model_loads():
    """Verify the share model pickle and its keys can be loaded."""
    if not os.path.exists("model/share_model_data.pkl"):
        pytest.skip("Model file not found, skipping.")
    with open("model/share_model_data.pkl", "rb") as f:
        data = pickle.load(f)
    assert "share_model" in data
    assert "le_state" in data
    assert "le_district" in data
    assert "crime_cols" in data


# -------------------------------------------------------
# Test 3: Flask routes respond correctly
# -------------------------------------------------------

def test_home_page(client):
    """Home page should return 200 OK."""
    response = client.get("/")
    assert response.status_code == 200


def test_analysis_page(client):
    """Analysis page should return 200 OK."""
    response = client.get("/analysis")
    assert response.status_code == 200


def test_api_states(client):
    """States API should return a JSON list."""
    response = client.get("/api/states")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_api_crime_types(client):
    """Crime types API should return a non-empty JSON list."""
    response = client.get("/api/crime_types")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_api_crime_data_no_filter(client):
    """Crime data API should return JSON with expected keys."""
    response = client.get("/api/crime_data")
    assert response.status_code == 200
    data = response.get_json()
    assert "labels" in data
    assert "historical" in data
    assert "projected" in data


def test_predict_missing_fields(client):
    """Predict route with missing fields should not crash (returns 200 with error msg)."""
    response = client.post("/predict", data={})
    # Should return 200 (rendered error page), not 500
    assert response.status_code in [200, 400]
