from openai import OpenAI
from utils import load_faqs
import json
from chat_history import load_chat_SQL,create_chat,load_chat,load_chat_Summary
from AI_env import get_Openai_api_config
AI_platform = [
    (1, "OpenAI(ChatGPT)"),
]


def ai_choice():
    chats = load_chat_SQL()
    while True:
        for AI_choice in AI_platform:
            print (AI_choice)
        user_choice = input("您要使用哪個平台?" )
        if user_choice == "1":
            API_information = get_Openai_api_config()
            chat_create = input ("您是否需要新開一個聊天室(Y/N)")
        else:
            print("輸入錯誤，請重新嘗試")
            continue
        if chat_create not in ("Y" ,"y"):
            while True:
                if chats == []:
                    print("尚未建立聊天室")
                    chat_name ="Y"
                else:
                    chat_ids = [chat["id"] for chat in chats]
                    for chat in chats:
                        print(chat)
                    chat_id= input("您要使用哪個聊天室，請輸入id(如果想要開啟新的聊天室，請輸入0)")
                    try:
                        chat_id = int(chat_id)
                    except ValueError:
                        print("輸入錯誤請重新輸入")
                        continue
                if chat_id == "0":
                    chat_create = "Y"
                    break
                elif chat_id not in chat_ids:
                    print("輸入錯誤請重新輸入")
                    continue
                user_question = input('我是客服小劉，您的問題?')
                for item in chats:
                    if item["id"] == chat_id:
                        chat_name = item["name"]
                        break
                
                talk_all(API_information["key"],API_information["model"],chat_name,user_question)
                break
        if  chat_create in ("Y" ,"y"):
            user_question = input('我是客服小劉，您的問題?')
            API_key = API_information["key"]
            API_model = API_information["model"]
            chat_name = create_chat(API_key,API_model,user_question)

        while True:
            user_question = input('您還有其他問題嗎(沒有請輸入0)?')
            if user_question == "0":
                break
            talk_all(API_information["key"],API_information["model"],chat_name,user_question)


    

def talk_all(api_key,APImodel,chat_name,user_question):
    
    faq = load_faqs()

    chats_summary = load_chat_Summary(chat_name)        
    faq_text = json.dumps(
        faq,
        ensure_ascii= False,
        indent=2
    )
    chat = load_chat(chat_name)
    existing_id = {chat_id["id"] for chat_id in chat}
    next_id = 1
    while next_id in existing_id:
        next_id+=1
    this_round = chats_summary["id"]
    recnt_chat = chat[this_round:]
    chat_talk = json.dumps(
        recnt_chat,
        ensure_ascii= False,
        indent=2
    )

    prompt = f"""
    請根據我給你的FAQ問題與對應回答來回答我下面的問題
    且內容要去結合您與客戶之間的聊天紀錄，清楚了解對方的需求
    使用者的問題:{user_question}
    客服的問答資料集{faq_text}
    您與客戶之間的最近六輪對話紀錄{chat_talk}
    您與客戶之間的對話摘要{chats_summary}
    回答規則：
    - 只能根據提供的 FAQ 回答
    - 如果 FAQ 資訊不足，要明確告知資訊不足
    - 不要自行編造企業政策
    
    """
    response = api_key.responses.create(
        model = APImodel,
        input = prompt,
        stream= True
    )
    ai_answer = ""
    for event in response:
        if event.type == "response.output_text.delta":
            print(event.delta, end="", flush=True)
            ai_answer += event.delta
    print()


    chat_information = {
        "id": next_id,
        "question" :user_question,
        "AI_reply" : ai_answer
    }
    chat.append(chat_information)
    with open(f"{chat_name}.json", "w", encoding="utf-8") as chat_file:
        json.dump(chat,chat_file,ensure_ascii=False,indent=2)

    if next_id%6 == 0:
        prompt =f"""
        請根據我給你的對話紀錄，幫我整理出你們對話的重點摘要。
        過去的對話摘要{chats_summary}
        您與客戶之間的對話紀錄{chat_talk}
        本論與使用者之間的對話紀錄{chat_information}
        回答規則：
        - 只能根據提供的對話紀錄
        - 不可以針對回答與使用者的問題，編造不存在的企業政策與對應方案
        - 不要自行編造企業政策
        - 摘要不可以超過30個字
        - 在30字外，如果使用者有提及過商品名稱、客戶本身的名字、客戶喜歡的對話風格、客戶的要求等，可以做為額外要求記錄下來
    """
        response = api_key.responses.create(
                model = APImodel,
                input = prompt,
            )
        summary_response ={
            "id": next_id,
            "summary":response.output_text
        }
        with open(f"{chat_name}_Summary.json", "w", encoding="utf-8") as chat_file:
            json.dump(summary_response,chat_file,ensure_ascii=False,indent=2)

