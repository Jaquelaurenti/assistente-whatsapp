from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database import (
    init_db, salvar_tarefa, listar_tarefas,
    concluir_tarefa, salvar_lembrete, listar_lembretes
)

init_db()
app = Server("server-tarefas")

@app.list_tools()
async def listar_ferramentas():
    return [
        types.Tool(
            name="salvar_tarefa",
            description="Salva uma nova tarefa do usuário com prioridade e prazo opcionais",
            inputSchema={
                "type": "object",
                "properties": {
                    "usuario_id": {"type": "string", "description": "ID do usuário"},
                    "descricao": {"type": "string", "description": "Descrição da tarefa"},
                    "prioridade": {"type": "string", "enum": ["alta", "normal", "baixa"], "description": "Prioridade da tarefa"},
                    "prazo": {"type": "string", "description": "Prazo no formato DD/MM (opcional)"}
                },
                "required": ["usuario_id", "descricao"]
            }
        ),
        types.Tool(
            name="listar_tarefas",
            description="Lista todas as tarefas pendentes do usuário ordenadas por prioridade",
            inputSchema={
                "type": "object",
                "properties": {
                    "usuario_id": {"type": "string", "description": "ID do usuário"}
                },
                "required": ["usuario_id"]
            }
        ),
        types.Tool(
            name="concluir_tarefa",
            description="Marca uma tarefa como concluída pelo nome ou parte dele",
            inputSchema={
                "type": "object",
                "properties": {
                    "usuario_id": {"type": "string", "description": "ID do usuário"},
                    "descricao_parcial": {"type": "string", "description": "Parte do nome da tarefa"}
                },
                "required": ["usuario_id", "descricao_parcial"]
            }
        ),
        types.Tool(
            name="salvar_lembrete",
            description="Salva um lembrete com horário para o usuário",
            inputSchema={
                "type": "object",
                "properties": {
                    "usuario_id": {"type": "string", "description": "ID do usuário"},
                    "descricao": {"type": "string", "description": "Descrição do lembrete"},
                    "horario": {"type": "string", "description": "Horário no formato HH:MM"}
                },
                "required": ["usuario_id", "descricao", "horario"]
            }
        ),
        types.Tool(
            name="listar_lembretes",
            description="Lista todos os lembretes pendentes do usuário",
            inputSchema={
                "type": "object",
                "properties": {
                    "usuario_id": {"type": "string", "description": "ID do usuário"}
                },
                "required": ["usuario_id"]
            }
        )
    ]

@app.call_tool()
async def executar_ferramenta(name: str, arguments: dict):
    usuario_id = arguments.get("usuario_id", "")

    if name == "salvar_tarefa":
        salvar_tarefa(
            usuario_id,
            arguments["descricao"],
            arguments.get("prioridade", "normal"),
            arguments.get("prazo")
        )
        return [types.TextContent(type="text", text=f"Tarefa salva: {arguments['descricao']}")]

    elif name == "listar_tarefas":
        tarefas = listar_tarefas(usuario_id)
        if not tarefas:
            return [types.TextContent(type="text", text="Nenhuma tarefa pendente.")]
        resultado = "\n".join([
            f"- [ID:{t[0]}] {t[1]} | prioridade: {t[2]}" + (f" | prazo: {t[3]}" if t[3] else "")
            for t in tarefas
        ])
        return [types.TextContent(type="text", text=resultado)]

    elif name == "concluir_tarefa":
        sucesso = concluir_tarefa(usuario_id, arguments["descricao_parcial"])
        msg = "Tarefa concluída!" if sucesso else "Tarefa não encontrada."
        return [types.TextContent(type="text", text=msg)]

    elif name == "salvar_lembrete":
        salvar_lembrete(usuario_id, arguments["descricao"], arguments["horario"])
        return [types.TextContent(type="text", text=f"Lembrete salvo para {arguments['horario']}: {arguments['descricao']}")]

    elif name == "listar_lembretes":
        lembretes = listar_lembretes(usuario_id)
        if not lembretes:
            return [types.TextContent(type="text", text="Nenhum lembrete pendente.")]
        resultado = "\n".join([f"- {l[1]} às {l[2]}" for l in lembretes])
        return [types.TextContent(type="text", text=resultado)]

    return [types.TextContent(type="text", text="Ferramenta não encontrada.")]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())