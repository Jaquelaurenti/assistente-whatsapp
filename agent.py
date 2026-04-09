from groq import Groq
from dotenv import load_dotenv
from database import (
    init_db, salvar_mensagem, buscar_historico,
    salvar_tarefa, listar_tarefas, concluir_tarefa,
    salvar_lembrete, listar_lembretes
)
import os
import json

load_dotenv()
init_db()

api_key = os.getenv("GROQ_API_KEY", "").strip()
print("API KEY DEBUG:", repr(os.getenv("GROQ_API_KEY")))

client = Groq(api_key=api_key)


def carregar_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {
            "nome_assistente": "Assistente",
            "tom": "amigavel e direto",
            "idioma": "portugues brasileiro",
            "regras_extras": [],
            "saudacao": "Oi! Como posso te ajudar?"
        }


def montar_system_prompt(config, tarefas, lembretes):
    regras = "\n".join([f"- {r}" for r in config.get("regras_extras", [])])

    contexto_tarefas = ""
    if tarefas:
        itens = "\n".join([
            f"- [ID:{t[0]}] {t[1]} | prioridade: {t[2]}" +
            (f" | prazo: {t[3]}" if t[3] else "")
            for t in tarefas
        ])
        contexto_tarefas = f"\n\nTarefas pendentes:\n{itens}"

    contexto_lembretes = ""
    if lembretes:
        itens = "\n".join([
            f"- [ID:{l[0]}] {l[1]} às {l[2]}"
            for l in lembretes
        ])
        contexto_lembretes = f"\n\nLembretes:\n{itens}"

    return f"""
Voce e {config.get("nome_assistente")}, um assistente de produtividade pessoal no WhatsApp.
Tom: {config.get("tom")}
Idioma: {config.get("idioma")}

Funcoes:

[TAREFA prioridade:alta/normal/baixa prazo:DD/MM: descricao]
[CONCLUIR: descricao]
[LEMBRETE horario:HH:MM: descricao]

Regras:
{regras}

{contexto_tarefas}
{contexto_lembretes}
"""


# 🔥 MELHORADO: suporta múltiplas tags
def detectar_tags(resposta, usuario_id):
    import re

    # TAREFAS
    tarefas = re.findall(r"\[TAREFA(.*?)\]", resposta)
    for t in tarefas:
        prioridade = "normal"
        prazo = None
        descricao = t.strip()

        if "prioridade:" in t:
            prioridade = re.search(r"prioridade:(\w+)", t)
            prioridade = prioridade.group(1) if prioridade else "normal"

        if "prazo:" in t:
            prazo_match = re.search(r"prazo:([\d/]+)", t)
            prazo = prazo_match.group(1) if prazo_match else None

        descricao = re.sub(r"(prioridade:\w+|prazo:[\d/]+)", "", descricao).strip(": ").strip()

        salvar_tarefa(usuario_id, descricao, prioridade, prazo)

    # CONCLUIR
    concluidas = re.findall(r"\[CONCLUIR:(.*?)\]", resposta)
    for c in concluidas:
        concluir_tarefa(usuario_id, c.strip())

    # LEMBRETES
    lembretes = re.findall(r"\[LEMBRETE(.*?)\]", resposta)
    for l in lembretes:
        horario_match = re.search(r"horario:(\d{2}:\d{2})", l)
        horario = horario_match.group(1) if horario_match else None

        descricao = re.sub(r"horario:\d{2}:\d{2}", "", l).strip(": ").strip()

        if horario:
            salvar_lembrete(usuario_id, descricao, horario)


def limpar_resposta(resposta):
    import re
    return re.sub(r"\[(TAREFA|CONCLUIR|LEMBRETE).*?\]", "", resposta).strip()


def formatar_historico(historico):
    # 🔥 GARANTE formato correto pro LLM
    mensagens = []
    for h in historico:
        mensagens.append({
            "role": h["role"],
            "content": h["content"]
        })
    return mensagens


def processar_mensagem(usuario_id, mensagem):
    salvar_mensagem(usuario_id, "user", mensagem)

    historico = buscar_historico(usuario_id, limite=10)
    tarefas = listar_tarefas(usuario_id)
    lembretes = listar_lembretes(usuario_id)
    config = carregar_config()

    system_prompt = montar_system_prompt(config, tarefas, lembretes)

    mensagens = [
        {"role": "system", "content": system_prompt},
        *formatar_historico(historico),
        {"role": "user", "content": mensagem}  # 🔥 IMPORTANTE
    ]

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=mensagens,
            temperature=0.7
        )

        resposta = response.choices[0].message.content

    except Exception as e:
        print("Erro na Groq:", e)
        resposta = "⚠️ Tive um problema ao processar sua mensagem. Tente novamente."

    detectar_tags(resposta, usuario_id)
    resposta_limpa = limpar_resposta(resposta)

    salvar_mensagem(usuario_id, "assistant", resposta_limpa)

    return resposta_limpa