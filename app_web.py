import streamlit as st
import database as db
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import requests

st.set_page_config(page_title="IA Luna - ERP", layout="wide")
db.garantir_estrutura()

# --- INICIALIZAÇÃO DE ESTADO ---
if 'pagina' not in st.session_state:
    st.session_state.pagina = "📦 Estoque"
if 'codigo_lido' not in st.session_state:
    st.session_state.codigo_lido = ""

# --- FUNÇÕES ---
def ler_codigo(img_bytes):
    try:
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        codigos = decode(img)
        for obj in codigos:
            return obj.data.decode('utf-8')
    except:
        return None
    return None

def buscar_produto_api(codigo):
    url = f"https://world.openfoodfacts.org/api/v0/product/{codigo}.json"
    try:
        response = requests.get(url, timeout=3)
        data = response.json()
        if data.get("status") == 1:
            return data["product"].get("product_name", "")
    except:
        pass
    return ""

st.title("🤖 IA Luna - Gestão Robusta")

# --- NAVEGAÇÃO SEGURA ---
opcoes = ["📦 Estoque", "➕ Gestão", "🛒 Vendas", "📜 Logs", "📷 Leitor"]

# Segurança: Se a página guardada não existir na lista, volta para o início
if st.session_state.pagina not in opcoes:
    st.session_state.pagina = opcoes[0]

# Cria o menu de navegação
st.session_state.pagina = st.radio(
    "Navegação", 
    opcoes, 
    horizontal=True, 
    index=opcoes.index(st.session_state.pagina), 
    label_visibility="collapsed"
)

# --- LÓGICA DAS TELAS ---
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
        st.info(f"📍 Código ativo para cadastro: {st.session_state.codigo_lido}")
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
            st.success("Produto salvo com sucesso!")
            st.rerun()

elif st.session_state.pagina == "🛒 Vendas":
    st.header("🛒 Registrar Venda (Baixa)")
    df = db.buscar_tudo()
    if not df.empty:
        prod_id = st.selectbox("Selecione o produto:", df['id'].tolist(), format_func=lambda x: df[df['id']==x]['nome'].values[0])
        qtd_venda = st.number_input("Quantidade vendida:", 1, step=1)
        if st.button("Confirmar Venda"):
            if db.registrar_venda(prod_id, qtd_venda):
                st.success("Venda registrada!")
                st.rerun()
            else:
                st.error("Estoque insuficiente!")
    else:
        st.write("Estoque vazio.")

elif st.session_state.pagina == "📜 Logs":
    st.header("📜 Histórico")
    st.dataframe(db.buscar_logs(), use_container_width=True)

elif st.session_state.pagina == "📷 Leitor":
    st.header("📷 Leitor de Código")
    img_file = st.camera_input("Capturar")
    if img_file is not None:
        codigo = ler_codigo(img_file.getvalue())
        if codigo:
            st.session_state.codigo_lido = codigo
            st.success(f"✅ Código identificado: {codigo}")
            # Redirecionamento automático
            st.session_state.pagina = "➕ Gestão"
            st.rerun()
        else:
            st.warning("❌ Código não detectado. Tente novamente.")