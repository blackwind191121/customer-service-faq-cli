from faq_service import find_faq,add_faq,search_faq,remove_faq


FAKE_FAQS = [
    {"id": 1, "topic": "退貨政策",
    "questions": ["可以退貨嗎"], 
    "answer": "七天內可退貨", 
    "keywords": [
    {"keyword": "退貨", "weight": 3}, 
    {"keyword": "退回", "weight": 2}, 
    {"keyword": "買錯", "weight": 2}, 
    {"keyword": "不要了", "weight": 1}, 
    {"keyword": "不想要", "weight": 1}]},
    {"id": 2, 
    "topic": "出貨時間", 
    "questions": ["多久出貨"], 
    "answer": "三個工作天", 
    "keywords":  [
      {"keyword": "出貨","weight": 3},
      {"keyword": "寄出","weight": 2},
      {"keyword": "多久出貨","weight": 3},
      {"keyword": "出貨時間","weight": 3},
      {"keyword": "什麼時候寄","weight": 2}
    ]},
]
#正確ID輸入
def test_find_faq_by_id_found(monkeypatch):
    def fake_load_faqs():
        return FAKE_FAQS

    monkeypatch.setattr("faq_service.load_faqs", fake_load_faqs)
    result = find_faq(1, 1)
    assert result == FAKE_FAQS[0]

#錯誤不存在ID輸入
def test_find_faq_by_wrongid_found(monkeypatch):
    def fake_load_faqs():
        return FAKE_FAQS
    monkeypatch.setattr("faq_service.load_faqs", fake_load_faqs)
    result = find_faq(1,3)
    assert result is None

#id尋找錯誤格式
def test_find_faq_by_wronginput_id_found(monkeypatch):
    def fake_load_faqs():
        return FAKE_FAQS
    monkeypatch.setattr("faq_service.load_faqs", fake_load_faqs)
    result = find_faq(1,"abc")
    assert result == "invalid_id"

#正確問題輸入
def test_find_faq_by_question_found(monkeypatch):
    def fake_load_faqs():
        return FAKE_FAQS
    monkeypatch.setattr("faq_service.load_faqs", fake_load_faqs)
    result = find_faq(2,"可以退貨嗎")
    assert result == [FAKE_FAQS[0]]

#錯誤問題輸入
def test_find_faq_by_wrongquestion_found(monkeypatch):
    def fake_load_faqs():
        return FAKE_FAQS
    monkeypatch.setattr("faq_service.load_faqs", fake_load_faqs)
    result = find_faq(2,"我心情不太好")
    assert result == []

#正確關鍵字輸入
def test_find_faq_by_keyword_found(monkeypatch):
    def fake_load_faqs():
        return FAKE_FAQS
    monkeypatch.setattr("faq_service.load_faqs", fake_load_faqs)
    result = find_faq(3,"退貨")
    assert result == [FAKE_FAQS[0]]

#錯誤關鍵字輸入
def test_find_faq_by_wrongkeyword_found(monkeypatch):
    def fake_load_faqs():
        return FAKE_FAQS
    monkeypatch.setattr("faq_service.load_faqs", fake_load_faqs)
    result = find_faq(3,"你好")
    assert result == []

#新增新的項目
def test_add_faq_by_id_found(monkeypatch):
    def fake_load_faqs():
        return FAKE_FAQS
    def fake_save_faq(faqs):
        pass   
    monkeypatch.setattr("faq_service.load_faqs", fake_load_faqs)
    monkeypatch.setattr("faq_service.save_faq", fake_save_faq)
    result = add_faq("購買條款",["我可以如何購買"],"購買直接買就行",[{"keyword": "購買","weight": 4}])
    
    assert result == {"id": 3, 
        "topic": "購買條款", 
        "questions": ["我可以如何購買"], 
        "answer": "購買直接買就行", 
        "keywords":  [{"keyword": "購買","weight": 4},]}

#測試系統客服給予回覆
def test_search_faq(monkeypatch):
    def fake_load_faqs():
        return FAKE_FAQS
    monkeypatch.setattr("faq_service.load_faqs", fake_load_faqs)
    
    result = search_faq("我要退貨")
    assert result == "七天內可退貨"


#測試系統客服無法給予回覆
def test_search_faq(monkeypatch):
    def fake_load_faqs():
        return FAKE_FAQS
    monkeypatch.setattr("faq_service.load_faqs", fake_load_faqs)
    
    result = search_faq("你好")
    assert result is None

#測試刪除選項
def test_remove_faq(monkeypatch):
    def fake_load_faqs():
        return FAKE_FAQS
    def fake_delet(faq):
        pass
    monkeypatch.setattr("faq_service.load_faqs", fake_load_faqs)
    monkeypatch.setattr("faq_service.delet_faq", fake_delet)
    monkeypatch.setattr("builtins.input", lambda prompt: "Y")
    result = remove_faq(1,1)
    assert result == "delete success"
    

