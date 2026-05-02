import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp.client import chamar_ferramenta_mcp

SERVER = "src/mcp/servers/server_calendar.py"


async def main():
    print("=== Teste: Eventos de Hoje ===")
    r = await chamar_ferramenta_mcp(SERVER, "buscar_eventos_hoje", {})
    print(r)

    print("\n=== Teste: Proximos 7 dias ===")
    r = await chamar_ferramenta_mcp(SERVER, "listar_eventos", {"dias": 7})
    print(r)


if __name__ == "__main__":
    asyncio.run(main())