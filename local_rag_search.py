#計算使用者問題的向量並與既有紀錄的向量進行比較
#tpo_k即是最多回傳幾個faq回去
def search_local_faqs(question,model,entries,faq_vectors,top_k=3):
    #檢查給予的數值、資料是否正確，不合理時拋出錯誤，結束函式
    if top_k < 1:
        raise ValueError("top_k 必須至少為 1")

    if not question.strip():
        raise ValueError("問題不能是空白")
    
    #沒有索引資料可搜尋時，直接回傳空清單
    if not entries:
        return []
    
    #計算使用者本次問題的向量長度
    question_vector = model.encode(
        question,
        normalize_embeddings=True,
    )
    #比較本次問題與其他faq向量之間的相似度
    scores = faq_vectors @ question_vector
    sorted_indices = scores.argsort()[::-1]

    #記錄已選過的FAQ ID，避免同一FAQ重複出現
    seen_faq_ids = set()
    #回傳的東西放這裡
    results = []

    # 按照相似度由高到低，逐一檢查候選問句
    for index in sorted_indices:
        index = int(index)
        entry = entries[index]
        faq_id = entry["faq_id"]

        if faq_id in seen_faq_ids:
            continue

        seen_faq_ids.add(faq_id)

        results.append({
            "faq_id": faq_id,
            "question": entry["question"],
            "score": float(scores[index]),
        })

        if len(results) >= top_k:
            break

    return results

# 將搜尋結果與 FAQ 資料結合，整理成AI回答時的參考內容
def build_faq_context(results, faqs):
    # 建立ID與FAQ的對照表，讓系統可以跟用ID直接查找
    faq_by_id = {}
    for faq in faqs:
        faq_by_id[faq["id"]] = faq
    context = []

    # 按照搜尋結果的順序，查找對應的 FAQ
    for result in results:
        faq = faq_by_id.get(result["faq_id"])

        # 如果 FAQ 已不存在，就跳過這筆結果
        if faq is None:
            continue

        # 結合搜尋命中的問句與 FAQ 中的主題、答案
        context.append({
            "faq_id": faq["id"],
            "topic": faq["topic"],
            "matched_question": result["question"],
            "answer": faq["answer"],
        })

    return context