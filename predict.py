import os

import numpy as np
import pandas as pd
import requests
from joblib import load

# 🔐 API KEY from environment
API_KEY = os.environ.get("API_KEY")

if not API_KEY:
    raise ValueError("API_KEY not found. Set environment variable.")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

model = load(os.path.join(BASE_DIR, 'models/model.pkl'))
scaler = load(os.path.join(BASE_DIR, 'models/scaler.pkl'))
encoder = load(os.path.join(BASE_DIR, 'models/label_encoder.pkl'))


# 🌍 Get weather using lat/lon
def get_weather_by_coords(lat, lon):
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
        res = requests.get(url).json()

        if str(res.get("cod")) != "200":
            return None, None, None

        return (
            res['main']['temp'],
            res['main']['humidity'],
            res.get('rain', {}).get('1h', 50)
        )

    except:
        return None, None, None


# 🌍 Reverse Geocoding (lat/lon → place)
def get_place_name(lat, lon):
    try:
        url = f"https://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={API_KEY}"
        res = requests.get(url).json()

        if not res:
            return "Unknown Location"

        name = res[0].get("name", "")
        state = res[0].get("state", "")
        country = res[0].get("country", "")

        return f"{name}, {state}, {country}"

    except:
        return "Unknown Location"


# 🌍 Convert place → lat/lon
def get_coords(place):
    try:
        url = f"https://api.openweathermap.org/geo/1.0/direct?q={place}&limit=1&appid={API_KEY}"
        res = requests.get(url).json()

        if not res:
            return None, None

        return res[0]['lat'], res[0]['lon']

    except:
        return None, None


# 🌾 Crop translations
crop_lang = {
    "rice": {"en":"Rice","te":"బియ్యం","hi":"चावल"},
    "maize": {"en":"Maize","te":"మొక్కజొన్న","hi":"मक्का"},
    "chickpea": {"en":"Chickpea","te":"సెనగ","hi":"चना"},
    "kidneybeans": {"en":"Kidney Beans","te":"చిక్కుడు","hi":"राजमा"},
    "pigeonpeas": {"en":"Pigeon Peas","te":"కందులు","hi":"अरहर"},
    "mothbeans": {"en":"Moth Beans","te":"కుంకుమపేసలు","hi":"मोठ"},
    "mungbean": {"en":"Mung Bean","te":"పెసలు","hi":"मूंग"},
    "blackgram": {"en":"Black Gram","te":"మినుములు","hi":"उड़द"},
    "lentil": {"en":"Lentil","te":"మసూర్","hi":"मसूर"},
    "pomegranate": {"en":"Pomegranate","te":"దానిమ్మ","hi":"अनार"},
    "banana": {"en":"Banana","te":"అరటి","hi":"केला"},
    "mango": {"en":"Mango","te":"మామిడి","hi":"आम"},
    "grapes": {"en":"Grapes","te":"ద్రాక్ష","hi":"अंगूर"},
    "watermelon": {"en":"Watermelon","te":"పుచ్చకాయ","hi":"तरबूज"},
    "muskmelon": {"en":"Muskmelon","te":"ఖర్బుజా","hi":"खरबूजा"},
    "apple": {"en":"Apple","te":"ఆపిల్","hi":"सेब"},
    "orange": {"en":"Orange","te":"నారింజ","hi":"संतरा"},
    "papaya": {"en":"Papaya","te":"బొప్పాయి","hi":"पपीता"},
    "coconut": {"en":"Coconut","te":"కొబ్బరి","hi":"नारियल"},
    "cotton": {"en":"Cotton","te":"పత్తి","hi":"कपास"},
    "jute": {"en":"Jute","te":"జూట్","hi":"जूट"},
    "coffee": {"en":"Coffee","te":"కాఫీ","hi":"कॉफी"}
}


# 🧪 Fertilizer suggestions
fert_lang = {
    "en": {"N":"Add Nitrogen fertilizer","P":"Add Phosphorus fertilizer","K":"Add Potassium fertilizer","ok":"Soil balanced"},
    "te": {"N":"నైట్రోజన్ ఎరువు వేయండి","P":"ఫాస్పరస్ ఎరువు వేయండి","K":"పొటాషియం ఎరువు వేయండి","ok":"మట్టి సమతుల్యం"},
    "hi": {"N":"नाइट्रोजन डालें","P":"फॉस्फोरस डालें","K":"पोटैशियम डालें","ok":"मिट्टी संतुलित है"}
}


def fertilizer(data, lang):
    if data['N'] < 50:
        return fert_lang[lang]["N"]
    elif data['P'] < 50:
        return fert_lang[lang]["P"]
    elif data['K'] < 50:
        return fert_lang[lang]["K"]
    return fert_lang[lang]["ok"]


# 🚀 MAIN FUNCTION
def predict_crop(data):

    lang = data.get("lang", "en")

    # 📍 GPS Mode
    if "lat" in data and "lon" in data:

        lat = data["lat"]
        lon = data["lon"]

        temp, humidity, rainfall = get_weather_by_coords(lat, lon)

        place_name = get_place_name(lat, lon)
        data["place_name"] = place_name


    # 🌍 Place Mode
    elif "place" in data and data["place"]:

        lat, lon = get_coords(data["place"])

        if lat is None:
            return {"error": "Location not found"}

        temp, humidity, rainfall = get_weather_by_coords(lat, lon)

        place_name = get_place_name(lat, lon)
        data["place_name"] = place_name


    # ✍️ Manual Mode
    else:

        temp = data['temperature']
        humidity = data['humidity']
        rainfall = data['rainfall']

        data["place_name"] = "Manual Input"


    # ❌ If weather fails
    if temp is None:
        return {"error": "Weather API failed"}


    data['temperature'] = temp
    data['humidity'] = humidity
    data['rainfall'] = rainfall

    data.setdefault('N', 50)
    data.setdefault('P', 40)
    data.setdefault('K', 40)
    data.setdefault('ph', 6)


    # 📊 Model prediction
    features = pd.DataFrame([{
        "N": data['N'],
        "P": data['P'],
        "K": data['K'],
        "temperature": data['temperature'],
        "humidity": data['humidity'],
        "ph": data['ph'],
        "rainfall": data['rainfall']
    }])

    scaled = scaler.transform(features)
    probs = model.predict_proba(scaled)[0]

    top3 = np.argsort(probs)[-3:][::-1]

    results = []

    for i in top3:
        crop = encoder.inverse_transform([i])[0].lower()
        name = crop_lang.get(crop, {}).get(lang, crop)

        results.append({
            "name": name,
            "prob": round(probs[i] * 100, 2)
        })


    # 🎯 FINAL RESPONSE
    return {
        "top": results,
        "fertilizer": fertilizer(data, lang),
        "location": data.get("place_name", "N/A"),
        "temperature": round(data['temperature'], 2),
        "humidity": data['humidity']
    }