# LEIA-ME

## Executar

```powershell
py -m pip install agno openai python-dotenv pydantic streamlit "sqlalchemy[asyncio]"
py testar_ferramentas.py
py medir.py
py medir_memoria.py
py -m streamlit run app.py
```

Copie `.env.example` para `.env` e informe somente se desejar usar a API. Sem chave,
o projeto usa o cálculo determinístico para permitir teste integral, medição e demonstração.
Para custo por cálculo a partir dos preços conhecidos, configure também:
`MODEL_INPUT_USD_PER_MILLION`, `MODEL_OUTPUT_USD_PER_MILLION` e
`MODEL_CACHE_READ_USD_PER_MILLION`.

## Arquivos principais

- `ferramentas.py`: quatro consultas sobre o acervo.
- `schemas.py`: contrato Pydantic.
- `agente_diarias.py`: Agno, guardrail, limites e fallback determinístico.
- `barra.py`: barreira contra dados inventados.
- `memoria_eliminacao.py`: eliminação LGPD do banco de trabalho.
- `medir.py`: três rodadas contra o gabarito.
- `medir.py`: também agrega tokens, cache, chamadas ao modelo/ferramentas e custo por rodada.
- `medir_memoria.py`: compara memória desligada, histórico da sessão e memória do usuário.
- `app.py`: formulário Streamlit.

## Decisões técnicas

1. Chamadas paralelas: desligadas, porque cadastro, cálculo e saldo são dependentes.
2. Teto: `tool_call_limit=8`, suficiente para quatro consultas principais e eventuais reconsultas.
3. Memória: sessões por número do pedido, `user_id` pela matrícula e
   `num_history_runs=2` no modo com histórico. A medição separa explicitamente os três modos.
4. Modelo: `gpt-5.6-luna`, `reasoning_effort="none"` e `telemetry=False`.

Os resultados são gravados em `resultados/medicoes.json` e `resultados/memoria.json`.
Cada execução real registra métricas na própria meta retornada pelo agente; a API pode
fornecer custo diretamente, ou o projeto calcula custo a partir dos preços configurados.

## Como impedir dado inventado

A barreira verifica todas as matrículas e datas usadas pelas ferramentas contra o pedido
original ou a complementação. A instrução usa Pydantic, status da API e ferramentas para
contas aritméticas. Qualquer recusa ou erro mostra uma mensagem padrão na tela e não
entrega conteúdo recusado.

## Dados guardados e eliminação

O banco `agno_diarias.db` guarda sessões, execuções, identificadores, eventuais memórias
e a decisão humana, incluindo minuta editada e motivo, na tabela `conferencias_humanas`.
A retenção é de trabalho e não há prazo automático por TTL.

A rotina de eliminação apaga sessões, memórias e conferências associadas à matrícula.
Depois verifica as tabelas SQLite procurando matrícula e nome. A confirmação só é
positiva se não houver restos nem falhas de verificação; consulte `eliminacao_confirmada`
e `falhas_verificacao` no resultado. O banco de trabalho não substitui o registro público
ou histórico legal das diárias.

## Respostas às perguntas de projeto

### 1. Chamadas paralelas, teto de chamadas e memória

As chamadas paralelas foram desativadas porque o cadastro, o cálculo e o saldo são
dependentes: o cálculo requer o cadastro e a consulta de saldo depende do valor calculado.
O teto foi escolhido em `tool_call_limit=8`, mais que o suficiente para as quatro consultas
ferramentais principais e eventuais reconsultas. A escolha é baseada nas quatro ferramentas
principais e em folga para erros ou verificações adicionais.

No modo padrão, a sessão usa até dois turnos anteriores com `num_history_runs=2`.
`medir_memoria.py` separa três configurações: sem memória, somente histórico da sessão
e histórico da sessão mais memórias do usuário.

### 2. Impedimento de dados inventados

O agente recebe somente o pedido e usa ferramentas para obter cadastro, histórico,
cálculo e saldo. A barreira `verificar_chamada` confere matrícula e datas contra o pedido
ou sua complementação antes de permitir argumentos das ferramentas. Matrículas ou datas
não presentes são recusadas.

As ferramentas realizam cálculos aritméticos; o modelo não recebe o encargo de calcular
dados. A resposta é limitada pelo esquema Pydantic `Instrucao`. O guardrail também mascara
CPF e dados bancários. Nenhum desses mecanismos torna a verificação uma garantia absoluta,
mas impede que conclusões sejam construídas com argumentos conhecidos como fora do caso.

### 3. Dados do servidor, retenção e eliminação

O banco `agno_diarias.db` pode guardar identificadores da sessão, `session_id`, `user_id`,
pedido enviado, respostas, execuções, histórico recente e, no modo com memória, memórias
do usuário. As memórias estão ligadas à matrícula usada como `user_id`; os dados pessoais
não devem permanecer além da finalidade de trabalho, mas não há prazo automático definido
por TTL no código atual. Portanto, a retenção é até eliminação pelo titular ou pela
operação administrativa correspondente.

O titular pode solicitar a eliminação por meio de `apagar_dados_servidor(matricula, nome)`.
A rotina apaga as sessões do usuário, limpa suas memórias e verifica todas as tabelas
SQLite procurando a matrícula e o nome. `servidoras_diligencia()` oferece a operação para
os servidores de diligência do acervo. O banco de trabalho não substitui os registros
públicos ou históricos legais das diárias.
