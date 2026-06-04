import streamlit as st
import database as db

st.set_page_config(page_title="IA Luna - ERP", layout="wide")
db.garantir_estrutura()

st.title("🤖 IA Luna - Gestão Robusta")

tab1, tab2, tab3, tab4 = st.tabs(["📦 Estoque e Busca", "➕ Gestão", "🛒 Vendas", "📜 Logs"])

with tab1:
    st.header("🔎 Estoque Atual")
    busca = st.text_input("Buscar produto por nome:")
    df = db.buscar_tudo()
    if busca:
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
    with col2:
        st.subheader("Remover Produto")
        id_del = st.selectbox("ID para remover:", db.buscar_tudo()['id'].tolist())
        if st.button("Confirmar Remoção"):
            db.remover_produto(id_del)
            st.rerun()

with tab3:
    st.header("🛒 Registrar Venda (Baixa)")
    df = db.buscar_tudo()
    prod_id = st.selectbox("Selecione o produto:", df['id'].tolist(), format_func=lambda x: df[df['id']==x]['nome'].values[0])
    qtd_venda = st.number_input("Quantidade vendida:", 1, step=1)
    if st.button("Confirmar Venda"):
        if db.registrar_venda(prod_id, qtd_venda):
            st.success("Venda registrada com sucesso!")
            st.rerun()
        else:
            st.error("Estoque insuficiente!")

with tab4:
    st.header("📜 Histórico de Logs")
    st.dataframe(db.buscar_logs(), use_container_width=True)
    
    st.header("📊 Relatório Financeiro")
    df = db.buscar_tudo()
    if not df.empty:
        total = (df['preco'] * df['quantidade']).sum()
        st.metric("💰 Valor Total em Estoque", f"R$ {total:,.2f}")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Exportar Relatório (CSV)", csv, "estoque.csv", "text/csv")