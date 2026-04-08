import sqlite3
from datetime import datetime

DB_PATH = "assistente.db"


# 🔥 conexão padronizada
def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
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

    # 🔥 índices (muito importante)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuario_historico ON historico(usuario_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuario_tarefas ON tarefas(usuario_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_usuario_lembretes ON lembretes(usuario_id)")

    conn.commit()
    conn.close()


def salvar_mensagem(usuario_id, papel, mensagem):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO historico (usuario_id, papel, mensagem, criado_em) VALUES (?, ?, ?, ?)",
        (usuario_id, papel, mensagem, datetime.now().isoformat())
    )

    conn.commit()
    conn.close()


def buscar_historico(usuario_id, limite=10):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT papel, mensagem FROM historico
           WHERE usuario_id = ?
           ORDER BY id DESC
           LIMIT ?""",
        (usuario_id, limite)
    )

    rows = cursor.fetchall()
    conn.close()

    # 🔥 já retorna no formato correto
    return [
        {"role": row["papel"], "content": row["mensagem"]}
        for row in reversed(rows)
    ]


def salvar_tarefa(usuario_id, descricao, prioridade="normal", prazo=None):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO tarefas
           (usuario_id, descricao, prioridade, prazo, criado_em)
           VALUES (?, ?, ?, ?, ?)""",
        (usuario_id, descricao, prioridade, prazo, datetime.now().isoformat())
    )

    conn.commit()
    conn.close()


def listar_tarefas(usuario_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT id, descricao, prioridade, prazo
           FROM tarefas
           WHERE usuario_id = ? AND concluida = 0
           ORDER BY CASE prioridade
               WHEN 'alta' THEN 1
               WHEN 'normal' THEN 2
               WHEN 'baixa' THEN 3
           END"""
        ,
        (usuario_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        (row["id"], row["descricao"], row["prioridade"], row["prazo"])
        for row in rows
    ]


# 🔥 MELHORADO: evita concluir várias tarefas sem querer
def concluir_tarefa(usuario_id, descricao_parcial):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT id FROM tarefas
           WHERE usuario_id = ?
           AND concluida = 0
           AND descricao LIKE ?
           LIMIT 1""",
        (usuario_id, f"%{descricao_parcial}%")
    )

    tarefa = cursor.fetchone()

    if not tarefa:
        conn.close()
        return False

    cursor.execute(
        "UPDATE tarefas SET concluida = 1 WHERE id = ?",
        (tarefa["id"],)
    )

    conn.commit()
    conn.close()

    return True


def salvar_lembrete(usuario_id, descricao, horario):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """INSERT INTO lembretes
           (usuario_id, descricao, horario, criado_em)
           VALUES (?, ?, ?, ?)""",
        (usuario_id, descricao, horario, datetime.now().isoformat())
    )

    conn.commit()
    conn.close()


def listar_lembretes(usuario_id):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """SELECT id, descricao, horario
           FROM lembretes
           WHERE usuario_id = ? AND enviado = 0"""
        ,
        (usuario_id,)
    )

    rows = cursor.fetchall()
    conn.close()

    return [
        (row["id"], row["descricao"], row["horario"])
        for row in rows
    ]