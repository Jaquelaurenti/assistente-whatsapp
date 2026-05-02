import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp.client import chamar_ferramenta_mcp

SERVER = "src/mcp/servers/server_gmail.py"


async def main():
    print("=== Teste: Listar Emails ===")
    r = await chamar_ferramenta_mcp(SERVER, "listar_emails", {"quantidade": 3})
    print(r)

    print("\n=== Teste: Buscar Emails ===")
    r = await chamar_ferramenta_mcp(SERVER, "buscar_emails", {
        "query": "is:unread",
        "quantidade": 3
    })
    print(r)


if __name__ == "__main__":
    asyncio.run(main())