from mcp_client import executar_mcp

SERVER = "mcp_servers/server_tarefas.py"
USUARIO = "jaque_mcp"

print("=== TESTE MCP — Salvar tarefa ===")
resultado = executar_mcp(SERVER, "salvar_tarefa", {
    "usuario_id": USUARIO,
    "descricao": "Preparar apresentação do produto",
    "prioridade": "alta",
    "prazo": "25/04"
})
print(resultado)

print("\n=== TESTE MCP — Listar tarefas ===")
resultado = executar_mcp(SERVER, "listar_tarefas", {"usuario_id": USUARIO})
print(resultado)

print("\n=== TESTE MCP — Salvar lembrete ===")
resultado = executar_mcp(SERVER, "salvar_lembrete", {
    "usuario_id": USUARIO,
    "descricao": "Reunião com time de produto",
    "horario": "15:00"
})
print(resultado)