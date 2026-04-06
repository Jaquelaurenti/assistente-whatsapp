from groq import Groq
from dotenv import load_dotenv
from database import (
    init_db, salvar_mensagem,
    buscar_historico, salvar_tarefa, listar_tarefas
)
import os

load_dotenv()
init_db()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
Você é um assistente de produtividade pessoal acessado via WhatsApp.
Você tem memória das conversas anteriores e ajuda o usuário com:

1. TAREFAS: quando o usuário mencionar algo que precisa fazer,
   confirme que salvou e use a tag [TAREFA: descrição da tarefa]

2. RESUMO: quando pedirem para resumir um texto,
   entregue em até 5 bullets objetivos

3. RASCUNHO: quando pedirem para escrever algo (email, mensagem, post),
   entregue o texto pronto para copiar e colar

4. PERGUNTAS: responda de forma direta e prática

Regras:
- Respostas curtas e diretas — você está no WhatsApp
- Sem formatação markdown excessiva (sem **, sem #)
- Sempre confirme quando salvar uma tarefa
- Tom amigável, como um assistente pessoal de confiança
"""

def detectar_tarefa(resposta: str):
    if "[TAREFA:" in resposta:
        inicio = resposta.index("[TAREFA:") + len("[TAREFA:")
        fim = resposta.index("]", inicio)
        return resposta[inicio:fim].strip()
    return None

def limpar_resposta(resposta: str) -> str:
    if "[TAREFA:" in resposta and "]" in resposta:
        inicio = resposta.index("[TAREFA:")
        fim = resposta.index("]", inicio) + 1
        resposta = resposta[:inicio] + resposta[fim:]
    return resposta.strip()

def processar_mensagem(usuario_id: str, mensagem: str) -> str:
    salvar_mensagem(usuario_id, "user", mensagem)
    historico = buscar_historico(usuario_id, limite=10)
    tarefas = listar_tarefas(usuario_id)
    contexto_tarefas = ""
    if tarefas:
        lista = "\n".join([f"- {t[1]}" for t in tarefas])
        contexto_tarefas = f"\n\nTarefas pendentes do usuário:\n{lista}"
    system_completo = SYSTEM_PROMPT + contexto_tarefas
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_completo},
            *historico
        ]
    )
    resposta = response.choices[0].message.content
    tarefa = detectar_tarefa(resposta)
    if tarefa:
        salvar_tarefa(usuario_id, tarefa)
    resposta_limpa = limpar_resposta(resposta)
    salvar_mensagem(usuario_id, "assistant", resposta_limpa)
    return resposta_limpa
