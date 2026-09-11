from dotenv import load_dotenv ,set_key
import os
from openai import OpenAI
import pwinput

#使用.env紀錄API資訊
ENV_PATH = ".env"

#讀取使用者的.env資料
def get_Openai_api_config():
    if not os.path.exists(ENV_PATH):
        open(ENV_PATH, "w").close()
    load_dotenv()
    api_key=os.getenv("OPENAI_API_KEY")
    model_name = os.getenv("OPENAI_MODEL")
    if api_key is None or model_name is None:
        api_key = pwinput.pwinput(
        prompt="請輸入您的 OpenAI API Key:",
        mask="*")
        model_name = input("請輸入您要使用的模型")        
        set_key(ENV_PATH,"OPENAI_API_KEY",api_key)
        set_key(ENV_PATH,"OPENAI_MODEL",model_name)
        client = OpenAI(api_key = api_key)
        user_api = {
                "key" : client,
                "model" : model_name
            }
    return user_api


