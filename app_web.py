import streamlit as st
import database as db
import cv2
import numpy as np
from pyzbar.pyzbar import decode

st.set_page_config(page_title="IA Luna - ERP", layout="wide")

# Garante que o banco exista
db.garantir_estrutura()

st.title("🤖 IA Luna - Gestão Robusta")

def ler_codigo(img_bytes):
    try:
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return None
        codigos = decode(img)
        for obj in codigos:
            return obj.data.decode('utf-8')
    except Exception as e:
        st.error(f"Erro na leitura: {e}")
    return None

tab1, tab2, tab3, tab4, tab5 = st.tabs(["📦 Estoque", "➕ Gestão", "🛒 Vendas", "📜 Logs", "📷 Leitor"])

with tab1:
    st.header("🔎 Estoque Atual")
    busca = st.text_input("Buscar produto por nome:")
    df = db.buscar_tudo()
    if not df.empty and busca:
        df = df[df['nome'].str.contains(busca, case=False, na=False)]
    st.dataframe(df, use_container_width=True)

with tab2:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Cadastrar Produto")
        with st.form("cadastro"):
            nome = st.text_input("Nome")
            cat = st.text_input("Categoria")
            preco = st.number_input("Preço", 0.0)
            ref = st.number_input("Preço Ref.", 0.0)
            qtd = st.number_input("Qtd", 0, step=1)
            val = st.text_input("Validade")
            if st.form_submit_button("Salvar"):
                db.adicionar_produto(nome, cat, preco, qtd, val, ref)
                st.rerun()

with tab5:
    st.header("📷 Leitor de Código")
    img_file = st.camera_input("Capturar")
    if img_file is not None:
        codigo_lido = ler_codigo(img_file.getvalue())
        if codigo_lido:
            st.success(f"✅ Código: {codigo_lido}")
        else:
            st.warning("❌ Código não detectado.")

# (Mantenha o restante das suas abas tab3 e tab4 exatamente como você já tinha)