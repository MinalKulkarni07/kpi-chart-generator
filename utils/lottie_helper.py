# utils/lottie_helper.py (or just lottie_helper.py)
import requests

def load_lottie_url(url: str):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception:
        return None
