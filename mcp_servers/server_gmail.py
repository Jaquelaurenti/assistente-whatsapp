from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import base64
import email
import os
import pickle

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send"
]
TOKEN_PATH = "token_gmail.pickle"
CREDENTIALS_PATH = "credentials.json"

app = Server("server-gmail")

def autenticar_gmail():
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)
    return build("gmail", "v1", credentials=creds)

def decodificar_mensagem(msg):
    payload = msg.get("payload", {})
    parts = payload.get("parts", [])
    corpo = ""

    if parts:
        for part in parts:
            if part.get("mimeType") == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    corpo = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                    break
    else:
        data = payload.get("body", {}).get("data", "")
        if data:
            corpo = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    return corpo[:500] + "..." if len(corpo) > 500 else corpo

@app.list_tools()
async def listar_ferramentas():
    return [
        types.Tool(
            name="listar_emails",
            description="Lista os emails mais recentes da caixa de entrada",
            inputSchema={
                "type": "object",
                "properties": {
                    "quantidade": {
                        "type": "integer",
                        "description": "Quantidade de emails a listar (padrao 5)"
                    },
                    "apenas_nao_lidos": {
                        "type": "boolean",
                        "description": "Se verdadeiro, lista apenas emails nao lidos"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="ler_email",
            description="Le o conteudo completo de um email pelo ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "email_id": {
                        "type": "string",
                        "description": "ID do email retornado pelo listar_emails"
                    }
                },
                "required": ["email_id"]
            }
        ),
        types.Tool(
            name="enviar_email",
            description="Envia um email",
            inputSchema={
                "type": "object",
                "properties": {
                    "destinatario": {
                        "type": "string",
                        "description": "Email do destinatario"
                    },
                    "assunto": {
                        "type": "string",
                        "description": "Assunto do email"
                    },
                    "corpo": {
                        "type": "string",
                        "description": "Corpo do email em texto"
                    }
                },
                "required": ["destinatario", "assunto", "corpo"]
            }
        ),
        types.Tool(
            name="buscar_emails",
            description="Busca emails por palavra-chave no assunto ou remetente",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Termo de busca (ex: 'from:joao@email.com' ou 'subject:reuniao')"
                    },
                    "quantidade": {
                        "type": "integer",
                        "description": "Quantidade de resultados (padrao 5)"
                    }
                },
                "required": ["query"]
            }
        )
    ]

@app.call_tool()
async def executar_ferramenta(name: str, arguments: dict):
    service = autenticar_gmail()

    if name == "listar_emails":
        quantidade = arguments.get("quantidade", 5)
        apenas_nao_lidos = arguments.get("apenas_nao_lidos", False)
        query = "is:unread" if apenas_nao_lidos else ""

        resultado = service.users().messages().list(
            userId="me",
            maxResults=quantidade,
            q=query,
            labelIds=["INBOX"]
        ).execute()

        mensagens = resultado.get("messages", [])
        if not mensagens:
            return [types.TextContent(type="text", text="Nenhum email encontrado.")]

        emails = []
        for msg in mensagens:
            detalhe = service.users().messages().get(
                userId="me", id=msg["id"], format="metadata",
                metadataHeaders=["From", "Subject", "Date"]
            ).execute()

            headers = {h["name"]: h["value"] for h in detalhe.get("payload", {}).get("headers", [])}
            emails.append(
                f"ID: {msg['id']}\n"
                f"De: {headers.get('From', 'Desconhecido')}\n"
                f"Assunto: {headers.get('Subject', 'Sem assunto')}\n"
                f"Data: {headers.get('Date', '')}\n"
            )

        return [types.TextContent(type="text", text="\n".join(emails))]

    elif name == "ler_email":
        email_id = arguments["email_id"]
        msg = service.users().messages().get(
            userId="me", id=email_id, format="full"
        ).execute()

        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        corpo = decodificar_mensagem(msg)

        resultado = (
            f"De: {headers.get('From', '')}\n"
            f"Para: {headers.get('To', '')}\n"
            f"Assunto: {headers.get('Subject', '')}\n"
            f"Data: {headers.get('Date', '')}\n\n"
            f"{corpo}"
        )
        return [types.TextContent(type="text", text=resultado)]

    elif name == "enviar_email":
        destinatario = arguments["destinatario"]
        assunto = arguments["assunto"]
        corpo = arguments["corpo"]

        mensagem = f"To: {destinatario}\nSubject: {assunto}\n\n{corpo}"
        encoded = base64.urlsafe_b64encode(mensagem.encode()).decode()

        service.users().messages().send(
            userId="me",
            body={"raw": encoded}
        ).execute()

        return [types.TextContent(
            type="text",
            text=f"Email enviado para {destinatario} com assunto: {assunto}"
        )]

    elif name == "buscar_emails":
        query = arguments["query"]
        quantidade = arguments.get("quantidade", 5)

        resultado = service.users().messages().list(
            userId="me",
            maxResults=quantidade,
            q=query
        ).execute()

        mensagens = resultado.get("messages", [])
        if not mensagens:
            return [types.TextContent(type="text", text="Nenhum email encontrado.")]

        emails = []
        for msg in mensagens:
            detalhe = service.users().messages().get(
                userId="me", id=msg["id"], format="metadata",
                metadataHeaders=["From", "Subject", "Date"]
            ).execute()

            headers = {h["name"]: h["value"] for h in detalhe.get("payload", {}).get("headers", [])}
            emails.append(
                f"ID: {msg['id']}\n"
                f"De: {headers.get('From', '')}\n"
                f"Assunto: {headers.get('Subject', '')}\n"
            )

        return [types.TextContent(type="text", text="\n".join(emails))]

    return [types.TextContent(type="text", text="Ferramenta nao encontrada.")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())