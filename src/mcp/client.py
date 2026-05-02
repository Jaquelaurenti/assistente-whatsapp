import asyncio
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv

# Root do projeto (2 niveis acima de src/mcp/)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# Garante que o .env e carregado no processo pai antes de passar env ao subprocess
load_dotenv(os.path.join(PROJECT_ROOT, ".env"))


async def chamar_ferramenta_mcp(server_script: str, tool_name: str, arguments: dict) -> str:
    """
    Chama uma ferramenta de um MCP Server via stdio.

    Args:
        server_script: Caminho para o script do servidor MCP (ex: src/mcp/servers/server_tarefas.py)
        tool_name: Nome da ferramenta a ser chamada
        arguments: Dicionario com os argumentos da ferramenta

    Returns:
        Texto retornado pela ferramenta
    """
    # Garante que o PYTHONPATH inclui o root do projeto no subprocess
    env = os.environ.copy()
    env["PYTHONPATH"] = PROJECT_ROOT

    server_params = StdioServerParameters(
        command="python3",
        args=[server_script],
        env=env
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result.content[0].text


def chamar_ferramenta_mcp_sync(server_script: str, tool_name: str, arguments: dict) -> str:
    """Versao sincrona do chamar_ferramenta_mcp para uso em contextos nao-async."""
    return asyncio.run(chamar_ferramenta_mcp(server_script, tool_name, arguments))