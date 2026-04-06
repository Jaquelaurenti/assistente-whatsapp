import requests
import os
from dotenv import load_dotenv

load_dotenv()

ZAPI_INSTANCE = os.getenv("ZAPI_INSTANCE")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
BASE_URL = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}"

def enviar_mensagem(telefone: str, mensagem: str):
    url = f"{BASE_URL}/send-text"
    payload = {
        "phone": telefone,
        "message": mensagem
    }
    response = requests.post(url, json=payload)
    return response.json()