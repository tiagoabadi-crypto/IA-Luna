import streamlit as st
import database as db
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import requests
import plotly.express as px  # Nova biblioteca

st.set_page_config(page_title="IA Luna - ERP", layout="wide")
db.garantir_estrutura()

# --- ESTADO INICIAL ---
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

# --- NAVEGAÇÃO ---
opcoes = ["📦 Estoque", "➕ Gestão", "🛒 Vendas", "📜 Logs", "📷 Leitor"]
if st.session_state.pagina not in opcoes:
    st.session_state.pagina = opcoes[0]

st.session_state.pagina = st.radio(
    "Navegação", opcoes, horizontal=True, index=opcoes.index(st.session_state.pagina), label_visibility="collapsed"
)

# --- TELAS ---
if st.session_state.pagina == "📦 Estoque":
    st.header("🔎 Dashboard e Estoque")
    df = db.buscar_tudo()
    
    if not df.empty:
        # --- NOVO: Dashboard de Inteligência ---
        col1, col2 = st.columns(2)
        
        with col1:
            # Gráfico de Quantidade por Produto
            fig = px.bar(df, x='nome', y='quantidade', title="Volume de Estoque por Produto", color='quantidade')
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            # Cálculo de valor aproximado (Preço * Quantidade)
            df['valor_total'] = df['preco'] * df['quantidade']
            fig_valor = px.pie(df, values='valor_total', names='nome', title="Distribuição de Valor em Estoque")
            st.plotly_chart(fig_valor, use_container_width=True)
        
        # --- Alerta de Estoque Crítico ---
        limite_baixo = 5 
        baixo_estoque = df[df['quantidade'] <= limite_baixo]
        if not baixo_estoque.empty:
            st.error(f"⚠️ Atenção: {len(baixo_estoque)} produtos com estoque crítico!")
            st.dataframe(baixo_estoque, use_container_width=True)
            st.divider()

        st.subheader("Lista Geral")
        st.dataframe(df, use_container_width=True)
    else:
        st.write("Estoque vazio.")

elif st.session_state.pagina == "➕ Gestão":
    # ... (Seu código de gestão permanece o mesmo)
    st.subheader("Cadastrar Produto")
    nome_inicial = ""
    if st.session_state.codigo_lido:
        st.info(f"📍 Código ativo: {st.session_state.codigo_lido}")
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
            db.salvar_produto_inteligente(nome, cat, preco, qtd, val, ref)
            st.session_state.codigo_lido = ""
            st.success("Produto salvo!")
            st.rerun()

elif st.session_state.pagina == "🛒 Vendas":
    # ... (Seu código de Vendas permanece o mesmo)
    st.header("🛒 Registrar Venda")
    df = db.buscar_tudo()
    if not df.empty:
        prod_id = st.selectbox("Selecione o produto:", df['id'].tolist(), format_func=lambda x: df[df['id']==x]['nome'].values[0])
        qtd_venda = st.number_input("Qtd vendida:", 1, step=1)
        if st.button("Confirmar Venda"):
            if db.registrar_venda(prod_id, qtd_venda):
                st.success("Venda registrada!")
                st.rerun()
            else:
                st.error("Estoque insuficiente!")

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
            st.success(f"✅ Código {codigo} identificado!")
            st.session_state.pagina = "➕ Gestão"
            st.rerun()