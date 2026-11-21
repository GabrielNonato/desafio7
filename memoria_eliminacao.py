import sqlite3
from pathlib import Path

from agente_diarias import DB, criar_agente


def nome_db() -> Path:
    return Path(__file__).resolve().parent / "agno_diarias.db"


def apagar_dados_servidor(matricula: str, nome: str) -> dict:
    """Apaga sessões e memórias do titular e prova a remoção em todas as tabelas."""
    agente = criar_agente(update_memory_on_run=True)

    sessions = DB.get_sessions(user_id=matricula)
    session_ids = [s.session_id for s in sessions if getattr(s, "session_id", None)]
    for session_id in session_ids:
        agente.delete_session(session_id=session_id, user_id=matricula)

    if agente.memory_manager is not None:
        agente.memory_manager.clear_user_memories(user_id=matricula)
    else:
        mems = DB.get_user_memories(user_id=matricula)
        ids = [m.memory_id for m in mems if getattr(m, "memory_id", None)]
        if ids:
            DB.delete_user_memories(ids, user_id=matricula)

    banco = sqlite3.connect(nome_db())
    restantes = []
    falhas_verificacao = []
    conferencias_apagadas = 0
    try:
        tabelas = banco.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        if any(table == "conferencias_humanas" for (table,) in tabelas):
            cursor = banco.execute(
                "DELETE FROM conferencias_humanas WHERE matricula = ?", (matricula,)
            )
            conferencias_apagadas = cursor.rowcount
            banco.commit()

        for (table,) in tabelas:
            colunas = banco.execute(f'PRAGMA table_info("{table}")').fetchall()
            for coluna in colunas:
                col = coluna[1]
                for valor in (matricula, nome) if nome else (matricula,):
                    try:
                        rows = banco.execute(
                            f'SELECT COUNT(*) FROM "{table}" WHERE CAST("{col}" AS TEXT) LIKE ?',
                            (f"%{valor}%",),
                        ).fetchone()
                        if rows and rows[0]:
                            restantes.append({"tabela": table, "coluna": col, "valor": valor})
                    except sqlite3.Error as exc:
                        falhas_verificacao.append({
                            "tabela": table,
                            "coluna": col,
                            "erro": type(exc).__name__,
                        })
    finally:
        banco.close()
    return {
        "matricula": matricula,
        "nome": nome,
        "sessoes_apagadas": len(session_ids),
        "conferencias_apagadas": conferencias_apagadas,
        "restos_encontrados": restantes,
        "falhas_verificacao": falhas_verificacao,
        "eliminacao_confirmada": len(restantes) == 0 and len(falhas_verificacao) == 0,
    }


def servir_diligencia_dia_0111():
    return apagar_dados_servidor("206689", "Beatriz Moraes Cunha")


def servidoras_diligencia():
    return [
        apagar_dados_servidor("206689", "Beatriz Moraes Cunha"),
        apagar_dados_servidor("207418", "Carla Regina Souza"),
        apagar_dados_servidor("207481", "Rafael Lima Antunes"),
    ]
