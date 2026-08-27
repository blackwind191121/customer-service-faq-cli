import json
from arrange_faq import load_faqs
#建立讀取faq函數
def load_faqs():
    #開啟faq文件
    with open("faq.json", "r", encoding="utf-8") as faq_file:
    # 在這裡操作 faq_file
        faqs = json.load(faq_file)
        return faqs
    
#存取新faq進JSON
def save_faq(faqs):
    with open("faq.json", "w", encoding="utf-8") as faq_file:
        json.dump(faqs,faq_file, ensure_ascii=False,indent=2)

#刪除Faqs
def delet_faq(faq):
    faqs =load_faqs()
    faqs.remove(faq)
    save_faq(faqs)

def Change_faq(faq):
    faqs =load_faqs()
    print("要刪除的 faq：", faq)
    print("faq 的型別：", type(faq))
    print("faq 的 ID：", faq.get("id") if isinstance(faq, dict) else "不是 dict")
    print("要刪除的 faq：", faq)
    print("目前 faqs：", faqs)
    faqs.remove(faq)
    Change_menu = [
            (1, "ID(編號)"),
            (2, "topic(主題)"),
            (3, "questions(問題)"),
            (4, "answer(回答)"),
            (5, "keywords(關鍵字與權重)"),
            (0, "Exit(離開))")
        ]
    while True:
        for changes in Change_menu:
            print(changes)
        user_change = input("您希望修改的項目:(1-5)")
        try:
            user_change = int(user_change)
        except ValueError:
            print("錯誤輸入，請重新嘗試")
            continue
        if user_change == 1:
            print("ID 不可修改")
            continue
        elif user_change == 2:
            print (faq["topic"])
        elif user_change == 3:
            print (faq["questions"])
        elif user_change == 4:
            print (faq["answer"])   
        elif user_change == 5:
            print (faq["keywords"])  
        elif user_change == 0:
            faqs.append(faq)
            save_faq(faqs)
            return(faq)
        else:
            print('錯誤輸入，請重新嘗試')
            continue
        user_chack = input("這是您希望修改的內容嗎?(Y/N)")
        if user_chack not in ("y","Y"):
            print('修改取消')
            continue
        
        if user_change not in (3,5):
            user_change_input= input('請輸入您想修改的內容')
            if user_change == 2:
                faq["topic"] = user_change_input
                continue
            elif user_change == 4:
                faq["answer"] = user_change_input
                continue
        else:
            while True:
                change_way=[
                    (1, "add(新增)"),
                    (2, "rewrit(重寫)"),
                    (0, "Exit(離開)")
                ]
                print(change_way)
                user_choice = input("您選擇如何處理:")
                if user_choice == "1":
                    if user_change == 3:
                        user_add_questions =[]
                        while True:
                            user_add_questions = faq["questions"]
                            questions = input("請輸入關鍵字，每輸入一個按下enter，完畢後，輸入 0 完成：")
                            if questions == "0":
                                break
                            user_add_questions.append(questions)
                        faq["questions"] = user_add_questions
                        continue
                    else:
                        user_add_keyword = []
                        while True:
                            user_add_keyword = faq["keywords"] 
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
                        faq["keywords"] = user_add_keyword
                        continue
                elif user_choice == "2":
                        if user_change == 3:
                            user_add_questions =[]
                            while True:
                                questions = input("請輸入關鍵字，每輸入一個按下enter，完畢後，輸入 0 完成：")
                                if questions == "0":
                                    break
                                user_add_questions.append(questions)
                            faq["questions"] = user_add_questions

                            continue
                        else:
                            user_add_keyword = []
                            while True:
                                user_add_keyword = faq["keywords"] 
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
                            faq["keywords"] = user_add_keyword

                            continue
                elif user_choice == "0":
                    break
                else:
                    print('錯誤輸入')
                    continue
            faqs.append(faq)
            save_faq(faqs)
            print(
                    '更新成功',faqs,"已經更新到json中"
                )
            load_faqs()
            return(faq)

            