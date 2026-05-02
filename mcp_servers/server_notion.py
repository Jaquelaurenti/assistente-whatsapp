from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
import httpx
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID")
NOTION_VERSION = "2022-06-28"

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": NOTION_VERSION
}

app = Server("server-notion")

@app.list_tools()
async def listar_ferramentas():
    return [
        types.Tool(
            name="criar_nota",
            description="Cria uma nova nota no Notion com titulo e conteudo",
            inputSchema={
                "type": "object",
                "properties": {
                    "titulo": {
                        "type": "string",
                        "description": "Titulo da nota"
                    },
                    "conteudo": {
                        "type": "string",
                        "description": "Conteudo da nota"
                    }
                },
                "required": ["titulo", "conteudo"]
            }
        ),
        types.Tool(
            name="listar_notas",
            description="Lista as notas salvas no Notion",
            inputSchema={
                "type": "object",
                "properties": {
                    "quantidade": {
                        "type": "integer",
                        "description": "Quantidade de notas a listar (padrao 5)"
                    }
                },
                "required": []
            }
        ),
        types.Tool(
            name="buscar_notas",
            description="Busca notas no Notion por palavra-chave",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Termo de busca"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="adicionar_tarefa_notion",
            description="Adiciona uma tarefa na pagina do Notion como item de lista",
            inputSchema={
                "type": "object",
                "properties": {
                    "tarefa": {
                        "type": "string",
                        "description": "Descricao da tarefa"
                    }
                },
                "required": ["tarefa"]
            }
        )
    ]

@app.call_tool()
async def executar_ferramenta(name: str, arguments: dict):

    if name == "criar_nota":
        titulo = arguments["titulo"]
        conteudo = arguments["conteudo"]
        data_hoje = datetime.now().strftime("%d/%m/%Y %H:%M")

        payload = {
            "parent": {"page_id": NOTION_PAGE_ID},
            "properties": {
                "title": {
                    "title": [{"text": {"content": f"{titulo} — {data_hoje}"}}]
                }
            },
            "children": [
                {
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [{"type": "text", "text": {"content": conteudo}}]
                    }
                }
            ]
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.notion.com/v1/pages",
                headers=HEADERS,
                json=payload
            )

        if response.status_code == 200:
            data = response.json()
            url = data.get("url", "")
            return [types.TextContent(type="text", text=f"Nota criada: {titulo}\nLink: {url}")]
        else:
            return [types.TextContent(type="text", text=f"Erro ao criar nota: {response.text}")]

    elif name == "listar_notas":
        quantidade = arguments.get("quantidade", 5)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children",
                headers=HEADERS,
                params={"page_size": quantidade}
            )

        if response.status_code != 200:
            return [types.TextContent(type="text", text=f"Erro ao listar notas: {response.text}")]

        data = response.json()
        results = data.get("results", [])

        if not results:
            return [types.TextContent(type="text", text="Nenhuma nota encontrada.")]

        notas = []
        for item in results[:quantidade]:
            tipo = item.get("type", "")
            if tipo == "child_page":
                titulo = item.get("child_page", {}).get("title", "Sem titulo")
                notas.append(f"- {titulo}")

        if not notas:
            return [types.TextContent(type="text", text="Nenhuma nota encontrada.")]

        return [types.TextContent(type="text", text="Notas salvas:\n" + "\n".join(notas))]

    elif name == "buscar_notas":
        query = arguments["query"]

        payload = {"query": query}

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.notion.com/v1/search",
                headers=HEADERS,
                json=payload
            )

        if response.status_code != 200:
            return [types.TextContent(type="text", text=f"Erro na busca: {response.text}")]

        data = response.json()
        results = data.get("results", [])

        if not results:
            return [types.TextContent(type="text", text=f"Nenhuma nota encontrada para '{query}'.")]

        notas = []
        for item in results[:5]:
            props = item.get("properties", {})
            titulo_data = props.get("title", {}).get("title", [])
            titulo = titulo_data[0]["text"]["content"] if titulo_data else "Sem titulo"
            url = item.get("url", "")
            notas.append(f"- {titulo}\n  {url}")

        return [types.TextContent(type="text", text="Resultados:\n" + "\n".join(notas))]

    elif name == "adicionar_tarefa_notion":
        tarefa = arguments["tarefa"]

        payload = {
            "children": [
                {
                    "object": "block",
                    "type": "to_do",
                    "to_do": {
                        "rich_text": [{"type": "text", "text": {"content": tarefa}}],
                        "checked": False
                    }
                }
            ]
        }

        async with httpx.AsyncClient() as client:
            response = await client.patch(
                f"https://api.notion.com/v1/blocks/{NOTION_PAGE_ID}/children",
                headers=HEADERS,
                json=payload
            )

        if response.status_code == 200:
            return [types.TextContent(type="text", text=f"Tarefa adicionada no Notion: {tarefa}")]
        else:
            return [types.TextContent(type="text", text=f"Erro ao adicionar tarefa: {response.text}")]

    return [types.TextContent(type="text", text="Ferramenta nao encontrada.")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())