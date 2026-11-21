import json
import streamlit as st

from agente_diarias import executar_instrucao
from barra import PEDIDOS
from memoria_eliminacao import apagar_dados_servidor
from registro_conferencia import registrar_conferencia


st.set_page_config(page_title="Instrução de Pedidos de Diárias", layout="wide")
st.title("Instrução de Pedidos de Diárias")

numero = st.selectbox("Pedido", list(PEDIDOS))
pedido = PEDIDOS[numero]

with st.expander("Pedido protocolado", expanded=True):
    st.json(pedido)

if "resultado" not in st.session_state:
    st.session_state.resultado = None

if st.button("Instruir pedido"):
    instrucao, meta = executar_instrucao(numero)
    st.session_state.resultado = (instrucao, meta)

resultado = st.session_state.resultado
if resultado:
    instrucao, meta = resultado
    if meta["status"] != "success":
        st.error("Não foi possível concluir a instrução. O caso voltou para análise manual.")
        st.stop()

    st.subheader("Recomendação")
    st.write(instrucao.recomendacao)
    col1, col2 = st.columns(2)
    col1.metric("Quantidade", "-" if instrucao.quantidade_diarias is None else str(instrucao.quantidade_diarias))
    col2.metric("Valor", "-" if instrucao.valor_total is None else f"R$ {instrucao.valor_total:.2f}")

    st.subheader("Verificações")
    for item in instrucao.verificacoes:
        st.markdown(f"**{item.criterio}** — {item.situacao}")
        st.caption(item.detalhe)

    st.subheader("Alertas")
    st.write(instrucao.alertas or ["Nenhum alerta"])
    st.subheader("Pendências")
    st.write(instrucao.pendencias or ["Nenhuma pendência"])

    st.subheader("Consultas utilizadas")
    st.code(json.dumps({
        "consultar_cadastro": pedido["matricula"],
        "consultar_historico_diarias": {"matricula": pedido["matricula"], "mes": pedido["data_partida"][:7]},
        "calcular_diarias": {
            "matricula": pedido["matricula"],
            "data_pedido": pedido["data_pedido"],
            "data_partida": pedido["data_partida"],
            "data_retorno": pedido["data_retorno"],
            "destino_uf": pedido["destino_uf"],
        },
    }, ensure_ascii=False, indent=2))

    minuta = st.text_area("Minuta do despacho", instrucao.minuta_despacho, height=180)
    decisao = st.selectbox("Encaminhamento decidido pelo servidor",
                           ["deferir", "indeferir", "devolver em diligência", "discorda da sugestão"])
    motivo = st.text_area("Motivo da decisão ou divergência", "")
    if st.button("Registrar conferência humana"):
        registro_id = registrar_conferencia(
            numero_pedido=numero,
            matricula=pedido["matricula"],
            recomendacao_agente=instrucao.recomendacao,
            minuta_editada=minuta,
            decisao_conferente=decisao,
            motivo=motivo,
        )
        st.success(f"Conferência registrada no SQLite (registro {registro_id}).")

    if instrucao.recomendacao == "diligencia":
        complementacao = st.text_area("Complementação")
        if st.button("Enviar complementação na mesma sessão"):
            instrucao2, meta2 = executar_instrucao(numero, complementar=True)
            if meta2["status"] == "success":
                st.session_state.resultado = (instrucao2, meta2)
                st.rerun()

st.divider()
st.subheader("Eliminação de dados")
matricula_eliminar = st.text_input("Matrícula do titular")
nome_eliminar = st.text_input("Nome do titular")
if st.button("Eliminar sessões e memórias"):
    resultado = apagar_dados_servidor(matricula_eliminar.strip(), nome_eliminar.strip())
    st.json(resultado)
