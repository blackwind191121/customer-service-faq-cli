import json
from pathlib import Path


INDEX_PATH = Path(__file__).resolve().parent / "faq_index.json"


def faq_index_exists():
    return INDEX_PATH.exists()


def load_faq_index():
    try:
        with INDEX_PATH.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_faq_index(index):
    with INDEX_PATH.open("w", encoding="utf-8") as file:
        json.dump(index, file, ensure_ascii=False)