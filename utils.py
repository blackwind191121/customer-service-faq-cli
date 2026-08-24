import json


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