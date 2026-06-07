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

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
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

# --- TELAS ---
if menu == "📦 Estoque":
    st.header("🔎 Dashboard de Estoque")
    df = db.buscar_tudo()
    
    if not df.empty:
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
            df['valor_total'] = df['preco_venda'] * df['quantidade']
            fig_valor = px.pie(df, values='valor_total', names='nome', title="Distribuição de Valor")
            st.plotly_chart(fig_valor, use_container_width=True)
        
        # Giro de Estoque - Lógica melhorada para detectar vendas em qualquer coluna
        st.subheader("🔥 Top 5 Produtos Mais Vendidos")
        df_logs = db.buscar_logs()
        if not df_logs.empty:
            # Procura a palavra "Venda" em qualquer coluna do DataFrame de Logs
            df_logs['temp_str'] = df_logs.apply(lambda row: ' '.join(row.values.astype(str)), axis=1)
            vendas = df_logs[df_logs['temp_str'].str.contains("Venda", case=False, na=False)]
            
            if not vendas.empty:
                # Agrupa e conta
                top_vendas = vendas.groupby('temp_str').size().reset_index(name='contagem').sort_values(by='contagem', ascending=False).head(5)
                fig_giro = px.bar(top_vendas, x='temp_str', y='contagem', title="Produtos com Maior Saída", color='contagem')
                st.plotly_chart(fig_giro, use_container_width=True)
            else:
                st.info("Nenhuma venda registrada ainda nos logs.")
        else:
            st.info("Logs insuficientes para cálculo de giro.")

        limite_baixo = 5 
        baixo_estoque = df[df['quantidade'] <= limite_baixo]
        if not baixo_estoque.empty:
            st.error(f"⚠️ Atenção: {len(baixo_estoque)} produtos com estoque crítico!")
            st.dataframe(baixo_estoque, use_container_width=True)

        st.subheader("Lista Geral de Produtos")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Estoque vazio no momento.")

elif menu == "💰 Financeiro":
    st.header("💰 Visão Financeira")
    df = db.buscar_tudo()
    if not df.empty:
        df['lucro_unitario'] = df['preco_venda'] - df['preco_custo']
        df['lucro_total_estoque'] = df['lucro_unitario'] * df['quantidade']
        
        df['margem_lucro'] = np.where(df['preco_venda'] > 0, 
                                      ((df['preco_venda'] - df['preco_custo']) / df['preco_venda']) * 100, 
                                      0)
        df['margem_lucro'] = df['margem_lucro'].round(2)
        df['margem_lucro'] = df['margem_lucro'].apply(lambda x: f"{x} %")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Venda Total (Estoque)", f"R$ {df['preco_venda'].mul(df['quantidade']).sum():.2f}")
        c2.metric("Capital Investido", f"R$ {df['preco_custo'].mul(df['quantidade']).sum():.2f}")
        c3.metric("Lucro Potencial", f"R$ {df['lucro_total_estoque'].sum():.2f}")
        
        st.write("---")
        st.dataframe(df[['nome', 'preco_venda', 'preco_custo', 'lucro_total_estoque', 'margem_lucro']], use_container_width=True)
        
        st.subheader("📊 Top 5 Produtos por Lucro")
        df_top = df.sort_values(by='lucro_total_estoque', ascending=False).head(5)
        fig_top = px.bar(df_top, x='nome', y='lucro_total_estoque', title="Ranking de Lucratividade", color='lucro_total_estoque')
        st.plotly_chart(fig_top, use_container_width=True)
        
    else:
        st.info("Não há dados financeiros disponíveis.")

elif menu == "➕ Gestão":
    st.header("➕ Gestão de Produtos")
    aba_cadastro, aba_edicao = st.tabs(["Novo Cadastro", "Editar/Excluir"])

    with aba_cadastro:
        with st.form("cadastro", clear_on_submit=True):
            c1, c2 = st.columns(2)
            cod_barras = c1.text_input("Código de Barras")
            nome = c2.text_input("Nome do Produto")
            c3, c4, c5 = st.columns(3)
            marca = c3.text_input("Marca")
            peso = c4.number_input("Peso (g/ml)", 0.0, step=0.001, format="%g")
            categoria = c5.text_input("Categoria")
            espec = st.text_input("Especificação")
            c6, c7, c8 = st.columns(3)
            p_venda = c6.number_input("Preço de Venda (R$)", 0.0, format="%.2f")
            p_custo = c7.number_input("Preço de Custo (R$)", 0.0, format="%.2f")
            ncm = c8.text_input("NCM")
            c9, c10, c11 = st.columns(3)
            qtd = c9.number_input("Qtd Inicial", 0, step=1)
            est_min = c10.number_input("Estoque Mínimo", 0, step=1)
            validade = c11.text_input("Validade (DD/MM/AAAA)")
            fornecedor = st.text_input("Fornecedor")
            local = st.text_input("Localização na Loja")
            status = st.selectbox("Status", ["Ativo", "Inativo"])
            foto = st.file_uploader("Foto do Produto", type=['png', 'jpg', 'jpeg'])

            if st.form_submit_button("Salvar Produto"):
                db.salvar_produto_inteligente(nome, cod_barras, marca, espec, peso, categoria, 
                                            validade, qtd, est_min, fornecedor, p_venda, 
                                            p_custo, ncm, local, status, "")
                st.success("Produto salvo com sucesso!")

    with aba_edicao:
        st.write("Selecione um produto para editar ou excluir:")
        df = db.buscar_tudo()
        
        if not df.empty:
            produto_selecionado = st.selectbox("Escolha o produto:", df['nome'].tolist())
            produto_info = df[df['nome'] == produto_selecionado].iloc[0]
            
            st.write(f"---")
            st.subheader(f"Editando: {produto_info['nome']}")
            
            with st.form("form_edicao"):
                c1, c2 = st.columns(2)
                nome = c1.text_input("Nome do Produto", value=produto_info['nome'])
                cod_barras = c2.text_input("Código de Barras", value=produto_info['codigo_barras'])
                
                c3, c4, c5 = st.columns(3)
                marca = c3.text_input("Marca", value=produto_info['marca'])
                peso = c4.number_input("Peso (g/ml)", value=float(produto_info['peso']), step=0.001, format="%g")
                categoria = c5.text_input("Categoria", value=produto_info['categoria'])
                espec = st.text_input("Especificação", value=produto_info['especificacao'])
                
                c6, c7, c8 = st.columns(3)
                p_venda = c6.number_input("Preço de Venda", value=float(produto_info['preco_venda']), format="%.2f")
                p_custo = c7.number_input("Preço de Custo", value=float(produto_info['preco_custo']), format="%.2f")
                ncm = c8.text_input("NCM", value=produto_info['ncm'])
                
                c9, c10, c11 = st.columns(3)
                qtd = c9.number_input("Qtd Inicial", value=int(produto_info['quantidade']), step=1)
                est_min = c10.number_input("Estoque Mínimo", value=int(produto_info['estoque_minimo']), step=1)
                validade = c11.text_input("Validade", value=produto_info['validade'])
                
                fornecedor = st.text_input("Fornecedor", value=produto_info['fornecedor'])
                local = st.text_input("Localização", value=produto_info['localizacao'])
                status = st.selectbox("Status", ["Ativo", "Inativo"], index=0 if produto_info['status'] == "Ativo" else 1)
                
                if st.form_submit_button("Salvar Alterações"):
                    db.atualizar_produto(int(produto_info['id']), nome, cod_barras, marca, espec, peso, categoria, 
                                       validade, qtd, est_min, fornecedor, p_venda, p_custo, ncm, local, status)
                    st.success(f"Alteração salva! Venda: R${p_venda} | Custo: R${p_custo}")
                    st.rerun()

            st.write("---")
            if st.button("❌ Excluir este produto"):
                db.excluir_produto(int(produto_info['id']))
                st.warning("Produto excluído!")
                st.rerun()
        else:
            st.info("Nenhum produto cadastrado.")

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