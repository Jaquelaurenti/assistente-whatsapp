import sys
import os
import pickle
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from mcp.server.fastmcp import FastMCP
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Caminhos relativos ao root do projeto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
CREDENTIALS_PATH = os.path.join(BASE_DIR, "credentials", "credentials.json")
TOKEN_PATH = os.path.join(BASE_DIR, "credentials", "token_calendar.pickle")

mcp = FastMCP("Google Calendar")


def get_calendar_service():
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

    return build("calendar", "v3", credentials=creds)


@mcp.tool()
def listar_eventos(dias: int = 7) -> str:
    """Lista eventos dos proximos N dias no Google Calendar."""
    service = get_calendar_service()
    agora = datetime.utcnow().isoformat() + "Z"
    ate = (datetime.utcnow() + timedelta(days=dias)).isoformat() + "Z"

    result = service.events().list(
        calendarId="primary",
        timeMin=agora,
        timeMax=ate,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    eventos = result.get("items", [])
    if not eventos:
        return f"Nenhum evento nos proximos {dias} dias."

    linhas = []
    for e in eventos:
        inicio = e["start"].get("dateTime", e["start"].get("date", ""))
        linhas.append(f"- {e['summary']} | {inicio}")
    return "\n".join(linhas)


@mcp.tool()
def criar_evento(titulo: str, data_hora_inicio: str, data_hora_fim: str, descricao: str = "") -> str:
    """
    Cria um evento no Google Calendar.
    Formato das datas: YYYY-MM-DDTHH:MM:SS (ex: 2024-12-25T10:00:00)
    """
    service = get_calendar_service()
    evento = {
        "summary": titulo,
        "description": descricao,
        "start": {"dateTime": data_hora_inicio, "timeZone": "America/Sao_Paulo"},
        "end": {"dateTime": data_hora_fim, "timeZone": "America/Sao_Paulo"}
    }
    resultado = service.events().insert(calendarId="primary", body=evento).execute()
    return f"Evento criado: {resultado.get('summary')} | {resultado.get('htmlLink')}"


@mcp.tool()
def buscar_eventos_hoje() -> str:
    """Lista todos os eventos de hoje no Google Calendar."""
    service = get_calendar_service()
    hoje = datetime.utcnow().date()
    inicio = datetime(hoje.year, hoje.month, hoje.day, 0, 0, 0).isoformat() + "Z"
    fim = datetime(hoje.year, hoje.month, hoje.day, 23, 59, 59).isoformat() + "Z"

    result = service.events().list(
        calendarId="primary",
        timeMin=inicio,
        timeMax=fim,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    eventos = result.get("items", [])
    if not eventos:
        return "Nenhum evento hoje."

    linhas = []
    for e in eventos:
        inicio_evt = e["start"].get("dateTime", e["start"].get("date", ""))
        linhas.append(f"- {e['summary']} | {inicio_evt}")
    return "\n".join(linhas)


if __name__ == "__main__":
    mcp.run()