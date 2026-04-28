import requests

BASE_URL = "https://oracleapex.com/ords/zahraa_individual_assignment/myapi"

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 Firefox/149.0"
}

def fetch_credit_limit_data():
    response = requests.get(f"{BASE_URL}/credit_limit", headers=HEADERS, timeout=30)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        print(f"Credit limit fetch failed. Status: {response.status_code}")
        return []

def fetch_average_order_data():
    response = requests.get(f"{BASE_URL}/average_order_value", headers=HEADERS, timeout=30)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        print(f"Average order fetch failed. Status: {response.status_code}")
        return []