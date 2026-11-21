# Documentação do projeto

## Apresentação

O projeto instrui pedidos hipotéticos de diárias de servidores e entrega uma
recomendação para conferência humana. O agente consulta cadastro e histórico,
calcula quantidade e valor conforme a norma fictícia e confere o saldo da unidade.
Ele não decide a concessão: a decisão final permanece com o servidor conferente e
o ordenador de despesa.

O acervo e os nomes são fictícios. O arquivo `gabarito.json` é calculado por regras
determinísticas em `gerar_dados.py`, sem modelo de linguagem. Ele é usado para avaliar
as respostas e não deve ser enviado ao agente.

## Requisitos

- Python 3.10 ou superior.
- Dependências: `agno`, `openai`, `python-dotenv`, `pydantic`, `streamlit` e
  `sqlalchemy[asyncio]`.
- Uma chave de API é necessária para medir o modelo real. Sem chave, o projeto usa
  o fallback determinístico.
- Para calcular custos quando o provedor não os retorna, configure os preços por
  milhão de tokens no `.env`, conforme `.env.example`.

## Como executar

No PowerShell, na pasta do projeto:

```powershell
py -m pip install agno openai python-dotenv pydantic streamlit "sqlalchemy[asyncio]"
py testar_ferramentas.py
```

Para executar as medições:

```powershell
py medir.py
py medir_memoria.py
```

`medir.py` instrui os doze pedidos e as duas complementações em três rodadas e
compara os resultados com `gabarito.json`. Sem chave, as rodadas usam o fallback
determinístico; para medir o modelo, configure a chave localmente no `.env` antes
de executar.

`medir_memoria.py` compara os modos sem memória, com histórico da sessão e com
histórico mais memórias do usuário, nos dois pedidos que recebem complementação.
Os arquivos gerados são:

- `resultados/medicoes.json`
- `resultados/memoria.json`

Para abrir o formulário:

```powershell
py -m streamlit run app.py
```

No formulário, selecione um pedido, solicite a instrução, edite a minuta e registre
o encaminhamento e o motivo da conferência.

Opcionalmente, `py gerar_dados.py` recria o acervo e o gabarito. Não execute para
apenas medir; o comando sobrescreve os arquivos de dados gerados.

## Componentes e localização dos requisitos

| Requisito ou responsabilidade | Arquivos |
| --- | --- |
| Dados fictícios, doze pedidos, duas complementações e gabarito normativo | `gerar_dados.py`, `dados/`, `gabarito.json` |
| Consultas e contas de cadastro, histórico, diárias e saldo | `ferramentas.py` |
| Contrato estruturado da resposta | `schemas.py` |
| Agente, guardrail PII, limite de ferramentas, status da API e fallback | `agente_diarias.py` |
| Dados válidos de pedidos e complementações | `barra.py` |
| Formulário, minuta editável, decisão humana e mensagens de erro | `app.py` |
| Persistência da conferência no SQLite | `registro_conferencia.py`, `agno_diarias.db` |
| Eliminação e verificação de dados locais | `memoria_eliminacao.py` |
| Comparação com gabarito, uso e custo | `medir.py` |
| Comparação dos modos de memória | `medir_memoria.py` |
| Desenho do processo e resultados narrados | `desenho.md`, `relatorio.md` |

O banco `agno_diarias.db` guarda sessões e execuções do Agno. A tabela
`conferencias_humanas` guarda pedido, matrícula, recomendação, minuta editada,
decisão e motivo. A função `apagar_dados_servidor(matricula, nome)` remove sessões,
memórias e conferências associadas à matrícula e verifica se restaram valores
correspondentes no SQLite.

## Critérios de avaliação

| Critério | Situação | Evidência ou ressalva |
| --- | --- | --- |
| Instruir doze pedidos e duas complementações em rodadas automatizadas | Implementado; medições registradas | `medir.py` e `resultados/medicoes.json`. Os resultados do fallback determinístico não representam desempenho do modelo. |
| Ferramentas documentadas, cálculos, esquema Pydantic, limites e status da API | Implementado | `ferramentas.py`, `schemas.py` e `agente_diarias.py`. |
| Proteção contra argumentos de ferramenta inventados | Parcial | `verificar_chamada` está definida em `barra.py`, mas não está conectada ao ciclo de chamadas de ferramenta do agente. Não se deve apresentar essa barreira como validação efetiva de chamadas do modelo. |
| Memória e identificação das sessões | Implementado para os modos configurados | `agente_diarias.py` e `medir_memoria.py`; as configurações precisam ser executadas com a API para produzir medições reais. |
| Eliminação e comprovação no SQLite | Verificada com registros sintéticos locais | `memoria_eliminacao.py` retorna `eliminacao_confirmada`, `restos_encontrados` e `falhas_verificacao`. O teste não comprova eliminação em sistemas externos ou retenção do provedor. |
| Três rodadas contra o gabarito | Implementado | `medir.py`; consultar os arquivos JSON para saber quais dados foram efetivamente capturados em cada execução. |
| Comparação de chamadas paralelas ligadas e desligadas | Não realizada | O agente está configurado sem chamadas paralelas; não há experimento comparativo registrado. |
| Falhas e casos adversariais | Parcialmente documentados | `relatorio.md` registra matrícula incorreta, dado ausente, ordem embutida, argumento fora do pedido e PII; nem todos são uma suíte automatizada de testes. |
| Formulário com minuta editável e mensagem padrão de erro | Implementado | `app.py`. Não há indicador explícito de progresso da execução. |
| Decisão humana persistida | Implementado | A conferência é salva em `conferencias_humanas` no SQLite por `registro_conferencia.py`. |
| Desenho, aritmética e justificativa da conferência humana | Documentado | `desenho.md` e `relatorio.md` apresentam o fluxo e o motivo para manter decisão humana. |

## Interpretação dos resultados

O relatório registra 100% no modo determinístico e resultados inferiores nas
rodadas com modelo. Esses números são de condições diferentes e devem ser
apresentados separadamente. As estimativas antigas de tokens em `memoria.json`
não são uso real da API.

O código atual registra métricas de tokens, cache, chamadas e custo quando
disponíveis, mas os arquivos existentes só refletem a instrumentação presente
quando foram gerados. Para observar os campos atualizados, execute novamente os
scripts com a chave configurada. Custo calculado com preços do `.env` é uma
estimativa baseada nesses valores; indique a fonte ao apresentar o resultado.

O ponto de conferência humana é necessário porque a recomendação pode conter erro,
o pagamento tem efeito financeiro e o ordenador de despesa conserva a decisão final.
