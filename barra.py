import json
from pathlib import Path
from typing import Any


RAIZ = Path(__file__).resolve().parent
with (RAIZ / "dados" / "pedidos.json").open(encoding="utf-8") as f:
    PEDIDOS = {p["numero"]: p for p in json.load(f)}
with (RAIZ / "dados" / "complementacoes.json").open(encoding="utf-8") as f:
    COMPLEMENTACOES = {c["numero"]: c for c in json.load(f)}


def pedido_corrente(numero: str, complementar: bool = False) -> dict:
    pedido = dict(PEDIDOS[numero])
    if complementar and numero in COMPLEMENTACOES:
        texto = COMPLEMENTACOES[numero]["texto"]
        pedido["_complementacao"] = texto
        if numero == "DIA-2026-0111":
            pedido["data_retorno"] = "2026-11-20"
        if numero == "DIA-2026-0112":
            pedido["matricula"] = "207418"
    return pedido


def verificar_chamada(
    numero_pedido: str,
    ferramenta: str,
    argumentos: dict[str, Any],
    complementar: bool = False,
) -> tuple[bool, str]:
    pedido = pedido_corrente(numero_pedido, complementar)
    matricula = str(argumentos.get("matricula", "")).strip()
    if matricula:
        matr_validas = {pedido["matricula"]}
        if complementar:
            original = PEDIDOS[numero_pedido]["matricula"]
            matr_validas.add(original)
        if matricula not in matr_validas:
            return False, f"Matrícula {matricula} não pertence ao pedido {numero_pedido}."

    for chave in ("data_pedido", "data_partida", "data_retorno"):
        if chave in argumentos:
            valor = argumentos[chave]
            permitido = pedido.get(chave)
            original = PEDIDOS[numero_pedido].get(chave)
            if valor not in (permitido, original):
                return False, f"Data {chave} não consta do pedido ou complementação."
    return True, "Argumentos conferem."
