import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.mcp.client import chamar_ferramenta_mcp

SERVER = "src/mcp/servers/server_tarefas.py"
USUARIO = "test_user"


async def main():
    print("=== Teste: Salvar Tarefa ===")
    r = await chamar_ferramenta_mcp(SERVER, "salvar_tarefa_tool", {
        "usuario_id": USUARIO,
        "descricao": "Estudar Python avancado",
        "prioridade": "alta",
        "prazo": "10/05"
    })
    print(r)

    print("\n=== Teste: Listar Tarefas ===")
    r = await chamar_ferramenta_mcp(SERVER, "listar_tarefas_tool", {"usuario_id": USUARIO})
    print(r)

    print("\n=== Teste: Salvar Lembrete ===")
    r = await chamar_ferramenta_mcp(SERVER, "salvar_lembrete_tool", {
        "usuario_id": USUARIO,
        "descricao": "Reuniao de alinhamento",
        "horario": "14:00"
    })
    print(r)

    print("\n=== Teste: Listar Lembretes ===")
    r = await chamar_ferramenta_mcp(SERVER, "listar_lembretes_tool", {"usuario_id": USUARIO})
    print(r)

    print("\n=== Teste: Concluir Tarefa ===")
    r = await chamar_ferramenta_mcp(SERVER, "concluir_tarefa_tool", {
        "usuario_id": USUARIO,
        "descricao_parcial": "Python"
    })
    print(r)

    print("\n=== Tarefas apos conclusao ===")
    r = await chamar_ferramenta_mcp(SERVER, "listar_tarefas_tool", {"usuario_id": USUARIO})
    print(r)


if __name__ == "__main__":
    asyncio.run(main())