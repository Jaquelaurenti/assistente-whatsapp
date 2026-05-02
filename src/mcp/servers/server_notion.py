import sys
import os
import httpx
from datetime import datetime

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, PROJECT_ROOT)

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

load_dotenv(os.path.join(PROJECT_ROOT, ".env"))

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
NOTION_PAGE_ID = os.getenv("NOTION_PAGE_ID") or os.getenv("NOTION_DATABASE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

mcp = FastMCP("Notion")


@mcp.tool()
def criar_nota(titulo: str, conteudo: str) -> str:
    """Cria uma nova subpagina (nota) dentro da pagina do Notion."""
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"page_id": NOTION_PAGE_ID},
        "properties": {
            "title": {
                "title": [{"text": {"content": titulo}}]
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
    response = httpx.post(url, json=payload, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    return f"Nota criada no Notion: '{titulo}' | ID: {data.get('id', '?')}"


@mcp.tool()
def listar_notas(quantidade: int = 10) -> str:
    """Lista subpaginas dentro da pagina principal do Notion."""
    url = "https://api.notion.com/v1/blocks/{}/children".format(NOTION_PAGE_ID)
    response = httpx.get(url, headers=HEADERS, params={"page_size": quantidade})
    response.raise_for_status()
    data = response.json()

    resultados = data.get("results", [])
    paginas = [b for b in resultados if b.get("type") == "child_page"]

    if not paginas:
        return "Nenhuma nota encontrada na pagina do Notion."

    linhas = []
    for p in paginas:
        titulo = p.get("child_page", {}).get("title", "(sem titulo)")
        linhas.append(f"- [{p['id']}] {titulo}")
    return "\n".join(linhas)


@mcp.tool()
def buscar_notas(termo: str) -> str:
    """Busca paginas no Notion que contenham o termo informado."""
    url = "https://api.notion.com/v1/search"
    payload = {
        "query": termo,
        "filter": {"value": "page", "property": "object"}
    }
    response = httpx.post(url, json=payload, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    resultados = data.get("results", [])
    if not resultados:
        return f"Nenhuma nota encontrada para: '{termo}'"

    linhas = []
    for page in resultados:
        props = page.get("properties", {})
        titulo_prop = props.get("title") or props.get("Name") or props.get("Titulo") or {}
        titulo_lista = titulo_prop.get("title", [])
        titulo = titulo_lista[0]["text"]["content"] if titulo_lista else "(sem titulo)"
        linhas.append(f"- [{page['id']}] {titulo}")
    return "\n".join(linhas)


@mcp.tool()
def adicionar_tarefa_notion(titulo: str, descricao: str = "") -> str:
    """Adiciona uma tarefa como subpagina na pagina do Notion."""
    url = "https://api.notion.com/v1/pages"
    conteudo = descricao or f"Tarefa criada em {datetime.now().strftime('%d/%m/%Y %H:%M')}"
    payload = {
        "parent": {"page_id": NOTION_PAGE_ID},
        "properties": {
            "title": {
                "title": [{"text": {"content": titulo}}]
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
    response = httpx.post(url, json=payload, headers=HEADERS)
    response.raise_for_status()
    data = response.json()
    return f"Tarefa adicionada ao Notion: '{titulo}' | ID: {data.get('id', '?')}"


if __name__ == "__main__":
    mcp.run()