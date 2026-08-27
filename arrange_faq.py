import json
#專門整理json檔案的
def sort_faqs_by_id():
    faqs = load_faqs()
    faqs.sort(key=lambda faq: faq["id"])
    with open("faq.json", "w", encoding="utf-8") as faq_file:
        json.dump(faqs,faq_file, ensure_ascii=False,indent=2)
    return(faqs)
#讀取檔案
def load_faqs():
    #開啟faq文件
    with open("faq.json", "r", encoding="utf-8") as faq_file:
    # 在這裡操作 faq_file
        faqs = json.load(faq_file)
        return faqs