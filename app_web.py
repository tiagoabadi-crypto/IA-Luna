import streamlit as st
import database as db
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import requests

st.set_page_config(page_title="IA Luna - ERP", layout="wide")
db.garantir_estrutura()

# 1. Inicializa o estado de página e do código lido
if 'pagina' not in st.session_state:
    st.session_state.pagina = "Estoque"
if 'codigo_lido' not in st.session_state:
    st.session_state.codigo_lido = ""

# Função de leitura
def ler_codigo(img_bytes):
    nparr = np.frombuffer(img_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    codigos = decode(img)
    for obj in codigos:
        return obj.data.decode('utf-8')
    return None

def buscar_produto_api(codigo):
    url = f"https://world.openfoodfacts.org/api/v0/product/{codigo}.json"
    try:
        response = requests.get(url, timeout=3)
        data = response.json()
        if data.get("status") == 1:
            return data["product"].get("product_name", "")
        return ""
    except:
        return ""

st.title("🤖 IA Luna - Gestão Robusta")

# 2. Navegação (Substitui o st.tabs)
opcoes = ["📦 Estoque", "➕ Gestão", "🛒 Vendas", "📜 Logs", "📷 Leitor"]
# Definimos o index baseado na página atual
index_pagina = opcoes.index(st.session_state.pagina)
st.session_state.pagina = st.radio("Navegação", opcoes, horizontal=True, index=index_pagina, label_visibility="collapsed")

# 3. Lógica das Telas
if st.session_state.pagina == "📦 Estoque":
    st.header("🔎 Estoque Atual")
    busca = st.text_input("Buscar produto por nome:")
    df = db.buscar_tudo()
    if not df.empty and busca:
        df = df[df['nome'].str.contains(busca, case=False, na=False)]
    st.dataframe(df, use_container_width=True)

elif st.session_state.pagina == "➕ Gestão":
    st.subheader("Cadastrar Produto")
    nome_inicial = ""
    if st.session_state.codigo_lido:
        st.info(f"📍 Código lido: {st.session_state.codigo_lido}")
        nome_inicial = buscar_produto_api(st.session_state.codigo_lido)
        if st.button("Limpar Código"):
            st.session_state.codigo_lido = ""
            st.rerun()

    with st.form("cadastro"):
        nome = st.text_input("Nome", value=nome_inicial)
        cat = st.text_input("Categoria")
        preco = st.number_input("Preço", 0.0)
        ref = st.number_input("Preço Ref.", 0.0)
        qtd = st.number_input("Qtd", 0, step=1)
        val = st.text_input("Validade")
        
        if st.form_submit_button("Salvar"):
            db.adicionar_produto(nome, cat, preco, qtd, val, ref)
            st.session_state.codigo_lido = ""
            st.success("Produto salvo!")
            st.rerun()

elif st.session_state.pagina == "🛒 Vendas":
    st.header("🛒 Registrar Venda")
    # ... (seu código de vendas aqui)

elif st.session_state.pagina == "📜 Logs":
    st.header("📜 Histórico")
    st.dataframe(db.buscar_logs(), use_container_width=True)

elif st.session_state.pagina == "📷 Leitor":
    st.header("📷 Leitor de Código")
    img_file = st.camera_input("Capturar Código")
    if img_file is not None:
        codigo = ler_codigo(img_file.getvalue())
        if codigo:
            st.session_state.codigo_lido = codigo
            st.success(f"✅ Código {codigo} identificado!")
            # A MÁGICA ACONTECE AQUI:
            st.session_state.pagina = "➕ Gestão" 
            st.rerun()
        else:
            st.warning("❌ Não detectado.")