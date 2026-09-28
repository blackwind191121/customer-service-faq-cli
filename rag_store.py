import json
from data_paths import CLOUD_INDEX_PATH, ensure_data_dirs

INDEX_PATH = CLOUD_INDEX_PATH


def faq_index_exists():
    return INDEX_PATH.exists()


def load_faq_index():
    try:
        with INDEX_PATH.open("r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []


def save_faq_index(index):
    # 確保 data/indexes/ 存在，才能在裡面建立檔案。
    ensure_data_dirs()

    with INDEX_PATH.open("w", encoding="utf-8") as file:
        json.dump(index, file, ensure_ascii=False)