from fastapi import FastAPI
from pydantic import BaseModel
from utils import load_faqs
from faq_service import search_faq
from fastapi.responses import StreamingResponse
from AI_env import get_Openai_api_config
from openai import OpenAI
from contextlib import asynccontextmanager
from data_paths import validate_chat_name
from starlette.concurrency import run_in_threadpool
from local_rag_service import load_local_rag, retrieve_faq_context
from chat_service import answer_stream
import logging
from fastapi import FastAPI, HTTPException
from errors import ChatModelError

logger = logging.getLogger(__name__)
# 服務啟動時載入本地模型與索引，保存起來供後續請求使用
@asynccontextmanager
async def lifespan(app: FastAPI):
    # 將同步載入工作交給執行緒池，避免阻塞事件迴圈
    app.state.rag = await run_in_threadpool(load_local_rag)

    # 啟動準備完成，讓 FastAPI 開始處理請求
    # 若有關閉服務時的清理工作，可以放在 yield 後面
    yield


# 建立 FastAPI，指定服務啟動與關閉時使用的生命週期函式
app = FastAPI(lifespan=lifespan)


# 定義一般查詢的請求格式，由 Pydantic 驗證輸入資料
class ChatRequest(BaseModel):
    question: str


# 定義串流對話的請求格式
class ChatStreamRequest(BaseModel):
    chat_name: str
    user_question: str
    provider: str = "local"


# 首頁：回傳簡單訊息，確認 API 可以回應
@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI"}


# 讀取並回傳目前所有 FAQ
@app.get("/faqs")
def get_all_faqs():
    faqs = load_faqs()
    return faqs


# 一般查詢：沿用關鍵字權重搜尋，直接回傳 FAQ 答案
@app.post("/chat")
def chat(request: ChatRequest):
    answer = search_faq(request.question)
    if answer is None:
        return {"answer": "找不到相關問題，請聯繫真人客服"}
    return {"answer": answer}


# 串流對話：先用本地向量搜尋 FAQ，再交給雲端 AI 回答
@app.post("/chat_stream")
def chat_stream(request: ChatStreamRequest):
    if request.provider not in ("openai", "local"):
        raise HTTPException(status_code=400, detail="provider 必須是 openai 或 local")
    question = request.user_question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="問題不能是空白"
        )
    try:
        chat_name = validate_chat_name(request.chat_name)
    except ValueError as error:
        raise HTTPException(status_code=400,detail=str(error)) from error
    faq_context = retrieve_faq_context(
        question=question,
        rag=app.state.rag,
        top_k=3,
    )

    # 本地模型不需要 OpenAI 用戶端，也不該因為缺 key 而卡住
    if request.provider == "openai":
        api_info = get_Openai_api_config()
        client, model = api_info["key"], api_info["model"]
    else:
        client, model = None, "qwen3:8b"

    def event_generator():
        try:
            yield from answer_stream(
                client=client,
                model=model,
                provider=request.provider,
                chat_name=chat_name,
                question=question,
                faq_context=faq_context,
            )
        except ChatModelError as error:
            # 串流已開始，HTTP 狀態碼已是 200，只能在結尾補一行錯誤標記
            logger.warning("stream failed chat=%s: %s", request.chat_name, error)
            yield f"\n[ERROR] {error}"

    return StreamingResponse(event_generator(), media_type="text/plain")