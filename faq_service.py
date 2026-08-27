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
    print(user_question)
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
        return "您的輸入無效請重新進入"
    return f'客服:{best_faq["answer"]}'


#新增FAQS
def add_faq(topic,questions,answer,keywords):
    faqs=load_faqs()
    new_id=get_next_faq_id(faqs)
    print(f'id:{new_id}\n topic:{topic}\n questions:{questions} \n answer:{answer} \n keyword:{keywords}')
    new_faq = {
        "id": new_id,
        "topic": topic,
        "questions" : questions,
        "answer" : answer,
        "keywords" : keywords
    }
    faqs.append(new_faq)
    save_faq(faqs)
    print(
        '更新成功',faqs,"已經更新到json中"
    )
    return(faqs)
#尋找空白ID
def get_next_faq_id(faqs):
    existing_id ={faq["id"]for faq in faqs}
    new_id = 1
    while new_id in existing_id:
        new_id +=1

    return new_id

def remove_faq(delete_way,user_delete):
    faq=find_faq(delete_way,user_delete)
    if faq == ('do not find the question'):
        return(faq)
    user_check =input("請問這是您要刪除的嗎?(Y/N)")
    if user_check == "Y" or user_check == "y":
        delet_faq(faq)
        print(faq,'刪除成功')
        return('deldete success')    
    else:
        print('取消刪除')
        return('Undo deletion')
                
def update_faq():
    while True:
        update_menu = [
        (1, "ID尋找"),
        (2, "問題尋找"),
        (3, "Keyword尋找"),
        (0, "離開(Exit)")
    ]
        print(update_menu)
        user_choice = input('您要如何選擇你要更新的方法')
        
        if user_choice == "1":
            user_update = input("請輸入您要的修改項目的ID:")
            try:
                user_update ==  int(user_update)
            except ValueError:
                continue
            
        elif user_choice == "2":
            user_update = input("請輸入您要的修改項目的問題是:")
        elif user_choice == "3":
            user_update = input("請輸入您要的修改項目的關鍵字是:")
        else:
            print("選項錯誤，請重新選擇")
            continue
        user_choice = int(user_choice)
        user_faq_choice=find_faq(user_choice,user_update)
        if user_faq_choice == "Value Error" or user_faq_choice == 'do not find the question':
            break
        update_back = Change_faq(user_faq_choice)
        sort_faqs_by_id()
        return(update_back)
        
        

def find_faq(find_way,Faq_project):
    faqs=load_faqs()
    if find_way == 1:
        try:
            Faq_project = int(Faq_project)
        except ValueError:
            print("Value Error，輸入錯誤")
            return("Value Error")
        existing_id ={faq["id"]for faq in faqs}
        if  Faq_project not in existing_id:
            print('問題未找到，請重新尋找')
            return('do not find the question')
        for  faq in faqs:
            if faq["id"] == Faq_project:
                print (faq)
                return(faq)
    elif find_way == 2:
        for  faq in faqs:
            if Faq_project in faq["questions"]:  
                print (faq)
                user_check =input("請問這是您要的項目嗎?(Y/N)")
                if user_check == "Y" or user_check == "y":
                    return(faq)
                else:
                    print('繼續尋找')
        print('問題未找到，請重新尋找')
        return('do not find the question')
    elif find_way == 3 :
        for faq in faqs:
            for keyword in faq["keywords"]:
                if Faq_project in keyword['keyword']:
                    print (faq)
                    user_check =input("請問這是您要的項目嗎?(Y/N)")
                    if user_check == "Y" or user_check == "y":
                        return(faq)
                    else:
                        break
    
        print('項目未找到，請重新尋找')
        return('do not find the question')