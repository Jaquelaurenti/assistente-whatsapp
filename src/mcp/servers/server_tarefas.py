import sys
import os

# Garante que o root do projeto esteja no path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from mcp.server.fastmcp import FastMCP
from src.database.repository import (
    init_db,
    salvar_tarefa,
    listar_tarefas,
    concluir_tarefa,
    salvar_lembrete,
    listar_lembretes
)

init_db()
mcp = FastMCP("Tarefas e Lembretes")


@mcp.tool()
def salvar_tarefa_tool(usuario_id: str, descricao: str, prioridade: str = "normal", prazo: str = None) -> str:
    """Salva uma nova tarefa para o usuario."""
    salvar_tarefa(usuario_id, descricao, prioridade, prazo)
    prazo_str = f" com prazo em {prazo}" if prazo else ""
    return f"Tarefa salva: '{descricao}' (prioridade: {prioridade}{prazo_str})"


@mcp.tool()
def listar_tarefas_tool(usuario_id: str) -> str:
    """Lista todas as tarefas pendentes do usuario, ordenadas por prioridade."""
    tarefas = listar_tarefas(usuario_id)
    if not tarefas:
        return "Nenhuma tarefa pendente."
    linhas = [f"[ID:{t[0]}] {t[1]} | prioridade: {t[2]}" + (f" | prazo: {t[3]}" if t[3] else "") for t in tarefas]
    return "\n".join(linhas)


@mcp.tool()
def concluir_tarefa_tool(usuario_id: str, descricao_parcial: str) -> str:
    """Marca como concluida a tarefa que contém o texto informado."""
    sucesso = concluir_tarefa(usuario_id, descricao_parcial)
    if sucesso:
        return f"Tarefa contendo '{descricao_parcial}' marcada como concluida!"
    return f"Nenhuma tarefa encontrada com '{descricao_parcial}'."


@mcp.tool()
def salvar_lembrete_tool(usuario_id: str, descricao: str, horario: str) -> str:
    """Salva um lembrete com horario no formato HH:MM."""
    salvar_lembrete(usuario_id, descricao, horario)
    return f"Lembrete salvo: '{descricao}' as {horario}"


@mcp.tool()
def listar_lembretes_tool(usuario_id: str) -> str:
    """Lista todos os lembretes pendentes do usuario."""
    lembretes = listar_lembretes(usuario_id)
    if not lembretes:
        return "Nenhum lembrete pendente."
    linhas = [f"[ID:{l[0]}] {l[1]} as {l[2]}" for l in lembretes]
    return "\n".join(linhas)


if __name__ == "__main__":
    mcp.run()