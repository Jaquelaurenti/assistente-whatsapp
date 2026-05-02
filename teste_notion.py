from mcp_client import executar_mcp

SERVER = "mcp_servers/server_notion.py"

print("=== TESTE 1 — Criar nota ===")
print(executar_mcp(SERVER, "criar_nota", {
    "titulo": "Resumo do projeto assistente WhatsApp",
    "conteudo": "Estou construindo um assistente de produtividade pessoal via WhatsApp com IA. Stack: FastAPI, Groq, Bedrock, SQLite, ZApi, Railway."
}))

print("\n=== TESTE 2 — Listar notas ===")
print(executar_mcp(SERVER, "listar_notas", {"quantidade": 5}))

print("\n=== TESTE 3 — Adicionar tarefa ===")
print(executar_mcp(SERVER, "adicionar_tarefa_notion", {
    "tarefa": "Finalizar integração MCP com Notion"
}))

print("\n=== TESTE 4 — Buscar nota ===")
print(executar_mcp(SERVER, "buscar_notas", {"query": "assistente"}))