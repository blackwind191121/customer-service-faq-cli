from openai import OpenAI
from dotenv import load_dotenv
from utils import load_faqs
from rag_store import (faq_index_exists,load_faq_index,save_faq_index)
#呼叫AI計算向量
def get_embedding(text):
    load_dotenv()
    # 会自动去讀取環境變數，採用.env 進行管理
    client = OpenAI()  
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

#建立FAQ中每個問答的向量
def build_faq_index(faqs):
    index = []
    for faq in faqs:
        for question in faq["questions"]:
            embedding = get_embedding(question)
            index.append({
                "faq_id": faq["id"],
                "question": question,
                "embedding": embedding
            })
    return index


    
#找出尚未建立向量的 FAQ 問句。
def find_missing_questions(faqs, index):
    
    existing_questions = {
        (item["faq_id"], item["question"])
        for item in index
        if item.get("embedding")
    }

    missing_questions = []

    for faq in faqs:
        for question in faq["questions"]:
            key = (faq["id"], question)

            if key not in existing_questions:
                missing_questions.append({
                    "faq_id": faq["id"],
                    "question": question,
                })
                existing_questions.add(key)

    return missing_questions

def ensure_faq_index():
    #存取舊的Faq文件    
    faqs = load_faqs()
    #嘗試尋找舊RAG文件
    old_index = load_faq_index()
    # 原始 FAQ 目前仍存在的問句。
    current_questions = {
        (faq["id"], question)
        for faq in faqs
        for question in faq["questions"]
    }

    # 移除已刪除的問句，以及沒有向量的項目。
    index = [
        item
        for item in old_index
        if (item["faq_id"], item["question"]) in current_questions
        and item.get("embedding")
    ]

    missing_questions = find_missing_questions(faqs, index)

    for item in missing_questions:
        embedding = get_embedding(item["question"])

        index.append({
            "faq_id": item["faq_id"],
            "question": item["question"],
            "embedding": embedding,
        })

    # 有變動才寫檔；首次啟動即使 FAQ 為空也建立檔案。
    if index != old_index or not faq_index_exists():
        save_faq_index(index)

    return index

#開啟系統時，計算整個FAQ的RAG向量
if __name__ == "__main__":
    index = ensure_faq_index()
    print(f"目前共有 {len(index)} 筆問句向量")
        

    
