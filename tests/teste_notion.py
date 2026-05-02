import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp.client import chamar_ferramenta_mcp

SERVER = "src/mcp/servers/server_notion.py"


async def main():
    print("=== Teste: Criar Nota ===")
    r = await chamar_ferramenta_mcp(SERVER, "criar_nota", {
        "titulo": "Nota de teste refatoracao",
        "conteudo": "Testando o MCP Server do Notion apos refatoracao."
    })
    print(r)

    print("\n=== Teste: Listar Notas ===")
    r = await chamar_ferramenta_mcp(SERVER, "listar_notas", {"quantidade": 5})
    print(r)

    print("\n=== Teste: Buscar Notas ===")
    r = await chamar_ferramenta_mcp(SERVER, "buscar_notas", {"termo": "teste"})
    print(r)

    print("\n=== Teste: Adicionar Tarefa Notion ===")
    r = await chamar_ferramenta_mcp(SERVER, "adicionar_tarefa_notion", {
        "titulo": "Tarefa via MCP refatorado",
        "descricao": "Criada pelo test_notion.py"
    })
    print(r)


if __name__ == "__main__":
    asyncio.run(main())