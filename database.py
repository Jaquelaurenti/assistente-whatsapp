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
            concluida INTEGER DEFAULT 0,
            criado_em TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def salvar_mensagem(usuario_id: str, papel: str, mensagem: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO historico (usuario_id, papel, mensagem, criado_em) VALUES (?, ?, ?, ?)",
        (usuario_id, papel, mensagem, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def buscar_historico(usuario_id: str, limite: int = 10):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT papel, mensagem FROM historico WHERE usuario_id = ? ORDER BY id DESC LIMIT ?",
        (usuario_id, limite)
    )
    rows = cursor.fetchall()
    conn.close()
    return [{"role": papel, "content": mensagem} for papel, mensagem in reversed(rows)]

def salvar_tarefa(usuario_id: str, descricao: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tarefas (usuario_id, descricao, criado_em) VALUES (?, ?, ?)",
        (usuario_id, descricao, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def listar_tarefas(usuario_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, descricao FROM tarefas WHERE usuario_id = ? AND concluida = 0",
        (usuario_id,)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows
