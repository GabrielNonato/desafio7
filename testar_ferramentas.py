from ferramentas import (
    consultar_cadastro,
    consultar_historico_diarias,
    calcular_diarias,
    consultar_saldo_diarias,
)


casos = [
    ("matricula trocada DIA-2026-0112", consultar_cadastro("207481")),
    ("prestacao vencida DIA-2026-0108",
     consultar_historico_diarias("203648", "2026-11")),
    ("meia diaria DIA-2026-0103",
     calcular_diarias("203156", "2026-10-07", "2026-11-05", "2026-11-05", "MT")),
    ("saldo insuficiente DIA-2026-0110",
     consultar_saldo_diarias("CRH", 1800.0)),
]

for nome, saida in casos:
    print(f"[{nome}]")
    print(saida)
