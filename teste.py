from agent import processar_mensagem

USUARIO = "jaque_teste"

print("=" * 50)
print("TESTE 1 — Captura de tarefa")
print("=" * 50)
resposta = processar_mensagem(USUARIO, "preciso entregar o relatório de vendas até sexta")
print(resposta)

print("\n" + "=" * 50)
print("TESTE 2 — Memória (lembra da conversa anterior)")
print("=" * 50)
resposta = processar_mensagem(USUARIO, "e o que eu preciso fazer essa semana?")
print(resposta)

print("\n" + "=" * 50)
print("TESTE 3 — Resumo de texto")
print("=" * 50)
texto_longo = """
A inteligência artificial generativa está transformando a forma como empresas 
operam em todo o mundo. Ferramentas como ChatGPT, Claude e Gemini permitem que 
equipes automatizem tarefas repetitivas, gerem conteúdo em escala e tomem 
decisões mais rápidas baseadas em dados. Estudos mostram que empresas que adotam 
IA generativa reportam ganhos de produtividade de até 40% em funções como 
atendimento ao cliente, criação de conteúdo e análise de dados. No entanto, 
desafios como privacidade, alucinações do modelo e resistência cultural ainda 
são barreiras para adoção em larga escala.
"""
resposta = processar_mensagem(USUARIO, f"resume isso pra mim: {texto_longo}")
print(resposta)

print("\n" + "=" * 50)
print("TESTE 4 — Rascunho de mensagem")
print("=" * 50)
resposta = processar_mensagem(USUARIO, "escreve um email pedindo extensão de prazo para o relatório de vendas")
print(resposta)