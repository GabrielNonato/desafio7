# Desenho do processo

## Processo manual atual

1. Registrar o pedido e conferir se os dados obrigatórios estão presentes.
2. Consultar o cadastro funcional e confirmar matrícula, nome, cargo, grupo e unidade.
3. Consultar o histórico do mês e de prestações de contas.
4. Conferir antecedência mínima e eventual urgência com autorização escrita.
5. Calcular pernoites, meias diárias e o valor pela tabela.
6. Somar diárias já concedidas no mês e verificar o limite.
7. Comparar o valor com o saldo da unidade.
8. Preparar recomendação e minuta.
9. O servidor conferente corrige ou encaminha ao ordenador de despesa.

## Processo do agente

1. Receber o pedido e mascarar CPF e dados bancários antes do modelo.
2. Consultar cadastro, histórico e calcular diárias.
3. Consultar saldo após o cálculo.
4. Aplicar a barreira de argumentos contra o pedido/complementação.
5. Validar o Pydantic e montar o formulário.
6. Retornar a recomendação sem decidir; a pessoa faz a conferência.
7. Em diligência, receber complementação na mesma sessão.

## Quadro PEAS

- **Performance:** acerto comparado com o gabarito em recomendação, quantidade, valor,
  autorização superior e critérios não atendidos. Tempo, tokens reais, cache,
  chamadas ao modelo/ferramentas e custo também são medidos.
- **Environment:** pedidos JSON, cadastro CSV, histórico CSV, tabela JSON, unidade JSON,
  complemento JSON e banco SQLite local.
- **Actuators:** quatro ferramentas de consulta/cálculo, objeto Pydantic, minuta editável,
  registro da decisão humana e rotina de eliminação.
- **Sensors:** número, matrícula, nome, datas, UF, destino, justificativa e complementação.

## Confiabilidade composta e custo

Com cinco chamadas ao modelo ou etapas encadeadas:

- 95% por passo: `0.95^5 = 77,4%`.
- 99% por passo: `0.99^5 = 95,1%`.

A estimativa histórica prevê entrada inicial de cerca de 2060 tokens e acréscimo de
90 a 150 tokens por passo. Ela não substitui a medição real.
`medir.py` registra os tokens fornecidos pela resposta da API; `medir_memoria.py`
mantém uma estimativa complementar e registra o uso efetivo de cada turno.

O volume mensal adotado para o piloto é 300 pedidos.

## Reversibilidade e detecção

Irreversível na origem (o pagamento diário pode ser considerado despesa indevida) e
detectável tarde (auditoria posterior). Portanto, o processo fica no quadrante inferior
direito: “agente apenas aconselha”, prepara a minuta e exige assinatura humana.
