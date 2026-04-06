from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from agent import processar_mensagem

app = FastAPI(title="Assistente WhatsApp")

@app.get("/")
def status():
    return {"status": "online", "produto": "Assistente de Produtividade"}

@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    usuario_id = data.get("usuario_id", "anonimo")
    mensagem = data.get("mensagem", "")

    if not mensagem:
        return JSONResponse(
            status_code=400,
            content={"erro": "Campo 'mensagem' é obrigatório"}
        )

    resposta = processar_mensagem(usuario_id, mensagem)

    return {"resposta": resposta, "usuario_id": usuario_id}
