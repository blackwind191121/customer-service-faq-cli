from fastapi import FastAPI
from pydantic import BaseModel
from utils import load_faqs
from faq_service import search_faq

app = FastAPI()

class ChatRequest(BaseModel):
    question: str

@app.get("/")
def read_root():
    return {"message": "Hello, FastAPI"}

@app.get("/faqs")
def get_all_faqs():
    faqs = load_faqs()
    return faqs

@app.post("/chat")
def chat(request: ChatRequest):
    answer = search_faq(request.question)
    if answer is None:
        return {"answer": "找不到相關問題，請聯繫真人客服"}
    return {"answer": answer}