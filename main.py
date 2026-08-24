from customer import show_all_faqs,search_faq,add_faq,remove_faq
# 主頁功能
MENU_OPTIONS=[
    ("1", "查詢 FAQ"),
    ("2", "查看所有 FAQ"),
    ("3", "新增 FAQ"),
    ("4", "刪除 FAQ"),
    ("5", "關於本程式"),
    ("0", "離開")
    ]
# 主頁視窗
def show_menu():
    print("主頁menu")
    for num,option in MENU_OPTIONS:
        print(f"{num}. {option}")
# 各選項功能
def main():
    while True:
        show_menu()
        user_choice = input("您要使用的功能:")
        try:
            user_choice = int(user_choice)
        except ValueError:
            print("請輸入正確的選項。")
            continue
        #查詢功能(客服用)
        if user_choice==1:
            print("進入 FAQ 查詢")
            user_question = input("您的問題是?")
            print(search_faq(user_question))
        #檢視所有問題
        elif user_choice==2:
            show_all_faqs()
        #新稱問題
        elif user_choice==3:
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
        #刪除問題
        elif user_choice==4:
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
        #系統說明
        elif user_choice==5:
            print("本系統為閱讀Json文檔後的概念客服系統，後續會添加AI來提升實用度 2026/08/24 開發者peng_wei_sung")
        #離開系統
        elif user_choice==0:
            break
        else:
            print('無效的選項')
        #詢問使用者是否繼續
        continue_menu=input("您是否繼續(Y/N)")
        if continue_menu == "N" or continue_menu =="n" or continue_menu=="0":
            break
        else:
            continue


if __name__ == "__main__":
  main()