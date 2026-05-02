from fastapi import FastAPI, Request
from src.agent.agent import processar_mensagem
from src.channels.whatsapp import enviar_mensagem_zapi
import os

app = FastAPI()


@app.get("/")
def health_check():
    return {"status": "online", "assistente": "Jaque Assistant"}


@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()

        # Evolution API envia evento no campo "event"
        evento = data.get("event", "")

        # So processa mensagens recebidas
        if evento not in ("messages.upsert", ""):
            return {"status": "ignored", "motivo": f"evento ignorado: {evento}"}

        # Extrai dados da mensagem (formato Evolution API)
        msg_data = data.get("data", data)  # suporte a ambos formatos

        key = msg_data.get("key", {})
        from_me = key.get("fromMe", False)
        remote_jid = key.get("remoteJid", "")

        # Ignora mensagens proprias e de grupos
        if from_me:
            return {"status": "ignored", "motivo": "mensagem propria"}
        if "@g.us" in remote_jid:
            return {"status": "ignored", "motivo": "mensagem de grupo"}

        # Extrai o numero (remove @s.whatsapp.net)
        phone = remote_jid.replace("@s.whatsapp.net", "").replace("+", "")
        if not phone:
            return {"status": "ignored", "motivo": "sem numero"}

        # Extrai o texto da mensagem
        message = msg_data.get("message", {})
        texto = (
            message.get("conversation")
            or message.get("extendedTextMessage", {}).get("text")
            or message.get("imageMessage", {}).get("caption")
            or message.get("videoMessage", {}).get("caption")
            or ""
        )

        if not texto:
            return {"status": "ignored", "motivo": "sem texto"}

        # Processa e responde
        resposta = processar_mensagem(phone, texto)
        await enviar_mensagem_zapi(phone, resposta)

        return {"status": "ok"}

    except Exception as e:
        print(f"Erro no webhook: {e}")
        return {"status": "erro", "detalhe": str(e)}