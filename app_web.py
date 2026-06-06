import streamlit as st
import database as db
import cv2
import numpy as np
from pyzbar.pyzbar import decode
import requests
import plotly.express as px
import os

st.set_page_config(page_title="IA Luna - ERP", layout="wide")
db.garantir_estrutura()

# --- AUTENTICAÇÃO ---
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False

def tela_login():
    st.title("🔐 IA Luna - Acesso Restrito")
    senha = st.text_input("Digite a senha de acesso:", type="password")
    if st.button("Entrar"):
        if senha == "1234":
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Senha incorreta!")

if not st.session_state.autenticado:
    tela_login()
    st.stop()

# --- SIDEBAR (NAVEGAÇÃO PROFISSIONAL) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100) # Logo genérico
    st.title("IA Luna ERP")
    menu = st.radio("Menu", ["📦 Estoque", "💰 Financeiro", "➕ Gestão", "🛒 Vendas", "📜 Logs", "📷 Leitor"])
    st.divider()
    st.caption("Versão 1.0 - Estável")

# --- FUNÇÕES ---
def ler_codigo(img_bytes):
    try:
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        codigos = decode(img)
        for obj in codigos: return obj.data.decode('utf-8')
    except: return None

def buscar_produto_api(codigo):
    url = f"https://world.openfoodfacts.org/api/v0/product/{codigo}.json"
    try:
        response = requests.get(url, timeout=3)
        data = response.json()
        if data.get("status") == 1: return data["product"].get("product_name", "")
    except: pass
    return ""

# --- TELAS ---
if menu == "📦 Estoque":
    st.header("🔎 Dashboard de Estoque")
    df = db.buscar_tudo()
    
    if not df.empty:
        # Layout de botões melhorado
        c1, c2 = st.columns(2)
        csv = df.to_csv(index=False).encode('utf-8')
        c1.download_button("📥 Exportar CSV", data=csv, file_name='estoque.csv', mime='text/csv')
        if os.path.exists('estoque.db'):
            with open('estoque.db', 'rb') as f:
                c2.download_button("💾 Backup DB", data=f, file_name='estoque.db', mime='application/octet-stream')
        
        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            fig = px.bar(df, x='nome', y='quantidade', title="Volume de Estoque", color='quantidade')
            st.plotly_chart(fig, use_container_width=True)
        with col2:
            df['valor_total'] = df['preco'] * df['quantidade']
            fig_valor = px.pie(df, values='valor_total', names='nome', title="Distribuição de Valor")
            st.plotly_chart(fig_valor, use_container_width=True)
        
        st.subheader("Lista Geral de Produtos")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Estoque vazio no momento.")

elif menu == "💰 Financeiro":
    st.header("💰 Visão Financeira")
    df = db.buscar_tudo()
    if not df.empty:
        df['lucro_unitario'] = df['preco'] - df['preco_referencia']
        df['lucro_total_estoque'] = df['lucro_unitario'] * df['quantidade']
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Venda Total", f"R$ {df['preco'].mul(df['quantidade']).sum():.2f}")
        c2.metric("Custo Total", f"R$ {df['preco_referencia'].mul(df['quantidade']).sum():.2f}")
        c3.metric("Lucro Potencial", f"R$ {df['lucro_total_estoque'].sum():.2f}")
        st.write("---")
        st.dataframe(df[['nome', 'preco', 'preco_referencia', 'lucro_total_estoque']], use_container_width=True)

elif menu == "➕ Gestão":
    st.header("➕ Cadastrar Produto")
    nome_inicial = buscar_produto_api(st.session_state.codigo_lido) if 'codigo_lido' in st.session_state else ""
    with st.form("cadastro"):
        nome = st.text_input("Nome", value=nome_inicial)
        cat = st.text_input("Categoria")
        c1, c2 = st.columns(2)
        preco = c1.number_input("Preço Venda", 0.0)
        ref = c2.number_input("Preço Custo", 0.0)
        qtd = st.number_input("Qtd Inicial", 0, step=1)
        val = st.text_input("Validade")
        if st.form_submit_button("Salvar Produto"):
            db.salvar_produto_inteligente(nome, cat, preco, qtd, val, ref)
            st.success("Produto salvo com sucesso!")

elif menu == "🛒 Vendas":
    st.header("🛒 Registrar Venda")
    df = db.buscar_tudo()
    if not df.empty:
        prod_id = st.selectbox("Selecione o produto:", df['id'].tolist(), format_func=lambda x: df[df['id']==x]['nome'].values[0])
        qtd_venda = st.number_input("Qtd vendida:", 1, step=1)
        if st.button("Confirmar Venda"):
            if db.registrar_venda(prod_id, qtd_venda):
                st.success("Venda registrada!")
                st.rerun()

elif menu == "📜 Logs":
    st.header("📜 Histórico de Ações")
    st.dataframe(db.buscar_logs(), use_container_width=True)

elif menu == "📷 Leitor":
    st.header("📷 Leitor de Código")
    img_file = st.camera_input("Capturar")
    if img_file is not None:
        codigo = ler_codigo(img_file.getvalue())
        if codigo:
            st.session_state.codigo_lido = codigo
            st.success(f"✅ Código {codigo} identificado! Vá para a aba 'Gestão' para cadastrar.")