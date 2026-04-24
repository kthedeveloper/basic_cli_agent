import json
import os

import requests


def get_weather(city: str) -> dict:
    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={
            "name": city,
            "count": 1,
            "language": "ru",
            "format": "json",
        },
        timeout=10,
    )

    geo.raise_for_status()
    geo_data = geo.json()

    results = geo_data.get("results", [])

    if not results:
        return {"error": f"Город '{city}' не найден"}

    place = results[0]

    lat = place["latitude"]
    lon = place["longitude"]
    name = place["name"]
    country = place.get("country", "")

    weather = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "current_weather": True,
        },
        timeout=10,
    )

    weather.raise_for_status()
    weather_data = weather.json()

    current = weather_data["current_weather"]

    return {
        "city": name,
        "country": country,
        "temperature": current["temperature"],
        "windspeed": current["windspeed"],
        "weathercode": current["weathercode"],
    }

def save_note(text: str) -> dict:
    path = "notes.json"

    notes = []

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            notes = json.load(f)

    notes.append(text)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(notes, f, ensure_ascii=False, indent=2)

    return {"status": "saved", text: text}

def list_notes() -> dict:
    path = "notes.json"

    if not os.path.exists(path):
        return {"notes": []}

    with open(path, "r", encoding="utf-8") as f:
        notes = json.load(f)

    return {"notes": notes}