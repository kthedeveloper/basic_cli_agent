import json
from pathlib import Path

from langchain_core.tools import tool
from pydantic import BaseModel, Field

NOTES_FILE = Path("notes.json")


class WeatherInput(BaseModel):
    city: str = Field(description="Название города, например: Москва, София, Лондон")


class SaveNoteInput(BaseModel):
    text: str = Field(description="Текст заметки, который нужно сохранить")


@tool(args_schema=WeatherInput)
def get_weather(city: str) -> str:
    """Возвращает текущую погоду в указанном городе."""
    weather_data = {
        "москва": "Облачно, +5°C",
        "софия": "Солнечно, +18°C",
        "лондон": "Дождь, +8°C",
    }
    return weather_data.get(city.lower(), f"Данных о погоде для города '{city}' нет.")


@tool(args_schema=SaveNoteInput)
def save_note(text: str) -> str:
    """Сохраняет текстовую заметку пользователя в локальный JSON-файл."""
    notes = []

    if NOTES_FILE.exists():
        with NOTES_FILE.open("r", encoding="utf-8") as file:
            notes = json.load(file)

    notes.append(text)

    with NOTES_FILE.open("w", encoding="utf-8") as file:
        json.dump(notes, file, ensure_ascii=False, indent=2)

    return "Заметка сохранена."


@tool
def list_notes() -> str:
    """Возвращает список всех сохранённых заметок пользователя."""
    if not NOTES_FILE.exists():
        return "Заметок пока нет."

    with NOTES_FILE.open("r", encoding="utf-8") as file:
        notes = json.load(file)

    if not notes:
        return "Заметок пока нет."

    return "\n".join(f"{index}. {note}" for index, note in enumerate(notes, start=1))