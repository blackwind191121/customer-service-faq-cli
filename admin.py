from faq_service import show_all_faqs,add_faq,remove_faq,update_faq

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
            user_add_topic = input("您要新贈FAQ的標題是:")
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
            add_faq(user_add_topic,user_add_question,user_add_answer,user_add_keyword)
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
                if remove_back == 'do not find the question':
                    continue
                break
        elif admin_choice == 4:
            update_faq()
        elif admin_choice == 0:
            break
        else:
            print("您的輸入錯誤")
        admin_continue = input("是否繼續使用(Y/N)")
        if admin_continue not in('Y' , "y"):
            return("user come back")