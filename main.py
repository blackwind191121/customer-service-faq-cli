from customer import service_ai
from admin import admin_main
from arrange_faq import load_faqs
# 主頁功能
MENU_OPTIONS=[
    (1, "Customer(顧客)"),
    (2, "Admin(員工)"),
    (0, "Exit(離開)")
    ]
# 主頁視窗
def show_menu():
    print("主頁menu")
    for num,option in MENU_OPTIONS:
        print(f"{num}. {option}")
# 各選項功能
def main():
    load_faqs()
    while True:
        show_menu()
        user_choice = input("您的身分是:")
        try:
            user_choice = int(user_choice)
        except ValueError:
            print("請輸入正確的選項。")
            continue
        #查詢功能(客服用)
        if user_choice==1:
            while True:
                print("進入顧客專區")
                user_question = input('您好，我是客服小劉，您的問題是?')
                service_ai(user_question)
                user_continue = input("是否繼續使用(Y/N)")
                if user_continue not in('Y' , "y"):
                    break
        #檢視所有問題
        elif user_choice==2:

            admin_main()
            
        #離開系統
        elif user_choice==0:
            break
        else:
            print('無效的選項')
    


if __name__ == "__main__":
  main()