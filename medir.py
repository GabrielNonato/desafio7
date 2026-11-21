import json
import time
from pathlib import Path

from agente_diarias import executar_instrucao
from barra import PEDIDOS


RAIZ = Path(__file__).resolve().parent
GABARITO = json.loads((RAIZ / "gabarito.json").read_text(encoding="utf-8"))


def somar_uso(metas):
    uso = {}
    campos = (
        "tokens_entrada", "tokens_saida", "tokens_total",
        "tokens_cache_leitura", "tokens_cache_escrita", "tokens_raciocinio",
        "chamadas_modelo", "chamadas_ferramenta",
        "duracao_segundos", "tempo_primeiro_token_segundos", "custo_usd",
    )
    for campo in campos:
        valores = [
            meta.get("uso", {}).get(campo)
            for meta in metas
            if isinstance(meta.get("uso", {}).get(campo), (int, float))
        ]
        uso[campo] = sum(valores) if valores else None

    modelos = {meta.get("uso", {}).get("modelo") for meta in metas}
    provedores = {meta.get("uso", {}).get("provedor") for meta in metas}
    fontes_custo = {meta.get("uso", {}).get("fonte_custo") for meta in metas}
    uso["modelo"] = next(iter(modelos - {None}), None)
    uso["provedor"] = next(iter(provedores - {None}), None)
    uso["fonte_custo"] = next(iter(fontes_custo - {None}), None)
    uso["custo_medio_por_pedido_usd"] = (
        round(uso["custo_usd"] / len(metas), 8)
        if uso["custo_usd"] is not None
        else None
    )
    uso["custo_mensal_estimado_usd"] = (
        round(uso["custo_medio_por_pedido_usd"] * 300, 6)
        if uso["custo_medio_por_pedido_usd"] is not None
        else None
    )
    return uso


def comparar(instrucao, esperado):
    acertos = 0
    campos = ("recomendacao", "quantidade_diarias", "valor_total",
              "exige_autorizacao_superior")
    for campo in campos:
        if getattr(instrucao, campo) == esperado[campo]:
            acertos += 1
    nao_esperados = {v.criterio for v in getattr(instrucao, "verificacoes", []) if v.situacao == "nao_atende"}
    esperado_nao = set(esperado.get("criterios_nao_atendidos", []))
    if nao_esperados == esperado_nao:
        acertos += 1
    return acertos


def medir_rodadas(rodadas=3):
    resultados = []
    for rodada in range(1, rodadas + 1):
        inicio = time.perf_counter()
        pontos = 0
        casos = 0
        falhas_status = 0
        detalhes = {}
        metas = []
        for numero in PEDIDOS:
            instrucao, meta = executar_instrucao(numero)
            metas.append(meta)
            pontos += comparar(instrucao, GABARITO["pedidos"][numero])
            casos += 5
            if meta["status"] != "success":
                falhas_status += 1
            detalhes[numero] = instrucao.recomendacao
        for numero in ("DIA-2026-0111", "DIA-2026-0112"):
            instrucao, meta = executar_instrucao(numero, complementar=True)
            metas.append(meta)
            pontos += comparar(instrucao, GABARITO["complementacoes"][numero])
            casos += 5
            detalhes[numero + "-complementacao"] = instrucao.recomendacao
        duracao = time.perf_counter() - inicio
        resultados.append({
            "rodada": rodada,
            "acertos": pontos,
            "casos": casos,
            "percentual": round(pontos * 100 / casos, 2),
            "tempo_segundos": round(duracao, 3),
            "falhas_status": falhas_status,
            "detalhes": detalhes,
            "uso": somar_uso(metas),
        })
    return resultados


if __name__ == "__main__":
    saida = medir_rodadas()
    pasta = RAIZ / "resultados"
    pasta.mkdir(exist_ok=True)
    (pasta / "medicoes.json").write_text(json.dumps(saida, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(saida, ensure_ascii=False, indent=2))
