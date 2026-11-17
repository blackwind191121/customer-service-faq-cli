from faq_service import show_all_faqs,add_faq,remove_faq,update_faq,save_faq_revision
from faq_draft_service import generate_faq_draft, validate_faq_draft, generate_faq_revision
from errors import ChatModelError
from utils import load_faqs

function_menu=[
    (1, "檢視所有FAQ(View all FAQs)"),
    (2, "新稱新的FAQ(add new FAQ)"),
    (3,"刪除舊的FAQ(delete old FAQ)"),
    (4,"修改舊的FAQ(Revise old FAQ)"),
    (0, "離開(Exit)")
]
#開發者視窗
def show_menu():
    print("主頁menu")
    for num,option in function_menu:
        print(f"{num}. {option}")

def edit_faq_draft(draft):
    edited = draft.copy()

    # 問句是清單，必須另外複製，避免改到原始草稿。
    edited["questions"] = draft["questions"].copy()

    while True:
        print("\n目前草稿")
        print(f"標題：{edited['topic']}")

        print("可能問法：")
        for number, question in enumerate(edited["questions"], start=1):
            print(f"{number}. {question}")

        print(f"答案：{edited['answer']}")

        choice = input(
            "編輯草稿：1 修改標題、2 修改答案、3 修改問句、"
            "0 完成、/cancel 取消："
        ).strip()

        if choice == "/cancel":
            return None

        if choice == "0":
            try:
                return validate_faq_draft(edited)
            except ValueError as error:
                print(f"草稿尚未通過檢查：{error}")
                print("請修正後再完成編輯。")
                continue

        if choice == "3":
            number_text = input(
                "請輸入要修改的問句編號（0 返回編輯選單）："
            ).strip()

            if number_text == "0":
                continue

            try:
                number = int(number_text)
            except ValueError:
                print("問句編號必須是整數。")
                continue

            if not 1 <= number <= len(edited["questions"]):
                print("沒有這個問句編號。")
                continue

            new_question = input(
                "請輸入新問句（直接 Enter 保留原內容）："
            ).strip()

            if not new_question:
                continue

            edited["questions"][number - 1] = new_question
            continue

        if choice == "1":
            field = "topic"
            label = "標題"
        elif choice == "2":
            field = "answer"
            label = "答案"
        else:
            print("請輸入 1、2、3、0 或 /cancel。")
            continue

        new_text = input(
            f"請輸入新{label}（直接 Enter 保留原內容）："
        ).strip()

        if not new_text:
            continue

        edited[field] = new_text

def preview_faq_draft():
    policy_text = input("請輸入政策內容（0 取消）：").strip()

    if policy_text == "0":
        return

    if not policy_text:
        print("政策內容不能是空白。")
        return

    print("正在產生 FAQ 草稿，請稍候……")

    try:
        draft = generate_faq_draft(policy_text)
    except ChatModelError as error:
        print(f"模型服務發生問題：{error}")
        return
    except ValueError as error:
        print(f"無法產生有效草稿：{error}")
        return

    if draft is None:
        print("模型判斷目前資料不足，請補充更明確的政策內容。")
        return

    print("\nFAQ 草稿（尚未儲存）")
    print(f"標題：{draft['topic']}")

    print("可能問法：")
    for number, question in enumerate(draft["questions"], start=1):
        print(f"{number}. {question}")

    print(f"答案：{draft['answer']}")

    draft = edit_faq_draft(draft)

    if draft is None:
        print("已取消，草稿未儲存。")
        return

    print("\n請確認修改後的答案仍符合政策，且能回答上方的問句。")
    print("接著可補充關鍵字與權重，最後確認是否儲存。")

    keywords = []

    while True:
        keyword = input(
            "請輸入關鍵字（0 完成，/cancel 取消整份草稿）："
        ).strip()

        if keyword == "/cancel":
            print("已取消，草稿未儲存。")
            return

        if keyword == "0":
            break

        if not keyword:
            print("關鍵字不能是空白。")
            continue

        if any(item["keyword"] == keyword for item in keywords):
            print("這個關鍵字已經輸入過。")
            continue

        while True:
            weight_text = input("請輸入關鍵字權重（整數）：").strip()

            try:
                weight = int(weight_text)
            except ValueError:
                print("權重必須是整數，請重新輸入。")
                continue

            break

        keywords.append({
            "keyword": keyword,
            "weight": weight,
        })

    print("\n本次新增的關鍵字：")

    if keywords:
        for item in keywords:
            print(f"- {item['keyword']}：權重 {item['weight']}")
    else:
        print("未設定關鍵字；這筆 FAQ 可用於向量搜尋，但不會由關鍵字搜尋命中。")

    while True:
        confirm = input(
            "確認上述草稿與關鍵字正確，並新增到正式 FAQ？(Y/N)："
        ).strip().upper()

        if confirm in ("Y", "N"):
            break

        print("請輸入 Y 或 N。")

    if confirm == "N":
        print("已取消，草稿未儲存。")
        return

    new_faq = add_faq(
        topic=draft["topic"],
        questions=draft["questions"],
        answer=draft["answer"],
        keywords=keywords,
    )

    print(f"FAQ 已新增，ID：{new_faq['id']}，標題：{new_faq['topic']}")

def preview_faq_revision():
    faqs = load_faqs()
    if not faqs:
        print("目前沒有可修改的 FAQ。")
        return

    for faq in faqs:
        print(f"{faq['id']}. {faq['topic']}")

    while True:
        id_text = input("請輸入要修改的 FAQ ID（0 取消）：").strip()
        if id_text == "0":
            return
        try:
            faq_id = int(id_text)
        except ValueError:
            print("FAQ ID 必須是整數。")
            continue

        original = next((faq for faq in faqs if faq["id"] == faq_id), None)
        if original is not None:
            break
        print("找不到這個 FAQ ID，請重新輸入。")

    print(f"\n原始標題：{original['topic']}")
    for number, question in enumerate(original["questions"], start=1):
        print(f"{number}. {question}")
    print(f"原始答案：{original['answer']}")
    policy_change = input("請輸入政策變更（0 取消）：").strip()
    if policy_change == "0":
        return

    try:
        if not policy_change:
            raise ValueError("政策變更不能是空白")
        print("正在產生修改草稿，請稍候……")
        draft = generate_faq_revision(original, policy_change)
    except ChatModelError as error:
        print(f"模型服務發生問題：{error}")
        return
    except ValueError as error:
        print(f"無法產生有效草稿：{error}")
        return

    if draft is None:
        print("模型無法判斷如何修改，請補充更明確的政策變更。")
        return

    draft = edit_faq_draft(draft)
    if draft is None:
        print("已取消，原始 FAQ 未更新。")
        return

    # 最終確認前列出完整前後內容，避免只確認模型最初的版本。
    for label, content in (("修改前", original), ("修改後", draft)):
        print(f"\n{label}")
        print(f"標題：{content['topic']}")
        for number, question in enumerate(content["questions"], start=1):
            print(f"{number}. {question}")
        print(f"答案：{content['answer']}")
    print(f"FAQ ID 保持 {original['id']}，原有關鍵字與權重也會保留。")
    print("請確認修改後內容符合政策，且答案能回答每個問句。")

    while True:
        confirm = input("確認更新這筆 FAQ？(Y/N)：").strip().upper()
        if confirm in ("Y", "N"):
            break
        print("請輸入 Y 或 N。")
    if confirm == "N":
        print("已取消，原始 FAQ 未更新。")
        return

    try:
        updated = save_faq_revision(original, draft)
    except ValueError as error:
        print(f"無法更新 FAQ：{error}")
        return
    print(f"FAQ 已更新，ID：{updated['id']}，標題：{updated['topic']}")


#開發者主程式
def admin_main():
    while True:
        show_menu()
        admin_choice = input('請選擇您要使用的功能: ')
        try:
            admin_choice = int(admin_choice)
        except ValueError:
            print('錯誤輸入，請重新使用')
            continue
        if admin_choice == 1:
            show_all_faqs()
        elif admin_choice == 2:
            while True:
                use_ai = input(
                    "是否使用 AI 輔助產生 FAQ 草稿？(Y/N)："
                ).strip().upper()

                if use_ai in ("Y", "N"):
                    break

                print("請輸入 Y 或 N。")

            if use_ai == "Y":
                preview_faq_draft()
                continue

            user_add_topic = input("您要新增 FAQ 的標題是：")
            user_add_question = []
            
            while True:
                question = input("請輸入可能問法，輸入 0 完成：")
                if question == "0":
                    break
                user_add_question.append(question)
            user_add_answer = input("你要新增FAQ的回答是:")
            user_add_keyword = []
            while True:
                keywords = input("請輸入關鍵字，每輸入一個按下enter，完畢後，輸入 0 完成：")
                if keywords == "0":
                    break
                else:
                    while True:
                        keywords_weight =input("請輸入關鍵字權重:")
                        try:
                            keywords_weight = int(keywords_weight)
                        except ValueError:
                            print("請重新輸入")
                            continue
                        break
                    new_keyword ={"keyword":keywords,"weight":keywords_weight}
                user_add_keyword.append(new_keyword)
            new_faq = add_faq(user_add_topic,user_add_question,user_add_answer,user_add_keyword)
            print(f"""id(編號):{new_faq["id"]}
主題(topic):{new_faq["topic"]}  """)
        elif admin_choice == 3:
            while True:
                user_delete_way=input(
                    "您打算如何查找您要刪除的選項:" \
                    "1.ID 2.問題 3.關鍵字" \
                    "(請輸入數字):" )
                try:
                    user_delete_way = int(user_delete_way)
                except ValueError:
                    print("請重新輸入")
                    continue
                user_delete_faq = input("請輸入你想刪除的faq:")
                if user_delete_way == 1:
                    try:
                        user_delete_faq =int(user_delete_faq)
                    except ValueError:
                        print("您的輸入有錯")
                        continue
                    remove_back=remove_faq(user_delete_way,user_delete_faq)
                else:
                    remove_back=remove_faq(user_delete_way,user_delete_faq)
                if remove_back is None:
                    continue
                if remove_back == 'delete success':
                    print("刪除成功")
                elif remove_back == 'Undo deletion':
                    print("刪除取消")
                break
        elif admin_choice == 4:
            while True:
                use_ai = input("是否使用 AI 輔助修改 FAQ？(Y/N)：").strip().upper()
                if use_ai in ("Y", "N"):
                    break
                print("請輸入 Y 或 N。")
            if use_ai == "Y":
                preview_faq_revision()
            else:
                update_faq()
        elif admin_choice == 0:
            break
        else:
            print("您的輸入錯誤")
        admin_continue = input("是否繼續使用(Y/N)")
        if admin_continue not in('Y' , "y"):
            return("user come back")
