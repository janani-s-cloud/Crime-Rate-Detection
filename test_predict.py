import requests
import json

base_url = "http://127.0.0.1:5000"

def get_states():
    try:
        response = requests.get(f"{base_url}/api/states")
        return response.json()
    except Exception as e:
        print(f"Error getting states: {e}")
        return []

def get_districts(state):
    try:
        response = requests.get(f"{base_url}/api/districts?state={state}")
        return response.json()
    except Exception as e:
        print(f"Error getting districts for {state}: {e}")
        return []

def test_prediction(state, district):
    url = f"{base_url}/predict"
    data = {
        "year": 2025,
        "state": state,
        "district": district
    }
    try:
        response = requests.post(url, data=data)
        if "Predicted Crime Growth Rate" in response.text:
            return True
        else:
            print(f"FAILURE for {state}, {district}")
            # check if it is a specific error
            if "Error:" in response.text:
                print(f"Server returned error: {response.text.split('<h4>')[1].split('</h4>')[0]}")
            return False
    except Exception as e:
        print(f"Request failed for {state}, {district}: {e}")
        return False

states = get_states()
print(f"Found {len(states)} states.")

failures = 0
successes = 0

# Test first 3 districts of each state to save time
for state in states:
    districts = get_districts(state)
    print(f"Testing {state} ({len(districts)} districts)...")
    for district in districts[:3]: 
        if test_prediction(state, district):
            successes += 1
        else:
            failures += 1

print(f"\nTest Complete. Successes: {successes}, Failures: {failures}")
