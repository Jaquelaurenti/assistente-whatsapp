from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import datetime
import os
import pickle

SCOPES = ["https://www.googleapis.com/auth/calendar"]
TOKEN_PATH = "token_calendar.pickle"
CREDENTIALS_PATH = "credentials.json"

app = Server("server-calendar")

def autenticar_google():
    """Autentica com Google e retorna o serviço do Calendar."""
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

@app.list_tools()
async def listar_ferramentas():
    return [
        types.Tool(
            name="listar_eventos",
            description="Lista os proximos eventos do Google Calendar do usuario",
            inputSchema={
                "type": "object",
                "properties": {
                    "quantidade": {
                        "type": "integer",
                        "description": "Quantidade de eventos a listar (padrao 5)"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="criar_evento",
            description="Cria um novo evento no Google Calendar",
            inputSchema={
                "type": "object",
                "properties": {
                    "titulo": {
                        "type": "string",
                        "description": "Titulo do evento"
                    },
                    "data": {
                        "type": "string",
                        "description": "Data do evento no formato YYYY-MM-DD"
                    },
                    "hora_inicio": {
                        "type": "string",
                        "description": "Hora de inicio no formato HH:MM"
                    },
                    "hora_fim": {
                        "type": "string",
                        "description": "Hora de fim no formato HH:MM"
                    },
                    "descricao": {
                        "type": "string",
                        "description": "Descricao opcional do evento"
                    }
                },
                "required": ["titulo", "data", "hora_inicio", "hora_fim"]
            }
        ),
        types.Tool(
            name="buscar_eventos_hoje",
            description="Busca todos os eventos de hoje no Google Calendar",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": []
            }
        )
    ]

@app.call_tool()
async def executar_ferramenta(name: str, arguments: dict):
    service = autenticar_google()

    if name == "listar_eventos":
        quantidade = arguments.get("quantidade", 5)
        agora = datetime.datetime.utcnow().isoformat() + "Z"

        eventos = service.events().list(
            calendarId="primary",
            timeMin=agora,
            maxResults=quantidade,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        items = eventos.get("items", [])

        if not items:
            return [types.TextContent(type="text", text="Nenhum evento encontrado.")]

        resultado = "Proximos eventos:\n"
        for evento in items:
            inicio = evento["start"].get("dateTime", evento["start"].get("date"))
            resultado += f"- {evento['summary']} | {inicio}\n"

        return [types.TextContent(type="text", text=resultado)]

    elif name == "criar_evento":
        titulo = arguments["titulo"]
        data = arguments["data"]
        hora_inicio = arguments["hora_inicio"]
        hora_fim = arguments["hora_fim"]
        descricao = arguments.get("descricao", "")

        evento = {
            "summary": titulo,
            "description": descricao,
            "start": {
                "dateTime": f"{data}T{hora_inicio}:00",
                "timeZone": "America/Sao_Paulo"
            },
            "end": {
                "dateTime": f"{data}T{hora_fim}:00",
                "timeZone": "America/Sao_Paulo"
            }
        }

        resultado = service.events().insert(calendarId="primary", body=evento).execute()
        link = resultado.get("htmlLink", "")

        return [types.TextContent(
            type="text",
            text=f"Evento criado: {titulo} em {data} das {hora_inicio} as {hora_fim}\nLink: {link}"
        )]

    elif name == "buscar_eventos_hoje":
        hoje = datetime.date.today()
        inicio_dia = datetime.datetime.combine(hoje, datetime.time.min).isoformat() + "Z"
        fim_dia = datetime.datetime.combine(hoje, datetime.time.max).isoformat() + "Z"

        eventos = service.events().list(
            calendarId="primary",
            timeMin=inicio_dia,
            timeMax=fim_dia,
            singleEvents=True,
            orderBy="startTime"
        ).execute()

        items = eventos.get("items", [])

        if not items:
            return [types.TextContent(type="text", text="Nenhum evento para hoje.")]

        resultado = "Eventos de hoje:\n"
        for evento in items:
            inicio = evento["start"].get("dateTime", evento["start"].get("date"))
            hora = inicio[11:16] if "T" in inicio else "dia todo"
            resultado += f"- {hora} {evento['summary']}\n"

        return [types.TextContent(type="text", text=resultado)]

    return [types.TextContent(type="text", text="Ferramenta nao encontrada.")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())