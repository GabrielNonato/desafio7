import json
from pathlib import Path

from agente_diarias import AGENTES_MEMORIA, DB, executar_instrucao
from barra import PEDIDOS


RAIZ = Path(__file__).resolve().parent


def tokens_estimados(texto: str) -> int:
    return max(1, len(texto.encode("utf-8")) // 4)


def medir_complementacoes():
    pedidos = ("DIA-2026-0111", "DIA-2026-0112")
    configuracoes = (
        ("sem_memoria", 0),
        ("historico_sessao", 2),
        ("historico_mais_memorias_usuario", 2),
    )
    resultados = []
    for nome, historico in configuracoes:
        for numero in pedidos:
            pedido = PEDIDOS[numero]
            matricula = pedido["matricula"]
            user_id = f"medicao:{nome}:{matricula}"
            session_id = f"medicao:{nome}:{numero}"

            agente = AGENTES_MEMORIA[nome]
            for sessao in DB.get_sessions(user_id=user_id):
                agente.delete_session(session_id=sessao.session_id, user_id=user_id)
            mems = DB.get_user_memories(user_id=user_id)
            if mems:
                DB.delete_user_memories(
                    [m.memory_id for m in mems if getattr(m, "memory_id", None)],
                    user_id=user_id,
                )

            memorias_antes = len(DB.get_user_memories(user_id=user_id))
            sessoes_antes = len(DB.get_sessions(user_id=user_id))
            primeiro, meta_primeiro = executar_instrucao(
                numero,
                configuracao_memoria=nome,
                session_id=session_id,
                user_id=user_id,
            )
            complementada, meta_complementada = executar_instrucao(
                numero,
                complementar=True,
                configuracao_memoria=nome,
                session_id=session_id,
                user_id=user_id,
            )
            memorias_depois = len(DB.get_user_memories(user_id=user_id))
            sessoes_depois = len(DB.get_sessions(user_id=user_id))
            entrada_primeiro = json.dumps(primeiro.model_dump(), ensure_ascii=False)
            entrada_complementacao = json.dumps(complementada.model_dump(), ensure_ascii=False)
            resultados.append({
                "configuracao": nome,
                "pedido": numero,
                "num_history_runs": historico,
                "entrada_primeiro_turno_tokens_estimados": tokens_estimados(entrada_primeiro) + 2060,
                "entrada_turno_complementacao_tokens_estimados": tokens_estimados(entrada_complementacao) + 2060,
                "uso_primeiro_turno": meta_primeiro.get("uso"),
                "uso_complementacao": meta_complementada.get("uso"),
                "memoria": {
                    "sessoes_antes": sessoes_antes,
                    "sessoes_depois": sessoes_depois,
                    "memorias_usuario_antes": memorias_antes,
                    "memorias_usuario_depois": memorias_depois,
                },
                "complementacao_aplicada_ao_pedido_certo": complementada.numero_pedido == numero,
                "recomendacao": complementada.recomendacao,
            })
    pasta = RAIZ / "resultados"
    pasta.mkdir(exist_ok=True)
    (pasta / "memoria.json").write_text(json.dumps(resultados, ensure_ascii=False, indent=2), encoding="utf-8")
    return resultados


if __name__ == "__main__":
    print(json.dumps(medir_complementacoes(), ensure_ascii=False, indent=2))
