from mcp_client import executar_mcp

SERVER = "mcp_servers/server_calendar.py"

print("=== TESTE 1 — Eventos de hoje ===")
print(executar_mcp(SERVER, "buscar_eventos_hoje", {}))

print("\n=== TESTE 2 — Próximos 3 eventos ===")
print(executar_mcp(SERVER, "listar_eventos", {"quantidade": 3}))

print("\n=== TESTE 3 — Criar evento ===")
print(executar_mcp(SERVER, "criar_evento", {
    "titulo": "Reunião de produto",
    "data": "2026-05-10",
    "hora_inicio": "10:00",
    "hora_fim": "11:00",
    "descricao": "Revisão do roadmap do assistente WhatsApp"
}))