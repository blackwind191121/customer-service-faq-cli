from chat_history import load_chat_SQL,create_chat,load_chat,load_chat_Summary
from AI_env import get_Openai_api_config
from local_rag_service import retrieve_faq_context
from local_llm_service import generate_local_recap, LocalModelError
from chat_service import answer_stream
from errors import ChatModelError

# 可選擇的 AI 平台
AI_platform = [
    (1, "OpenAI(ChatGPT)"),
    (2, "本地模型(Qwen3 8B)"),
]


# CLI 選擇 AI 平台，建立或繼續聊天室
def ai_choice(rag):
    

    while True:
        chats = load_chat_SQL()
        # 顯示平台選單，取得 API 用戶端與模型設定
        for AI_choice in AI_platform:
            print(AI_choice)

        user_choice = input("您要使用哪個平台?")

        if user_choice == "1":
            provider = "openai"
            API_information = get_Openai_api_config()
            
        elif user_choice == "2":
            provider = "local"
            API_information = {"key": None,"model": "qwen3:8b"}
        else:
            print("輸入錯誤，請重新嘗試")
            continue
        chat_create = input("您是否需要新開一個聊天室(Y/N)")

        # 使用者不建立新聊天室時，選擇既有聊天室
        if chat_create not in ("Y", "y"):
            while True:
                if chats == []:
                    print("尚未建立聊天室")
                    chat_create = "Y"
                    break
                    # 待修正：此分支沒有設定後面會用到的 chat_id、chat_ids
                else:
                    chat_ids = [chat["id"] for chat in chats]

                    for chat in chats:
                        print(chat)

                    chat_id = input(
                        "您要使用哪個聊天室，請輸入id"
                        "(如果想要開啟新的聊天室，請輸入0)"
                    )

                    try:
                        chat_id = int(chat_id)
                    except ValueError:
                        print("輸入錯誤請重新輸入")
                        continue

                # 待修正：chat_id 已轉成整數，應與整數 0 比較
                if chat_id == 0:
                    chat_create = "Y"
                    break
                elif chat_id not in chat_ids:
                    print("輸入錯誤請重新輸入")
                    continue

                 # 根據選擇的 ID，取得聊天室名稱。
                for item in chats:
                    if item["id"] == chat_id:
                        chat_name = item["name"]
                        break

                # 離開聊天室選擇迴圈。
                break

        # 建立新聊天室，取得聊天室名稱
        if chat_create in ("Y", "y"):
            while True:
                user_question = input("我是客服小劉，您的問題？（0 離開）").strip()
                if user_question == "0":
                    return
                if not user_question:
                    print("請輸入問題。")
                    continue

                if user_question.lower() == "/recap":
                    print("新聊天室還沒有對話，請先提出問題。")
                    continue
                break
            API_key = API_information["key"]
            API_model = API_information["model"]

            faq_context = retrieve_faq_context(user_question, rag)

            try:
                chat_name = create_chat(API_key,API_model,user_question,faq_context,provider)

            except ChatModelError as error:
                print(f"\n無法建立聊天室：{error}")
                print("請確認模型服務後，再重新選擇平台。")
                continue
         # 在目前聊天室持續對話。
        while True:
            user_question = input(
                "請輸入問題（/recap 回顧對話，0 離開）："
            ).strip()

            if user_question == "0":
                return

            if not user_question:
                print("請輸入問題。")
                continue

            # 指令先處理，不進入 FAQ 搜尋與問答儲存。
            if user_question.lower() == "/recap":
                if provider == "local":
                    try:
                        recap = recap_local_chat(
                            chat_name,
                            model_name=API_information["model"],
                        )
                        print(recap)

                    except LocalModelError as error:
                        print(f"回顧失敗：{error}")
                else:
                    print("目前 /recap 僅支援本地模型模式。")

                continue

            # 一般問題才搜尋 FAQ 並產生回答。
            faq_context = retrieve_faq_context(user_question, rag)

            try:
                talk_all(API_information["key"],API_information["model"],chat_name,user_question,faq_context=faq_context,provider=provider)

            except ChatModelError as error:
                print(f"\n本次回答失敗：{error}")
                print("這次問題尚未存入對話紀錄，服務恢復後可重新輸入。")
                continue


# 呼叫 AI 串流 API，逐段回傳新增的回答文字
# api_key 在這裡實際上是 OpenAI 用戶端物件，不是金鑰字串
def generate_answer(api_key, APImodel, prompt):
    response = api_key.responses.create(
        model=APImodel,
        input=prompt,
        stream=True,
    )

    # 串流包含不同事件，只取出新增文字的事件
    for event in response:
        if event.type == "response.output_text.delta":
            yield event.delta


# CLI 客服對話：呼叫共用的 answer_stream，逐段印出回答
def talk_all(api_key, APImodel, chat_name, user_question, faq_context, provider="openai"):
    for chunk in answer_stream(client=api_key,model=APImodel,provider=provider,chat_name=chat_name,question=user_question,faq_context=faq_context):
        print(chunk, end="", flush=True)
    print()


def recap_local_chat(chat_name, model_name="qwen3:8b"):
    # 讀取已儲存的摘要與完整對話。
    chat_summary = load_chat_Summary(chat_name)
    chat = load_chat(chat_name)

    # 取得摘要已涵蓋到的對話 ID。
    summary_id = chat_summary.get("id", 0)

    # 只補上摘要尚未涵蓋的對話。
    recent_chat = []
    for turn in chat:
        if turn["id"] > summary_id:
            recent_chat.append(turn)

    # 交給回顧模型，回傳文字。
    return generate_local_recap(
        chat_summary=chat_summary,
        recent_chat=recent_chat,
        model_name=model_name,
    )