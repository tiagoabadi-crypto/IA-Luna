import pandas as pd
import os

# --- Configurações Iniciais ---
FILE_NAME = 'estoque.csv'
COLUNAS = ['id', 'nome', 'categoria', 'preco', 'quantidade', 'validade']

# --- Funções do Sistema ---

def inicializar_sistema():
    """Verifica se o arquivo de estoque existe, se não, cria um vazio."""
    if not os.path.exists(FILE_NAME):
        print(f"🔄 Arquivo '{FILE_NAME}' não encontrado. Criando novo banco de dados...")
        df = pd.DataFrame(columns=COLUNAS)
        df.to_csv(FILE_NAME, index=False)
        print("✅ Sistema inicializado com sucesso.")
    else:
        print(f"📂 Sistema carregado. Arquivo '{FILE_NAME}' encontrado.")

def carregar_estoque():
    """Lê o arquivo CSV e retorna o DataFrame."""
    return pd.read_csv(FILE_NAME)

def adicionar_produto(nome, categoria, preco, quantidade, validade):
    """Adiciona um novo produto ao arquivo CSV."""
    df = carregar_estoque()
    
    # Define o ID automaticamente (se vazio começa em 1, senão pega o maior + 1)
    novo_id = 1 if df.empty else int(df['id'].max()) + 1
    
    # Cria novo registro como um DataFrame
    novo_registro = pd.DataFrame({
        'id': [novo_id],
        'nome': [nome],
        'categoria': [categoria],
        'preco': [preco],
        'quantidade': [quantidade],
        'validade': [validade]
    })
    
    # Concatena o novo produto ao estoque existente
    df = pd.concat([df, novo_registro], ignore_index=True)
    
    # Salva no arquivo CSV
    df.to_csv(FILE_NAME, index=False)
    print(f"✨ Produto '{nome}' (ID: {novo_id}) cadastrado com sucesso!")

# --- Execução Principal ---

if __name__ == "__main__":
    # 1. Preparar o ambiente
    inicializar_sistema()
    
    # 2. Teste rápido: Adicionar um item
    # (Você pode trocar os dados abaixo para testar novos cadastros)
    adicionar_produto("Arroz", "Grãos", 12.50, 100, "2026-12-31")
    
    # 3. Mostrar o estado final
    print("\n--- Estoque Atualizado ---")
    print(carregar_estoque())