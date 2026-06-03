import pandas as pd
import os

FILE_NAME = 'estoque.csv'
COLUNAS = ['id', 'nome', 'categoria', 'preco', 'quantidade', 'validade']

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def input_numerico(mensagem, tipo):
    while True:
        try:
            valor = tipo(input(mensagem))
            if valor < 0:
                print("⚠️  Por favor, digite um valor positivo.")
                continue
            return valor
        except ValueError:
            print("❌ Entrada inválida. Digite apenas números.")

def inicializar_sistema():
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=COLUNAS)
        df.to_csv(FILE_NAME, index=False)

def carregar_estoque():
    return pd.read_csv(FILE_NAME)

def verificar_alertas(df):
    baixo_estoque = df[df['quantidade'] < 5]
    if not baixo_estoque.empty:
        print("\n⚠️  ATENÇÃO: PRODUTOS COM ESTOQUE BAIXO:")
        for _, produto in baixo_estoque.iterrows():
            print(f"   -> {produto['nome']} (ID: {produto['id']}) - Restam: {produto['quantidade']}")

def adicionar_produto(nome, categoria, preco, quantidade, validade):
    df = carregar_estoque()
    novo_id = 1 if df.empty else int(df['id'].max()) + 1
    novo_registro = pd.DataFrame({'id': [novo_id], 'nome': [nome], 'categoria': [categoria], 'preco': [preco], 'quantidade': [quantidade], 'validade': [validade]})
    df = pd.concat([df, novo_registro], ignore_index=True)
    df.to_csv(FILE_NAME, index=False)
    print(f"\n✨ Produto '{nome}' cadastrado!")

def vender_produto(id_produto, qtd_vendida):
    df = carregar_estoque()
    if id_produto not in df['id'].values:
        print("❌ ID não encontrado.")
        return
    idx = df[df['id'] == id_produto].index[0]
    if df.loc[idx, 'quantidade'] >= qtd_vendida:
        df.loc[idx, 'quantidade'] -= qtd_vendida
        df.to_csv(FILE_NAME, index=False)
        print(f"✅ Venda realizada!")
    else:
        print(f"❌ Estoque insuficiente.")

def remover_produto(id_produto):
    df = carregar_estoque()
    if id_produto not in df['id'].values:
        print("❌ ID não encontrado.")
        return
    df = df[df['id'] != id_produto]
    df.to_csv(FILE_NAME, index=False)
    print(f"🗑️ Produto removido!")

def exibir_relatorio_financeiro():
    df = carregar_estoque()
    if df.empty:
        print("\nEstoque vazio. Nada a calcular.")
    else:
        df['total_item'] = df['preco'] * df['quantidade']
        total_geral = df['total_item'].sum()
        
        print("\n--- 📊 RELATÓRIO FINANCEIRO ---")
        print(df[['nome', 'total_item']])
        print("-" * 30)
        print(f"💰 VALOR TOTAL DO ESTOQUE: R$ {total_geral:.2f}")

def menu():
    while True:
        limpar_tela() 
        print("--- 🤖 IA LUNA - GESTÃO ROBUSTA ---")
        print("1. Adicionar Produto")
        print("2. Ver Estoque")
        print("3. Registrar Venda (Baixa)")
        print("4. Remover Produto")
        print("5. Relatório Financeiro")
        print("6. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            nome = input("Nome: ").strip()
            cat = input("Categoria: ").strip()
            preco = input_numerico("Preço: ", float)
            qtd = input_numerico("Quantidade: ", int)
            val = input("Validade (AAAA-MM-DD): ").strip()
            adicionar_produto(nome, cat, preco, qtd, val)
        elif opcao == "2":
            print("\n--- ESTOQUE ATUAL ---")
            df = carregar_estoque()
            print(df)
            verificar_alertas(df)
            input("\nPressione ENTER para voltar...")
        elif opcao == "3":
            id_prod = input_numerico("ID do produto: ", int)
            qtd_venda = input_numerico("Quantidade a vender: ", int)
            vender_produto(id_prod, qtd_venda)
            input("\nPressione ENTER para continuar...")
        elif opcao == "4":
            id_prod = input_numerico("ID para REMOVER: ", int)
            remover_produto(id_prod)
            input("\nPressione ENTER para continuar...")
        elif opcao == "5":
            exibir_relatorio_financeiro()
            input("\nPressione ENTER para voltar...")
        elif opcao == "6":
            break

if __name__ == "__main__":
    inicializar_sistema()
    menu()