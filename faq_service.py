from utils import load_faqs ,save_faq,delet_faq,Change_faq
from arrange_faq import sort_faqs_by_id
#展示所有FAQS
def show_all_faqs():
    faqs = load_faqs()
    print("以下是所有FAQ")
    for faq in faqs:
        print(f'{faq["id"]} . {faq["topic"]}')

#查找FAQS
def search_faq(user_question):
    Customer_reply=[]
    faqs=load_faqs()
    best_score=0
    best_faq=None
    for faq in faqs:
        score=0
        for keyword in faq["keywords"]:
            if keyword["keyword"] in user_question:
                score += keyword["weight"]
        Customer_reply.append((faq,score))
    for faq,score in Customer_reply:
        if best_score<score:
            best_score=score
            best_faq=faq
    if best_score == 0:
        return None
    return best_faq["answer"]


#新增FAQS
def add_faq(topic,questions,answer,keywords):
    faqs=load_faqs()
    new_id=get_next_faq_id(faqs)
    new_faq = {
        "id": new_id,
        "topic": topic,
        "questions" : questions,
        "answer" : answer,
        "keywords" : keywords
    }
    faqs.append(new_faq)
    save_faq(faqs)
    return new_faq

#尋找空白ID
def get_next_faq_id(faqs):
    existing_id ={faq["id"]for faq in faqs}
    new_id = 1
    while new_id in existing_id:
        new_id +=1

    return new_id

#刪除Faq
def remove_faq(delete_way, user_delete):
    result = find_faq(delete_way, user_delete)

    if result is None or result == "invalid_id" or result == "invalid_find_way":
        print("問題未找到，請重新尋找")
        return None

    # find_way == 1 的情況，result 直接是單一 faq
    if isinstance(result, dict):
        candidates = [result]
    else:
        candidates = result  # find_way == 2 或 3，是 list

    if len(candidates) == 0:
        print("問題未找到，請重新尋找")
        return None

    for faq in candidates:
        print(faq)
        user_check = input("請問這是您要刪除的嗎?(Y/N)")
        if user_check in ("Y", "y"):
            delet_faq(faq)
            print(faq, "刪除成功")
            return "delete success"

    return "Undo deletion"

#更新Faq  
def update_faq():
    update_menu = [
        (1, "ID尋找"),
        (2, "問題尋找"),
        (3, "Keyword尋找"),
        (0, "離開(Exit)")
    ]
    while True:
        print(update_menu)
        user_choice = input('您要如何選擇你要更新的方法:')

        if user_choice not in ("1", "2", "3"):
            print("選項錯誤，請重新選擇")
            continue

        if user_choice == "1":
            user_update = input("請輸入您要的修改項目的ID:")
        elif user_choice == "2":
            user_update = input("請輸入您要的修改項目的問題是:")
        elif user_choice == "3":
            user_update = input("請輸入您要的修改項目的關鍵字是:")

        user_choice = int(user_choice)
        result = find_faq(user_choice, user_update)

        if result is None or result == "invalid_id" or result == "invalid_find_way":
            print("問題未找到，請重新尋找")
            continue

        # find_way == 1 時 result 直接是單一 faq；2、3 時是 list
        if isinstance(result, dict):
            candidates = [result]
        else:
            candidates = result

        if len(candidates) == 0:
            print("問題未找到，請重新尋找")
            continue

        selected_faq = None
        for faq in candidates:
            print(faq)
            user_check = input("請問這是您要修改的項目嗎?(Y/N)")
            if user_check in ("Y", "y"):
                selected_faq = faq
                break

        if selected_faq is None:
            print("未選擇任何項目，請重新尋找")
            continue

        update_back = Change_faq(selected_faq)
        sort_faqs_by_id()
        return update_back



#查找FAQS 
def find_faq(find_way, Faq_project):
    faqs = load_faqs()

    if find_way == 1:
        try:
            Faq_project = int(Faq_project)
        except ValueError:
            return "invalid_id"
        for faq in faqs:
            if faq["id"] == Faq_project:
                return faq
        return None

    elif find_way == 2:
        matches = [faq for faq in faqs if Faq_project in faq["questions"]]
        return matches

    elif find_way == 3:
        matches = []
        for faq in faqs:
            for keyword in faq["keywords"]:
                if Faq_project in keyword["keyword"]:
                    matches.append(faq)
                    break  
        return matches

    else:
        return "invalid_find_way"