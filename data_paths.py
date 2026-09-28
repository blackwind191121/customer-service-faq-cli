from pathlib import Path


# 以這個程式檔的位置，找到專案根目錄。
BASE_DIR = Path(__file__).resolve().parent

# 各類資料的固定資料夾。
DATA_DIR = BASE_DIR / "data"
CHATS_DIR = DATA_DIR / "chats"
INDEXES_DIR = DATA_DIR / "indexes"

# 固定檔案的完整路徑。
FAQ_PATH = DATA_DIR / "faq.json"
CHAT_HISTORY_PATH = DATA_DIR / "chat_history.json"
LOCAL_INDEX_PATH = INDEXES_DIR / "faq_index_local.json"
CLOUD_INDEX_PATH = INDEXES_DIR / "faq_index.json"

#建立資料目錄；已存在時不會清空或覆蓋內容。
def ensure_data_dirs():
    CHATS_DIR.mkdir(parents=True, exist_ok=True)
    INDEXES_DIR.mkdir(parents=True, exist_ok=True)

#取得聊天室對話檔案的路徑。
def get_chat_path(chat_name):
    return CHATS_DIR / f"{chat_name}.json"

#取得聊天室摘要檔案的路徑。
def get_summary_path(chat_name):
    return CHATS_DIR / f"{chat_name}_Summary.json"