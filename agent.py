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

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def carregar_config():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
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
            "- [ID:{}] {} | prioridade: {}".format(t[0], t[1], t[2]) +
            (" | prazo: {}".format(t[3]) if t[3] else "")
            for t in tarefas
        ])
        contexto_tarefas = "\n\nTarefas pendentes do usuario (ordenadas por prioridade):\n" + itens

    contexto_lembretes = ""
    if lembretes:
        itens = "\n".join(["- [ID:{}] {} as {}".format(l[0], l[1], l[2]) for l in lembretes])
        contexto_lembretes = "\n\nLembretes agendados:\n" + itens

    return """Voce e {nome}, um assistente de produtividade pessoal no WhatsApp.
Tom: {tom}
Idioma: {idioma}

Voce ajuda o usuario com os seguintes caminhos:

1. TAREFA: quando mencionar algo que precisa fazer
   Use a tag [TAREFA prioridade:alta/normal/baixa prazo:DD/MM: descricao]
   Identifique a prioridade pelo contexto (urgente, hoje, importante = alta)

2. CONCLUIR: quando disser que terminou ou concluiu algo
   Use a tag [CONCLUIR: parte do nome da tarefa]

3. LEMBRETE: quando pedir para ser lembrado em um horario
   Use a tag [LEMBRETE horario:HH:MM: descricao]

4. PRIORIZAR: quando pedir o que fazer primeiro ou o que e mais urgente
   Liste as tarefas ordenadas por prioridade com sugestao de por onde comecar

5. RESUMO: quando pedir para resumir um texto
   Entregue em ate 5 bullets objetivos

6. RASCUNHO: quando pedir para escrever algo
   Entregue o texto pronto para copiar e colar

7. PERGUNTA: responda de forma direta e pratica

Regras:
{regras}
{contexto_tarefas}
{contexto_lembretes}""".format(
        nome=config.get("nome_assistente", "Assistente"),
        tom=config.get("tom", "amigavel"),
        idioma=config.get("idioma", "portugues"),
        regras=regras,
        contexto_tarefas=contexto_tarefas,
        contexto_lembretes=contexto_lembretes
    )

def detectar_tags(resposta, usuario_id):
    # Detecta TAREFA
    if "[TAREFA" in resposta and "]" in resposta:
        inicio = resposta.index("[TAREFA")
        fim = resposta.index("]", inicio)
        conteudo = resposta[inicio+7:fim].strip()

        prioridade = "normal"
        prazo = None
        descricao = conteudo

        if "prioridade:" in conteudo:
            p_start = conteudo.index("prioridade:") + 11
            resto = conteudo[p_start:]
            p_end = resto.index(" ") if " " in resto else len(resto)
            prioridade = resto[:p_end].strip()
            descricao = descricao.replace("prioridade:" + prioridade, "").strip()

        if "prazo:" in conteudo:
            pz_start = conteudo.index("prazo:") + 6
            resto = conteudo[pz_start:]
            pz_end = resto.index(" ") if " " in resto else len(resto)
            prazo = resto[:pz_end].strip().rstrip(":")
            descricao = descricao.replace("prazo:" + prazo, "").strip().strip(":")

        salvar_tarefa(usuario_id, descricao.strip(), prioridade, prazo)

    # Detecta CONCLUIR
    if "[CONCLUIR:" in resposta and "]" in resposta:
        inicio = resposta.index("[CONCLUIR:") + 10
        fim = resposta.index("]", inicio)
        descricao = resposta[inicio:fim].strip()
        concluir_tarefa(usuario_id, descricao)

    # Detecta LEMBRETE
    if "[LEMBRETE" in resposta and "]" in resposta:
        inicio = resposta.index("[LEMBRETE")
        fim = resposta.index("]", inicio)
        conteudo = resposta[inicio+9:fim].strip()

        horario = ""
        descricao = conteudo

        if "horario:" in conteudo:
            h_start = conteudo.index("horario:") + 8
            resto = conteudo[h_start:]
            h_end = resto.index(" ") if " " in resto else len(resto)
            horario = resto[:h_end].strip().rstrip(":")
            descricao = descricao.replace("horario:" + horario, "").strip().strip(":")

        if horario:
            salvar_lembrete(usuario_id, descricao.strip(), horario)

def limpar_resposta(resposta):
    tags = ["[TAREFA", "[CONCLUIR:", "[LEMBRETE"]
    for tag in tags:
        while tag in resposta and "]" in resposta:
            inicio = resposta.index(tag)
            fim = resposta.index("]", inicio) + 1
            resposta = resposta[:inicio] + resposta[fim:]
    return resposta.strip()

def processar_mensagem(usuario_id, mensagem):
    salvar_mensagem(usuario_id, "user", mensagem)

    historico = buscar_historico(usuario_id, limite=10)
    tarefas = listar_tarefas(usuario_id)
    lembretes = listar_lembretes(usuario_id)
    config = carregar_config()

    system_prompt = montar_system_prompt(config, tarefas, lembretes)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            *historico
        ]
    )

    resposta = response.choices[0].message.content
    detectar_tags(resposta, usuario_id)
    resposta_limpa = limpar_resposta(resposta)
    salvar_mensagem(usuario_id, "assistant", resposta_limpa)

    return resposta_limpa
