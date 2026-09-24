import numpy as np
from sentence_transformers import SentenceTransformer
from local_rag_store import load_local_index,save_local_index
from local_rag_search import search_local_faqs, build_faq_context
from utils import load_faqs

#RAG使用的計算向量的模型
DEFAULT_MODEL_NAME = "BAAI/bge-small-zh-v1.5"
# 載入本地索引與模型，準備搜尋資源，並支援沒有問句的空索引
def load_local_rag():
    # 讀取已儲存的本地索引
    index_data = load_local_index()

    # 索引檔案不存在時，指出原因並中止本次載入
    if index_data is None:
        index_data = {"model_name": DEFAULT_MODEL_NAME,"normalized": True,"entries": []}
        
    # 確認索引記錄的模型名稱與目前設定一致，避免混用不同模型的向量
    if index_data.get("model_name") != DEFAULT_MODEL_NAME:
        raise ValueError("索引模型與目前設定不同，請使用對應模型或重新建立索引" )

    # 確認索引標記為已正規化，才能沿用內積計算餘弦相似度的搜尋方式
    if index_data.get("normalized") is not True:
        raise ValueError("目前搜尋需要正規化向量，請重新建立正規化索引")
    
    # 取出問句索引；清單可能有資料，也可能是空清單
    entries = index_data["entries"]

    # 根據索引記錄的名稱載入模型，供後續計算問題與新增問句的向量
    model = SentenceTransformer(
        index_data["model_name"],
        device="cpu",
    )

    # 從模型取得輸出向量的維度，避免在程式中寫死為 512
    dimension = model.get_embedding_dimension()

    # 索引有資料時，按照問句順序收集已儲存的向量
    if entries:
        vectors = []
        for entry in entries:
            vectors.append(entry["embedding"])

        # 將向量清單轉成 NumPy 陣列，方便計算相似度
        faq_vectors = np.array(vectors, dtype=np.float32)
        # 預期向量陣列的形狀為「問句數量 × 模型輸出的向量維度」
        # 例如 29 個問句，每個向量 512 維，預期形狀就是 (29, 512)
        expected_shape = (len(entries), dimension)

        # 確認實際陣列的筆數與維度符合預期，不符合時中止載入
        if faq_vectors.shape != expected_shape:
            raise ValueError(
                f"索引向量形狀錯誤：預期 {expected_shape}，"
                f"實際為 {faq_vectors.shape}"
            )
        # 逐一檢查向量中的數值是否有限，排除 NaN、正無限大與負無限大
        # all() 要求所有數值都符合條件，只要有一個不符合就拋出錯誤
        if not np.isfinite(faq_vectors).all():
            raise ValueError("索引向量包含 NaN 或無限大")

        # 計算每一列向量的長度，axis=1 表示沿著每個問句的向量維度計算
        norms = np.linalg.norm(faq_vectors, axis=1)

        # 確認所有向量長度都接近 1，符合正規化向量的要求，容許微小誤差，是因為浮點數運算不一定得到精確的 1
        if not np.allclose(norms, 1.0, rtol=0, atol=1e-4):
            raise ValueError("索引向量未正規化，長度應接近 1")
    
    else:
        # 沒有問句時，建立「0 筆資料 × 模型向量維度」的空陣列
        faq_vectors = np.empty((0, dimension),dtype=np.float32)

    # 將模型名稱、模型物件、問句索引與向量陣列一起回傳
    return {"model_name": index_data["model_name"],"model": model,"entries": entries,"faq_vectors": faq_vectors,}

# 搜尋相關 FAQ，並結合目前的 FAQ 資料，回傳 AI 回答用的參考內容
def retrieve_faq_context(question, rag, top_k=3):
    if not question.strip():
        raise ValueError("問題不能是空白")

    if top_k < 1:
        raise ValueError("top_k 必須至少為 1")

    # 本次只讀取一次 FAQ。
    faqs = load_faqs()

    # 先讓索引與這份FAQ一致。
    refresh_local_rag(rag, faqs=faqs)

    # 使用更新後的索引搜尋。
    results = search_local_faqs(
        question=question,
        model=rag["model"],
        entries=rag["entries"],
        faq_vectors=rag["faq_vectors"],
        top_k=top_k
    )

    # 使用同一份 FAQ 取得答案。
    return build_faq_context(results, faqs)

# 比較目前 FAQ 與既有索引的問句，找出需要新增或移除的項目
def compare_faq_questions(faqs, entries):
    current_questions = set()

    # 將目前 FAQ 的每個問句整理成 (FAQ ID, 問句) 配對，方便比較與查重
    for faq in faqs:
        for question in faq["questions"]:
            current_questions.add((faq["id"], question))

    indexed_questions = set()

    # 將已建立索引的問句整理成相同格式
    for entry in entries:
        indexed_questions.add(
            (entry["faq_id"], entry["question"])
        )

    # 目前 FAQ 有，但索引沒有：需要建立向量的問句
    added = current_questions - indexed_questions

    # 索引有，但目前 FAQ 沒有：需要從索引移除的問句
    removed = indexed_questions - current_questions

    # 回傳差異，這裡只做比較，不會計算向量或修改檔案
    return {
        "added": added,
        "removed": removed,
    }

# 移除已不在目前 FAQ 中的問句索引，保留其餘資料與原有向量
def keep_current_entries(entries, removed):
    kept_entries = []

    for entry in entries:
        # 使用 FAQ ID 與問句組成配對，對照待移除的項目
        key = (entry["faq_id"], entry["question"])

        # 若這筆索引需要移除，就跳過，不加入保留清單
        if key in removed:
            continue

        # 保留整筆索引資料，包含已計算好的向量
        kept_entries.append(entry)

    return kept_entries

# 只為新增或修改後的問句計算向量，建立新的索引資料
def build_added_entries(added, model):
    # 沒有新增問句時，直接回傳空清單，不呼叫模型
    if not added:
        return []

    # 將集合排序成清單，固定順序，方便問句與向量一一對應
    added_items = sorted(added)
    questions = []

    # 從 (FAQ ID, 問句) 配對中取出問句，準備交給模型
    for faq_id, question in added_items:
        questions.append(question)

    # 一次計算所有新增問句的向量，並正規化
    vectors = model.encode(questions,normalize_embeddings=True)
    new_entries = []

    # 按照相同順序，將每筆問句資料與計算出的向量配對
    for item, vector in zip(added_items, vectors):
        faq_id, question = item

        # 將向量轉成 Python 清單，方便後續儲存為 JSON
        new_entries.append({"faq_id": faq_id,"question": question,"embedding": vector.tolist()})
    return new_entries

# 根據目前 FAQ 同步問句索引，保留舊向量並補上新增問句的向量
def sync_faq_entries(faqs, entries, model):
    # 比較目前 FAQ 與既有索引，找出新增及移除的問句
    changes = compare_faq_questions(faqs, entries)

    # 排除需要移除的索引，其餘資料與向量繼續保留
    kept_entries = keep_current_entries(entries,changes["removed"])

    # 只為新增的問句計算向量，建立新索引
    new_entries = build_added_entries(changes["added"],model)

    # 合併保留的舊索引與新增索引
    updated_entries = kept_entries + new_entries

    # 回傳更新後的索引，以及本次新增、移除的問句筆數
    return {"entries": updated_entries,"added_count": len(new_entries),"removed_count": len(entries) - len(kept_entries)}

# 根據目前 FAQ 更新本地索引，同步儲存檔案與記憶體中的搜尋資料
def refresh_local_rag(rag, faqs=None):
    if faqs is None:
        faqs = load_faqs()

    # 保留有效的舊向量、移除已經失效的問句，並計算新增問句的向量
    result = sync_faq_entries(faqs,rag["entries"],rag["model"])

    # 問句沒有變動時，直接回傳結果，不重寫索引或更新向量陣列
    if result["added_count"] == 0 and result["removed_count"] == 0:
        return result

    # 取得同步後的完整問句索引
    updated_entries = result["entries"]

    # 按照更新後的索引順序，收集每個問句的向量
    vectors = []
    for entry in updated_entries:
        vectors.append(entry["embedding"])

    # 取得原本每個向量的維度
    dimension = rag["faq_vectors"].shape[1]

    # 將向量轉成 NumPy 陣列，形狀設定為「問句數量 × 向量維度」
    # 即使全部問句被刪除，也能建立形狀為 (0, dimension) 的空陣列
    updated_vectors = np.array(
        vectors,
        dtype=np.float32,
    ).reshape(len(updated_entries), dimension)

    # 整理要儲存的索引，記錄模型名稱、正規化設定與問句向量
    index_data = {
        "model_name": rag["model_name"],
        "normalized": True,
        "entries": updated_entries
    }

    # 先將更新後的索引寫入檔案，供下次啟動時讀取
    # 若寫入失敗並拋出錯誤，後面的記憶體更新不會執行
    save_local_index(index_data)

    # 更新目前程式使用的索引與向量，讓後續搜尋使用最新資料
    # 直接修改傳入的 rag 字典，持有同一個字典的呼叫端也會看到變動
    rag["entries"] = updated_entries
    rag["faq_vectors"] = updated_vectors

    # 回傳同步後的索引，以及新增與移除的筆數
    return result