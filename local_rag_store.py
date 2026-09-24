import json
from pathlib import Path

# 本地向量索引的儲存位置
INDEX_PATH = Path(__file__).resolve().parent / "faq_index_local.json"

# 將索引寫入 JSON，覆蓋原本內容
def save_local_index(index):
    with INDEX_PATH.open("w", encoding="utf-8") as file:
        json.dump(index, file, ensure_ascii=False)

# 讀取本地索引，檔案不存在時回傳 None
def load_local_index():
    if not INDEX_PATH.exists():
        return None

    with INDEX_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)

