import json

from data_paths import CHAT_HISTORY_PATH, get_chat_path,get_summary_path
from chat_service import answer_stream

def load_chat_SQL():
    try:
        with CHAT_HISTORY_PATH.open("r", encoding="utf-8") as chat_file:
            return json.load(chat_file)
    except FileNotFoundError:
        return []

# 根據第一個問題產生未使用的聊天室名稱，不建立檔案。
def build_chat_name(user_question):
    chats = load_chat_SQL()
    base_name = user_question.strip()[:12]

    # 將不適合當檔名的字元替換成底線。
    invalid_chars = '\\/:*?"<>|'
    for char in base_name:
        if char in invalid_chars or ord(char) < 32:
            base_name = base_name.replace(char, "_")

    base_name = base_name.strip(". ")

    if not base_name:
        base_name = "聊天室"

    base_name = f"chat_{base_name}"
    existing_names = {chat["name"] for chat in chats}

    chat_name = base_name
    suffix = 1

    while (
        chat_name in existing_names
        or get_chat_path(chat_name).exists()
        or get_summary_path(chat_name).exists()
    ):
        chat_name = f"{base_name}_{suffix}"
        suffix += 1

    return chat_name

def create_chat(client, ai_model, user_question, faq_context, provider="openai"):
    question = user_question.strip()

    if not question:
        raise ValueError("問題不能是空白")

    chat_name = build_chat_name(question)

    for chunk in answer_stream(
        client=client,
        model=ai_model,
        provider=provider,
        chat_name=chat_name,
        question=question,
        faq_context=faq_context,
    ):
        print(chunk, end="", flush=True)

    print()
    return chat_name

# 根據聊天室名稱，讀取完整的對話紀錄
def load_chat(chat_name):
    # 從固定的聊天室資料夾讀取對話。
    with get_chat_path(chat_name).open("r", encoding="utf-8") as chat_file:
        chat = json.load(chat_file)

    return chat


# 讀取聊天室摘要，若尚未建立摘要檔案則回傳初始資料
def load_chat_Summary(chat_name):
    try:
        # 從固定的聊天室資料夾讀取摘要。
        with get_summary_path(chat_name).open("r", encoding="utf-8") as chat_file:
            chats_summary = json.load(chat_file)

        return chats_summary

    except FileNotFoundError:
        # 新聊天室可能尚未產生摘要。
        return {
            "id": 0,
            "summary": "尚未有任何摘要",
        }