import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def chamar_ferramenta_mcp(server_script: str, tool_name: str, arguments: dict):
    """Conecta a um MCP Server e executa uma ferramenta."""
    server_params = StdioServerParameters(
        command="python3",
        args=[server_script]
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(tool_name, arguments)
            return result.content[0].text

def executar_mcp(server_script: str, tool_name: str, arguments: dict) -> str:
    """Wrapper síncrono para usar o cliente MCP."""
    return asyncio.run(chamar_ferramenta_mcp(server_script, tool_name, arguments))