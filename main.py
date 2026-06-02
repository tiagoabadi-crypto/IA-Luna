import pandas as pd
import os

# --- Configurações Iniciais ---
FILE_NAME = 'estoque.csv'
COLUNAS = ['id', 'nome', 'categoria', 'preco', 'quantidade', 'validade']

# --- Funções do Sistema ---

def inicializar_sistema():
    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame(columns=COLUNAS)
        df.to_csv(FILE_NAME, index=False)
        print("✅ Sistema inicializado.")
    else:
        print(f"📂 Sistema carregado.")

def carregar_estoque():
    return pd.read_csv(FILE_NAME)

def adicionar_produto(nome, categoria, preco, quantidade, validade):
    df = carregar_estoque()
    novo_id = 1 if df.empty else int(df['id'].max()) + 1
    novo_registro = pd.DataFrame({'id': [novo_id], 'nome': [nome], 'categoria': [categoria], 'preco': [preco], 'quantidade': [quantidade], 'validade': [validade]})
    df = pd.concat([df, novo_registro], ignore_index=True)
    df.to_csv(FILE_NAME, index=False)
    print(f"\n✨ Produto '{nome}' (ID: {novo_id}) cadastrado com sucesso!")

def vender_produto(id_produto, qtd_vendida):
    df = carregar_estoque()
    if id_produto not in df['id'].values:
        print("❌ Erro: ID não encontrado.")
        return
    idx = df[df['id'] == id_produto].index[0]
    if df.loc[idx, 'quantidade'] >= qtd_vendida:
        df.loc[idx, 'quantidade'] -= qtd_vendida
        df.to_csv(FILE_NAME, index=False)
        print(f"✅ Venda realizada! Estoque de '{df.loc[idx, 'nome']}' atualizado.")
    else:
        print(f"❌ Erro: Estoque insuficiente.")

def remover_produto(id_produto):
    """Remove um produto do estoque pelo ID."""
    df = carregar_estoque()
    if id_produto not in df['id'].values:
        print("❌ Erro: ID não encontrado.")
        return
    
    # Filtra o DataFrame mantendo todos, menos o que tem o ID escolhido
    df = df[df['id'] != id_produto]
    df.to_csv(FILE_NAME, index=False)
    print(f"🗑️ Produto (ID: {id_produto}) removido com sucesso!")

def menu():
    while True:
        print("\n--- 🤖 IA LUNA - GESTÃO ---")
        print("1. Adicionar Produto")
        print("2. Ver Estoque")
        print("3. Registrar Venda (Baixa)")
        print("4. Remover Produto")
        print("5. Sair")
        
        opcao = input("\nEscolha uma opção: ")
        
        if opcao == "1":
            nome = input("Nome: ")
            cat = input("Categoria: ")
            preco = float(input("Preço: "))
            qtd = int(input("Quantidade: "))
            val = input("Validade (AAAA-MM-DD): ")
            adicionar_produto(nome, cat, preco, qtd, val)
        elif opcao == "2":
            print("\n--- ESTOQUE ATUAL ---")
            print(carregar_estoque())
        elif opcao == "3":
            try:
                id_prod = int(input("Digite o ID do produto para venda: "))
                qtd_venda = int(input("Quantidade a vender: "))
                vender_produto(id_prod, qtd_venda)
            except ValueError:
                print("Por favor, digite números válidos.")
        elif opcao == "4":
            try:
                id_prod = int(input("Digite o ID do produto para REMOVER: "))
                remover_produto(id_prod)
            except ValueError:
                print("ID inválido.")
        elif opcao == "5":
            print("Encerrando a IA Luna. Até logo!")
            break
        else:
            print("Opção inválida.")

if __name__ == "__main__":
    inicializar_sistema()
    menu()
