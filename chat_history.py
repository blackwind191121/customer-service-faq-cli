import json
from openai import OpenAI
from utils import load_faqs
import os
from local_llm_service import generate_local_answer
from data_paths import CHAT_HISTORY_PATH, ensure_data_dirs,get_chat_path,get_summary_path


def load_chat_SQL():
    try:
        with CHAT_HISTORY_PATH.open("r", encoding="utf-8") as chat_file:
            return json.load(chat_file)
    except FileNotFoundError:
        return []

def create_chat(client, ai_model, user_question, faq_context, provider="openai"):
    chats=load_chat_SQL()
    chat_history =json.dumps(chats,ensure_ascii= False,indent=2)
    existing_id = {chat["id"] for chat in chats}
   
    next_id = 1
    while next_id in existing_id:
        next_id+=1
    faq_text = json.dumps(faq_context,ensure_ascii=False,indent=2)
    
    prompt = f"""
    請根據以下使用者問題與企業 FAQ 完成三件事：

    1. 產生一個簡短的聊天室名稱。
    2. 根據 FAQ 回答使用者的問題。


    聊天室名稱規則：
    - 使用繁體中文
    - 約 4～12 個中文字
    - 不包含 .json
    - 不使用 \\ / : * ? " < > | 等檔名特殊字元
    - 不可與{chat_history}中的檔案名稱有所重複

    回答規則：
    - 企業政策只能依據提供的 FAQ。
    - FAQ 是候選資料，排名第一不代表一定適用。
    - 請依使用者的意思選擇相關政策。
    - 如果 FAQ 為空或資訊不足，請明確說明無法確認，必要時追問。
    - 不要自行編造企業政策、聯絡方式或已完成的操作。
    - 使用自然、簡潔的繁體中文回答。
    

    使用者問題：
    {user_question}

    企業 FAQ：
    {faq_text}

    """
    # 根據模型來源，使用本地模型或 OpenAI 產生首次回答
    if provider == "local":
        result = {
            # 去除問題前後空白，取前 12 個字元作為聊天室名稱
            "chat_name": user_question.strip()[:12],

            # 將使用者問題與候選 FAQ 交給指定的本地模型回答
            "answer": generate_local_answer(
                user_question,
                faq_context,
                model_name=ai_model,
            ),
        }

    elif provider == "openai":
        # 呼叫 OpenAI，透過提示詞產生聊天室名稱與首次回答
        response = client.responses.create(
            model=ai_model,
            input=prompt,
            text={
                "format": {
                    # 指定使用 JSON Schema 定義回傳資料的格式
                    "type": "json_schema",
                    "name": "new_chat_response",
                    "strict": True,
                    "schema": {
                        # 回傳資料必須是物件，包含兩個字串欄位
                        "type": "object",
                        "properties": {
                            "chat_name": {"type": "string"},
                            "answer": {"type": "string"},
                        },

                        # 兩個欄位都必須提供，且不可加入其他欄位
                        "required": ["chat_name", "answer"],
                        "additionalProperties": False,
                    },
                },
            },
        )

        # 將模型回傳的 JSON 文字轉成 Python 字典
        result = json.loads(response.output_text)

    else:
        # 模型來源不在支援範圍時，指出原因並中止執行
        raise ValueError(f"不支援的模型來源：{provider}")

    # 兩種來源都整理成相同的字典格式，後續統一取出回答
    answer = result["answer"]
    # 先清理模型提供的名稱。
    base_name = result["chat_name"]

    invalid_chars = '\\/:*?"<>|'
    for char in invalid_chars:
        base_name = base_name.replace(char, "_")

    base_name = base_name.strip().strip(". ")

    if not base_name:
        base_name = "聊天室"

    # 加上固定前綴，避免直接使用 Windows 保留名稱。
    base_name = f"chat_{base_name}"

    # 清理後才檢查重複，也檢查硬碟上是否已有同名檔案。
    existing_names = {chat["name"] for chat in chats}
    chat_name = base_name
    suffix = 1

    while (chat_name in existing_names or get_chat_path(chat_name).exists() or get_summary_path(chat_name).exists()):
        chat_name = f"{base_name}_{suffix}"
        suffix += 1

    # 名稱確定後，才建立清單紀錄。
    new_chat = {"id": next_id,"name": chat_name}

    # 將新聊天室資料加入聊天室清單
    chats.append(new_chat)

    # 建立新聊天室的第一輪對話紀錄
    chat = [{"id": 1,"question": user_question,"AI_reply": answer}]
    print(answer)

    # 儲存聊天室清單，方便之後列出與選擇聊天室。
    ensure_data_dirs()
    with CHAT_HISTORY_PATH.open("w", encoding="utf-8") as chat_file:
        json.dump(chats, chat_file, ensure_ascii=False, indent=2)

    # 將第一輪對話存入 data/chats/ 下的聊天室檔案。
    with get_chat_path(chat_name).open("w", encoding="utf-8") as chat_file:
        json.dump(chat, chat_file, ensure_ascii=False, indent=2)

    # 回傳聊天室名稱，供後續讀取紀錄與繼續對話
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