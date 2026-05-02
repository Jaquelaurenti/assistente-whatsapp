import httpx
import os
from dotenv import load_dotenv

_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
load_dotenv(os.path.join(_BASE_DIR, ".env"))

EVOLUTION_API_URL = os.getenv("EVOLUTION_API_URL")       # https://sua-url.railway.app
EVOLUTION_API_KEY = os.getenv("EVOLUTION_API_KEY")       # sua chave secreta
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "assistente")


async def enviar_mensagem_zapi(phone: str, mensagem: str) -> dict:
    """Envia mensagem de texto via Evolution API."""
    # Garante formato correto do numero (so digitos, sem @)
    numero = phone.replace("@s.whatsapp.net", "").replace("+", "").strip()

    url = f"{EVOLUTION_API_URL}/message/sendText/{EVOLUTION_INSTANCE}"

    headers = {
        "Content-Type": "application/json",
        "apikey": EVOLUTION_API_KEY
    }

    payload = {
        "number": numero,
        "text": mensagem
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()