import sqlite3
from datetime import datetime

DB_PATH = "assistente.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS historico (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id TEXT NOT NULL,
            papel TEXT NOT NULL,
            mensagem TEXT NOT NULL,
            criado_em TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tarefas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id TEXT NOT NULL,
            descricao TEXT NOT NULL,
            prioridade TEXT DEFAULT 'normal',
            prazo TEXT DEFAULT NULL,
            concluida INTEGER DEFAULT 0,
            criado_em TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lembretes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id TEXT NOT NULL,
            descricao TEXT NOT NULL,
            horario TEXT NOT NULL,
            enviado INTEGER DEFAULT 0,
            criado_em TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def salvar_mensagem(usuario_id, papel, mensagem):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO historico (usuario_id, papel, mensagem, criado_em) VALUES (?, ?, ?, ?)",
        (usuario_id, papel, mensagem, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def buscar_historico(usuario_id, limite=10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT papel, mensagem FROM historico WHERE usuario_id = ? ORDER BY id DESC LIMIT ?",
        (usuario_id, limite)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": papel, "content": mensagem} for papel, mensagem in reversed(rows)]

def salvar_tarefa(usuario_id, descricao, prioridade="normal", prazo=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tarefas (usuario_id, descricao, prioridade, prazo, criado_em) VALUES (?, ?, ?, ?, ?)",
        (usuario_id, descricao, prioridade, prazo, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def listar_tarefas(usuario_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT id, descricao, prioridade, prazo FROM tarefas
           WHERE usuario_id = ? AND concluida = 0
           ORDER BY CASE prioridade
               WHEN 'alta' THEN 1
               WHEN 'normal' THEN 2
               WHEN 'baixa' THEN 3
           END""",
        (usuario_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows

def concluir_tarefa(usuario_id, descricao_parcial):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tarefas SET concluida = 1 WHERE usuario_id = ? AND concluida = 0 AND descricao LIKE ?",
        (usuario_id, "%" + descricao_parcial + "%")
    )
    alteradas = cursor.rowcount
    conn.commit()
    conn.close()
    return alteradas > 0

def salvar_lembrete(usuario_id, descricao, horario):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO lembretes (usuario_id, descricao, horario, criado_em) VALUES (?, ?, ?, ?)",
        (usuario_id, descricao, horario, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def listar_lembretes(usuario_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, descricao, horario FROM lembretes WHERE usuario_id = ? AND enviado = 0",
        (usuario_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
