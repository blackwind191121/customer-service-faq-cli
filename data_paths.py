from pathlib import Path
import ntpath

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

# 驗證聊天室名稱；不合法時直接中止。
def validate_chat_name(chat_name):
    if not isinstance(chat_name, str):
        raise ValueError("聊天室名稱必須是文字")

    if not chat_name.strip():
        raise ValueError("聊天室名稱不能是空白")

    if "/" in chat_name or "\\" in chat_name:
        raise ValueError("聊天室名稱不能包含路徑分隔符號")

    if ntpath.isreserved(chat_name):
        raise ValueError("聊天室名稱包含 Windows 不允許的字元或保留名稱")

    return chat_name


# 取得聊天室對話檔案的路徑。
def get_chat_path(chat_name):
    chat_name = validate_chat_name(chat_name)
    return CHATS_DIR / f"{chat_name}.json"


# 取得聊天室摘要檔案的路徑。
def get_summary_path(chat_name):
    chat_name = validate_chat_name(chat_name)
    return CHATS_DIR / f"{chat_name}_Summary.json"