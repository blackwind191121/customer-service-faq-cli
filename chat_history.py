import json
from openai import OpenAI
from utils import load_faqs
import os
def load_chat_SQL():
    try:
        with open("chat_history.json","r",encoding="utf-8") as chat_file:
            chats = json.load(chat_file)
            return chats
    except FileNotFoundError:
        return [{"id":1 ,"name":"尚未建立聊天室"}]

def create_chat(client,ai_model,user_question):
    chats=load_chat_SQL()
    chat_history =json.dumps(
        chats,
        ensure_ascii= False,
        indent=2
    )
    existing_id = {chat["id"] for chat in chats}
   
    next_id = 1
    while next_id in existing_id:
        next_id+=1
    faq = load_faqs()

    faq_text = json.dumps(
        faq,
        ensure_ascii= False,
        indent=2
    )
    
    prompt = prompt = f"""
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
    - 只能根據提供的 FAQ 回答
    - 如果資訊不足，要明確告知資訊不足，請客戶以電子郵件的方式，詢問真人客服
    - 不要自行編造企業政策
    

    使用者問題：
    {user_question}

    企業 FAQ：
    {faq_text}

    """

    response = client.responses.create(
        model= ai_model,
        input=prompt,
        text ={
            "format":{
                "type" : "json_schema",
                "name" : "new_chat_response",
                "strict" : True,
                "schema":{
                    "type" :"object",
                    "properties" :{"chat_name":{"type":"string"},"answer" : {"type":"string"}},
                    "required" : ["chat_name","answer"],
                    "additionalProperties": False
                }
            }
        }
         
     )
    result = json.loads(response.output_text)
    chat_name =result["chat_name"]
    answer = result["answer"]
    new_chat ={
        "id":next_id,
        "name":chat_name
    }
    name_id = 0
    existing_name = {chat["name"] for chat in chats}
    old_name = chat_name
    while chat_name in existing_name:
        chat_name = old_name
        chat_name = f"{chat_name}_{name_id}"
        name_id +=1
    invalid_chars = '\\/:*?"<>|'
    for char in invalid_chars:
        chat_name = chat_name.replace(char, "_")
    chat_name = chat_name.strip()
    chat_name = chat_name.strip(". ")
    chats.append(new_chat)
    chat = [
        {
        "id" :1,
        "question" :user_question,
        "AI_reply" : answer
        }
    ]
    print(answer)
    with open("chat_history.json","w",encoding="utf-8") as chat_file:
        json.dump(chats,chat_file,ensure_ascii=False,indent=2)
    with open(f"{chat_name}.json","w",encoding="utf-8") as chat_file:
        json.dump(chat,chat_file,ensure_ascii=False,indent=2)
    return chat_name

def load_chat(chat_name):
    with open(f"{chat_name}.json","r",encoding="utf-8") as chat_file:
        chat = json.load(chat_file)
        return chat

def load_chat_Summary(chat_name):
    try:
        with open(f"{chat_name}_Summary.json","r",encoding="utf-8") as chat_file:
            chats_Summary = json.load(chat_file)
            return chats_Summary
    except FileNotFoundError:
        return {
            "id":0,
            "summary":"尚未任何摘要"}