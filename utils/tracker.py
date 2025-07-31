import requests

def log_to_google_sheets(event, page, user_info="anonymous", notes=""):
    url = "https://script.google.com/macros/s/AKfycbwXo2emErt44h50gEcoLgQJwRZYduk7Y-fe5J_cL7tbta1LHeWhbrKhLCNjIrdbkMUH7g/exec"
    payload = {
        "event": event,
        "page": page,
        "user_info": user_info,
        "notes": notes,
    }
    try:
        requests.post(url, json=payload, timeout=3)
    except Exception as e:
        print("Logging failed:", e)

def get_user_location():
    try:
        response = requests.get("https://ipinfo.io/json", timeout=3)
        if response.status_code == 200:
            data = response.json()
            city = data.get("city", "")
            region = data.get("region", "")
            country = data.get("country", "")
            return f"{city}, {region}, {country}"
    except:
        pass
    return "Unknown"
