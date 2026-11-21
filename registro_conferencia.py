import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "agno_diarias.db"


def registrar_conferencia(
    numero_pedido: str,
    matricula: str,
    recomendacao_agente: str,
    minuta_editada: str,
    decisao_conferente: str,
    motivo: str,
) -> int:
    """Persiste a decisão humana no SQLite e retorna o identificador do registro."""
    with sqlite3.connect(DB_PATH) as banco:
        banco.execute(
            """
            CREATE TABLE IF NOT EXISTS conferencias_humanas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero_pedido TEXT NOT NULL,
                matricula TEXT NOT NULL,
                recomendacao_agente TEXT NOT NULL,
                minuta_editada TEXT NOT NULL,
                decisao_conferente TEXT NOT NULL,
                motivo TEXT NOT NULL,
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor = banco.execute(
            """
            INSERT INTO conferencias_humanas (
                numero_pedido, matricula, recomendacao_agente, minuta_editada,
                decisao_conferente, motivo
            ) VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                numero_pedido,
                matricula,
                recomendacao_agente,
                minuta_editada,
                decisao_conferente,
                motivo,
            ),
        )
        return int(cursor.lastrowid)
