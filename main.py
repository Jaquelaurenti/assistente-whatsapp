from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from agent import processar_mensagem
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Assistente WhatsApp")

ZAPI_INSTANCE = os.getenv("ZAPI_INSTANCE")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")


async def enviar_mensagem_zapi(telefone: str, mensagem: str):
    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE}/token/{ZAPI_TOKEN}/send-text"
    headers = {
        "Client-Token": os.getenv("ZAPI_CLIENT_TOKEN")
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            url,
            json={"phone": telefone, "message": mensagem},
            headers=headers
        )
        print(f"ZApi response: {response.status_code} - {response.text}")

@app.get("/")
def status():
    return {"status": "online", "produto": "Assistente de Produtividade"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    # Ignora mensagens próprias (evita loop)
    # Ignora só mensagens enviadas pelo próprio bot via API (evita loop)
    #if data.get("fromMe", False) and data.get("fromApi", False):
      #  print("⚠️ Ignorando resposta do bot")
       # return {"status": "ignorado"}
    # Ignora mensagens de grupos
    #if data.get("isGroup", False):
      #  print("⚠️ Ignorando mensagem de grupo")
       # return {"status": "ignorado"}

    telefone = data.get("phone", "")

    # Tenta pegar texto normal ou legenda de imagem/vídeo
    mensagem = (
        data.get("text", {}).get("message") or
        data.get("image", {}).get("caption") or
        data.get("video", {}).get("caption") or
        ""
    )

    print(f"📱 Telefone: {telefone}")
    print(f"💬 Mensagem: {mensagem}")

    if not telefone or not mensagem:
        print("❌ Telefone ou mensagem vazia")
        return JSONResponse(status_code=400, content={"erro": "Dados incompletos"})

    resposta = processar_mensagem(telefone, mensagem)
    print(f"🤖 Resposta: {resposta}")

    await enviar_mensagem_zapi(telefone, resposta)
    return {"status": "enviado"}