from utils import load_faqs ,save_faq,delet_faq
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
    faqs=load_faqs()
    if delete_way == 1:
        existing_id ={faq["id"]for faq in faqs}
        if  user_delete not in existing_id:
            print('問題未找到，請重新尋找')
            return('do not find the question')
        for  faq in faqs:
            if faq["id"] == user_delete:
                print (faq)
                user_check =input("請問這是您要刪除的嗎?(Y/N)")
                if user_check == "Y" or user_check == "y":
                    delet_faq(faq)
                    print(faq,'刪除成功')
                    return('deldete success')    
                else:
                    print('取消刪除')
                    return('Undo deletion')
    elif delete_way == 2:
        for  faq in faqs:
            if user_delete in faq["questions"]:  
                print (faq)
                user_check =input("請問這是您要刪除的嗎?(Y/N)")
                if user_check == "Y" or user_check == "y":
                    delet_faq(faq)
                    print(faq,'刪除成功')
                    return('deldete success') 
                else:
                    print('取消刪除')
                    return('Undo deletion')
        print('問題未找到，請重新尋找')
        return('do not find the question')
    elif delete_way == 3 :
        for faq in faqs:
            for keyword in faq["keywords"]:
                if user_delete in keyword['keyword']:
                    print (faq)
                    user_check =input("請問這是您要刪除的嗎?(Y/N)")
                    if user_check == "Y" or user_check == "y":
                        delet_faq(faq)
                        print(faq,'刪除成功')
                        return('deldete success') 
                    else:
                        break
    
        print('問題未找到，請重新尋找')
        return('do not find the question')
                    
        