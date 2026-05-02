from mcp_client import executar_mcp

SERVER = "mcp_servers/server_gmail.py"

print("=== TESTE 1 — Listar 3 emails recentes ===")
print(executar_mcp(SERVER, "listar_emails", {"quantidade": 3}))

print("\n=== TESTE 2 — Emails não lidos ===")
print(executar_mcp(SERVER, "listar_emails", {"quantidade": 3, "apenas_nao_lidos": True}))

print("\n=== TESTE 3 — Buscar emails ===")
print(executar_mcp(SERVER, "buscar_emails", {"query": "subject:reuniao", "quantidade": 3}))