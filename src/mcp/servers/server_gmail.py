import sys
import os
import pickle
import base64
from email.mime.text import MIMEText

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from mcp.server.fastmcp import FastMCP
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send"
]

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials", "credentials.json")
TOKEN_PATH = os.path.join(BASE_DIR, "credentials", "token_gmail.pickle")

mcp = FastMCP("Gmail")


def get_gmail_service():
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


@mcp.tool()
def listar_emails(quantidade: int = 5) -> str:
    """Lista os N emails mais recentes da caixa de entrada."""
    service = get_gmail_service()
    result = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=quantidade
    ).execute()

    mensagens = result.get("messages", [])
    if not mensagens:
        return "Nenhum email encontrado."

    linhas = []
    for msg in mensagens:
        detalhe = service.users().messages().get(
            userId="me", id=msg["id"], format="metadata",
            metadataHeaders=["Subject", "From", "Date"]
        ).execute()
        headers = {h["name"]: h["value"] for h in detalhe["payload"]["headers"]}
        linhas.append(
            f"[{msg['id']}] De: {headers.get('From', '?')} | "
            f"Assunto: {headers.get('Subject', '(sem assunto)')} | "
            f"Data: {headers.get('Date', '?')}"
        )
    return "\n".join(linhas)


@mcp.tool()
def ler_email(email_id: str) -> str:
    """Le o conteudo completo de um email pelo seu ID."""
    service = get_gmail_service()
    msg = service.users().messages().get(
        userId="me", id=email_id, format="full"
    ).execute()

    headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}
    corpo = ""

    partes = msg["payload"].get("parts", [])
    if partes:
        for parte in partes:
            if parte.get("mimeType") == "text/plain":
                data = parte["body"].get("data", "")
                corpo = base64.urlsafe_b64decode(data).decode("utf-8")
                break
    else:
        data = msg["payload"]["body"].get("data", "")
        if data:
            corpo = base64.urlsafe_b64decode(data).decode("utf-8")

    return (
        f"De: {headers.get('From', '?')}\n"
        f"Assunto: {headers.get('Subject', '(sem assunto)')}\n"
        f"Data: {headers.get('Date', '?')}\n\n"
        f"{corpo[:2000]}"
    )


@mcp.tool()
def enviar_email(destinatario: str, assunto: str, corpo: str) -> str:
    """Envia um email para o destinatario informado."""
    service = get_gmail_service()
    mensagem = MIMEText(corpo)
    mensagem["to"] = destinatario
    mensagem["subject"] = assunto

    raw = base64.urlsafe_b64encode(mensagem.as_bytes()).decode()
    result = service.users().messages().send(
        userId="me",
        body={"raw": raw}
    ).execute()
    return f"Email enviado! ID: {result.get('id')}"


@mcp.tool()
def buscar_emails(query: str, quantidade: int = 5) -> str:
    """
    Busca emails usando query do Gmail.
    Exemplos de query: 'from:fulano@email.com', 'subject:reuniao', 'is:unread'
    """
    service = get_gmail_service()
    result = service.users().messages().list(
        userId="me",
        q=query,
        maxResults=quantidade
    ).execute()

    mensagens = result.get("messages", [])
    if not mensagens:
        return f"Nenhum email encontrado para: {query}"

    linhas = []
    for msg in mensagens:
        detalhe = service.users().messages().get(
            userId="me", id=msg["id"], format="metadata",
            metadataHeaders=["Subject", "From", "Date"]
        ).execute()
        headers = {h["name"]: h["value"] for h in detalhe["payload"]["headers"]}
        linhas.append(
            f"[{msg['id']}] De: {headers.get('From', '?')} | "
            f"Assunto: {headers.get('Subject', '(sem assunto)')} | "
            f"Data: {headers.get('Date', '?')}"
        )
    return "\n".join(linhas)


if __name__ == "__main__":
    mcp.run()