# 🤖 Assistente de Produtividade Pessoal via WhatsApp

Agente de IA acessado pelo WhatsApp que funciona como um segundo cérebro pessoal. Você manda mensagem como se fosse para um assistente humano e ele captura tarefas, resume textos, gera rascunhos e responde perguntas — com memória persistente entre conversas.

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────┐
│                   USUÁRIO                        │
│              (WhatsApp no celular)               │
└─────────────────┬───────────────────────────────┘
                  │ mensagem de texto
                  ▼
┌─────────────────────────────────────────────────┐
│              TWILIO / ZAPI                       │
│         (ponte WhatsApp → webhook)               │
└─────────────────┬───────────────────────────────┘
                  │ POST /webhook
                  ▼
┌─────────────────────────────────────────────────┐
│              FASTAPI (backend)                   │
│                                                  │
│  1. Recebe a mensagem                            │
│  2. Busca histórico do usuário                   │
│  3. Monta o prompt com contexto                  │
│  4. Chama o LLM (Groq)                           │
│  5. Salva a conversa                             │
│  6. Devolve a resposta                           │
└──────┬──────────────────────┬───────────────────┘
       │                      │
       ▼                      ▼
┌─────────────┐      ┌────────────────┐
│    GROQ     │      │    SQLITE      │
│  (LLM API) │      │  (histórico +  │
│   grátis    │      │   tarefas)     │
└─────────────┘      └────────────────┘
```

---

## 🛠️ Stack Tecnológica

| Componente | Ferramenta | Custo |
|---|---|---|
| LLM | Groq (LLaMA 3.3 70B) | Grátis |
| Backend | FastAPI + Uvicorn | Grátis |
| Banco de dados | SQLite | Grátis |
| WhatsApp | ZApi ou Twilio | Trial grátis |
| Túnel local | ngrok | Grátis |
| Deploy | Railway ou Render | Grátis (tier free) |

---

## 📁 Estrutura do Projeto

```
assistente-whatsapp/
├── .env                  ← chaves de API (nunca sobe pro GitHub)
├── .gitignore
├── README.md
├── requirements.txt
├── venv/                 ← ambiente virtual Python
├── database.py           ← SQLite: histórico e tarefas
├── agent.py              ← cérebro do produto (LLM + memória)
├── main.py               ← servidor FastAPI + webhook
└── teste.py              ← validação das funcionalidades
```

---

## ⚙️ Funcionalidades do Agente

| Funcionalidade | Como usar | Exemplo |
|---|---|---|
| Captura de tarefas | Mencione algo que precisa fazer | "preciso entregar o relatório sexta" |
| Resumo de texto | Cole um texto e peça resumo | "resume isso: [texto longo]" |
| Rascunho | Peça para escrever algo | "escreve um email pedindo extensão de prazo" |
| Perguntas | Pergunte qualquer coisa | "o que eu tenho para fazer essa semana?" |

---

## 🚀 Como Rodar Localmente

### Pré-requisitos

- Python 3.11+
- Conta gratuita no [Groq](https://console.groq.com)
- Conta gratuita no [ngrok](https://dashboard.ngrok.com/signup)

### 1. Clone o repositório

```bash
git clone https://github.com/jaquelaurenti/assistente-whatsapp.git
cd assistente-whatsapp
```

### 2. Crie e ative o ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```
GROQ_API_KEY=sua_chave_aqui
```

Obtenha sua chave gratuita em: https://console.groq.com

### 5. Rode o servidor

```bash
uvicorn main:app --reload --port 8000
```

### 6. Exponha para a internet (em outro terminal)

```bash
ngrok http 8000
```

Copie o link `https://...ngrok-free.app` gerado — ele é o seu webhook público.

### 7. Teste o agente

```bash
# Verifica se está online
curl http://localhost:8000/

# Envia uma mensagem
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": "voce", "mensagem": "preciso estudar FastAPI até amanhã"}'

# Testa a memória
curl -X POST http://localhost:8000/webhook \
  -H "Content-Type: application/json" \
  -d '{"usuario_id": "voce", "mensagem": "o que eu tenho para fazer?"}'
```

---

## 📡 Endpoints da API

### `GET /`
Verifica se o servidor está online.

**Resposta:**
```json
{
  "status": "online",
  "produto": "Assistente de Produtividade"
}
```

### `POST /webhook`
Recebe uma mensagem e retorna a resposta do agente.

**Body:**
```json
{
  "usuario_id": "identificador_unico_do_usuario",
  "mensagem": "texto da mensagem"
}
```

**Resposta:**
```json
{
  "resposta": "resposta do agente",
  "usuario_id": "identificador_unico_do_usuario"
}
```

---

## 🗄️ Banco de Dados

O projeto usa **SQLite** com duas tabelas:

**`historico`** — armazena todas as mensagens para memória contextual
```
id | usuario_id | papel (user/assistant) | mensagem | criado_em
```

**`tarefas`** — armazena tarefas capturadas pelo agente
```
id | usuario_id | descricao | concluida | criado_em
```

---

## 🧠 Como o Agente Funciona

1. Usuário envia mensagem via WhatsApp
2. ZApi/Twilio encaminha para o webhook `/webhook`
3. FastAPI recebe e chama `processar_mensagem()` em `agent.py`
4. O agente busca as últimas 10 mensagens do histórico no SQLite
5. Busca as tarefas pendentes do usuário
6. Monta o prompt completo com system prompt + histórico + contexto de tarefas
7. Chama o Groq (LLaMA 3.3 70B) com todo o contexto
8. Detecta se o modelo sinalizou uma nova tarefa com a tag `[TAREFA: ...]`
9. Salva a tarefa no banco se houver
10. Remove a tag interna da resposta
11. Salva a resposta no histórico
12. Retorna a resposta limpa para o usuário

---

## 🗺️ Roadmap

- [x] **Semana 1** — Core do agente com memória e 4 funcionalidades
- [x] **Semana 2** — FastAPI + webhook funcionando com ngrok
- [ ] **Semana 3** — Integração com WhatsApp via ZApi ou Twilio
- [ ] **Semana 4** — Deploy na nuvem (Railway ou Render)

---

## 🔧 Variáveis de Ambiente

| Variável | Descrição | Onde obter |
|---|---|---|
| `GROQ_API_KEY` | Chave da API do Groq | [console.groq.com](https://console.groq.com) |
| `ZAPI_TOKEN` | Token da ZApi (Semana 3) | [z-api.io](https://z-api.io) |
| `ZAPI_INSTANCE` | ID da instância ZApi (Semana 3) | [z-api.io](https://z-api.io) |

---

## 📦 Instalação das Dependências

```bash
pip install groq python-dotenv fastapi uvicorn
```

Ou via requirements.txt:

```bash
pip install -r requirements.txt
```

---

## 🤝 Contribuindo

Este projeto está em desenvolvimento ativo como parte de um estudo de construção de agentes de IA com foco em produto. Sugestões e PRs são bem-vindos!

---

## 📄 Licença

MIT
