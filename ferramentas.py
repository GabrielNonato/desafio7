import csv
import json
from datetime import date
from pathlib import Path


PASTA_DADOS = Path(__file__).resolve().parent / "dados"
with (PASTA_DADOS / "servidores.csv").open(encoding="utf-8", newline="") as f:
    SERVIDORES = {row["matricula"]: row for row in csv.DictReader(f)}
with (PASTA_DADOS / "historico_diarias.csv").open(encoding="utf-8", newline="") as f:
    HISTORICO = list(csv.DictReader(f))
with (PASTA_DADOS / "tabela_diarias.json").open(encoding="utf-8") as f:
    TABELA = json.load(f)
with (PASTA_DADOS / "unidades.json").open(encoding="utf-8") as f:
    UNIDADES = json.load(f)


def consultar_cadastro(matricula: str) -> str:
    """Use para localizar o servidor antes de qualquer cálculo.

    Devolve nome, cargo, grupo de diária, unidade e município de sede. Os argumentos
    devem ser uma matrícula com seis dígitos, como "204317". CPF e e-mail não são
    devolvidos para minimizar dados pessoais.
    """
    matricula = str(matricula).strip()
    servidor = SERVIDORES.get(matricula)
    if not servidor:
        return f"Matrícula '{matricula}' não localizada no cadastro."
    return (
        f"Matrícula {matricula}; nome {servidor['nome']}; cargo {servidor['cargo']}; "
        f"grupo_diaria {servidor['grupo_diaria']}; unidade {servidor['unidade']}; "
        f"municipio_sede {servidor['municipio_sede']}."
    )


def consultar_historico_diarias(matricula: str, mes: str) -> str:
    """Use para verificar prestação de contas vencida e diárias já concedidas no mês.

    `matricula` é uma matrícula de seis dígitos, como "204317". `mes` usa AAAA-MM,
    como "2026-11". Devolve os registros relevantes, quantidade já concedida no mês,
    situação da prestação e a indicação de impedimento. Não devolve CPF.
    """
    matricula = str(matricula).strip()
    mes = str(mes).strip()
    if matricula not in SERVIDORES:
        return f"Matrícula '{matricula}' não localizada no histórico."

    vencida = False
    pendentes = []
    historico_servidor = [r for r in HISTORICO if r["matricula"] == matricula]
    for r in historico_servidor:
        if r["prestacao_contas"] == "pendente":
            try:
                vencimento = somar_dias_uteis(date.fromisoformat(r["data_retorno"]),
                                              TABELA["prazo_prestacao_dias_uteis"])
                if vencimento < date.fromisoformat(TABELA["data_da_analise"]):
                    vencida = True
                    pendentes.append(r["pedido"])
            except (TypeError, ValueError):
                continue

    concedidas = 0.0
    for r in historico_servidor:
        if r["data_partida"].startswith(mes):
            concedidas += float(r["quantidade"])
    limite = float(TABELA["limite_mensal_diarias"])
    situacao = "IMPEDIMENTO" if vencida else "sem prestação vencida"
    return (
        f"Matrícula {matricula}; mês {mes}; diárias já concedidas no mês {concedidas:.1f}; "
        f"limite {limite:.1f}; situação das prestações: {situacao}; "
        f"pedidos pendentes vencidos: {', '.join(pendentes) if pendentes else 'nenhum'}."
    )


def calcular_diarias(
    matricula: str,
    data_pedido: str,
    data_partida: str,
    data_retorno: str,
    destino_uf: str,
) -> str:
    """Use após o cadastro para calcular quantidade, antecedência, valor e limite mensal.

    `matricula`, `data_pedido`, `data_partida`, `data_retorno` e `destino_uf`
    devem ser valores presentes no pedido ou complementação. Datas usam AAAA-MM-DD
    e destino_uf usa MT, DF ou outra UF. Devolve quantidade em diárias, valor em reais,
    antecedência em dias corridos e comparação com o limite mensal.
    """
    matricula = str(matricula).strip()
    servidor = SERVIDORES.get(matricula)
    if not servidor:
        return f"Matrícula '{matricula}' não localizada no cadastro."
    try:
        pedido = date.fromisoformat(str(data_pedido).strip())
        partida = date.fromisoformat(str(data_partida).strip())
        retorno = date.fromisoformat(str(data_retorno).strip())
    except ValueError:
        return "Dados incompletos: data ausente ou em formato inválido."

    pernoites = (retorno - partida).days
    if pernoites < 0:
        return "Dados inválidos: data de retorno anterior à partida."
    quantidade = 0.5 if pernoites == 0 else float(pernoites + 0.5)
    antecedencia = (partida - pedido).days

    uf = str(destino_uf).strip().upper()
    classe = "interior_mt" if uf == "MT" else "distrito_federal" if uf == "DF" else "outra_uf"
    grupo = servidor["grupo_diaria"]
    valor_unico = float(TABELA["valores"][grupo][classe])
    valor_total = round(quantidade * valor_unico, 2)

    mes = partida.strftime("%Y-%m")
    concedidas = 0.0
    for r in HISTORICO:
        if r["matricula"] == matricula and r["data_partida"].startswith(mes):
            concedidas += float(r["quantidade"])
    limite = float(TABELA["limite_mensal_diarias"])
    excede = concedidas + quantidade > limite
    return (
        f"Quantidade {quantidade:.1f} diária(s); valor unitário R$ {valor_unico:.2f}; "
        f"valor total R$ {valor_total:.2f}; antecedência {antecedencia} dias corridos; "
        f"diárias do mês {concedidas:.1f} + pedidas {quantidade:.1f} = "
        f"{concedidas + quantidade:.1f}, limite {limite:.1f}; "
        f"limite {'EXCEDIDO' if excede else 'dentro do limite'}."
    )


def consultar_saldo_diarias(unidade: str, valor: float) -> str:
    """Use depois de calcular o valor total das diárias.

    `unidade` é a sigla da unidade do cadastro, como CFF ou CRH. `valor` é o total
    em reais com ponto decimal, como 980.0. Devolve saldo disponível e a indicação
    suficiente ou insuficiente conforme o artigo 8º.
    """
    sigla = str(unidade).strip().upper()
    if sigla not in UNIDADES:
        return f"Unidade '{unidade}' não localizada. Siglas válidas: {', '.join(sorted(UNIDADES))}."
    try:
        pedido = float(valor)
    except (TypeError, ValueError):
        return "Valor inválido para comparação de saldo."
    saldo = float(UNIDADES[sigla]["saldo_diarias"])
    situacao = "suficiente" if saldo >= pedido else "INSUFICIENTE"
    return (
        f"Saldo da unidade {sigla}: R$ {saldo:.2f}. "
        f"Saldo {situacao} para R$ {pedido:.2f} (art. 8º)."
    )


def somar_dias_uteis(inicio: date, dias: int) -> date:
    atual = inicio
    while dias:
        atual = atual.fromordinal(atual.toordinal() + 1)
        if atual.weekday() < 5:
            dias -= 1
    return atual
