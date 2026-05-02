from agent import processar_mensagem

U = "jaque_teste"

testes = [
    ("Tarefa com prioridade", "preciso urgente terminar o pitch deck hoje"),
    ("Tarefa com prazo", "preciso entregar o relatório até dia 20/04"),
    ("Lembrete", "me lembra de tomar remédio às 20:00"),
    ("Priorização", "o que eu devo fazer primeiro?"),
    ("Concluir tarefa", "terminei o pitch deck"),
    ("Resumo", "resume isso: inteligência artificial está transformando empresas com ganhos de produtividade de até 40%"),
    ("Rascunho", "escreve um email avisando que vou atrasar a entrega do relatório"),
    ("Listar tarefas", "quais são minhas tarefas pendentes?"),
]

for titulo, mensagem in testes:
    print(f"\n{'='*50}")
    print(f"TESTE — {titulo}")
    print(f"{'='*50}")
    print(f"Você: {mensagem}")
    print(f"Bot: {processar_mensagem(U, mensagem)}")