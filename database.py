import sqlite3
import pandas as pd
from datetime import datetime

def conectar():
    return sqlite3.connect('estoque.db')

def garantir_estrutura():
    conn = conectar()
    cursor = conn.cursor()
    # Tabela de Produtos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT, codigo_barras TEXT, marca TEXT, especificacao TEXT,
            peso REAL, categoria TEXT, validade TEXT, quantidade INTEGER,
            estoque_minimo INTEGER, fornecedor TEXT, preco_venda REAL,
            preco_custo REAL, ncm TEXT, localizacao TEXT,
            status TEXT, imagem_path TEXT
        )
    ''')
    # Tabela de Logs (Essencial para as suas funções de registro funcionarem)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            acao TEXT, data TEXT
        )
    ''')
    conn.commit()
    conn.close()

def salvar_produto_inteligente(nome, cod_barras, marca, espec, peso, cat, val, qtd, est_min, fornec, preco_venda, preco_custo, ncm, local, status, img_path):
    conn = conectar()
    cursor = conn.cursor()
    
    # Verifica se já existe produto com esse código de barras para atualizar
    cursor.execute("SELECT id FROM produtos WHERE codigo_barras = ?", (cod_barras,))
    resultado = cursor.fetchone()
    
    if resultado:
        cursor.execute("""UPDATE produtos SET nome=?, marca=?, especificacao=?, peso=?, categoria=?, 
                          validade=?, quantidade=?, estoque_minimo=?, fornecedor=?, preco_venda=?, 
                          preco_custo=?, ncm=?, localizacao=?, status=?, imagem_path=? WHERE id=?""", 
                       (nome, marca, espec, peso, cat, val, qtd, est_min, fornec, preco_venda, preco_custo, ncm, local, status, img_path, resultado[0]))
        acao = f"Atualizado: {nome}"
    else:
        cursor.execute("""INSERT INTO produtos (nome, codigo_barras, marca, especificacao, peso, categoria, 
                          validade, quantidade, estoque_minimo, fornecedor, preco_venda, preco_custo, 
                          ncm, localizacao, status, imagem_path) 
                          VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", 
                       (nome, cod_barras, marca, espec, peso, cat, val, qtd, est_min, fornec, preco_venda, preco_custo, ncm, local, status, img_path))
        acao = f"Cadastrado: {nome}"
    
    cursor.execute("INSERT INTO logs (acao, data) VALUES (?, ?)", (acao, datetime.now().strftime("%d/%m/%Y %H:%M")))
    conn.commit()
    conn.close()

def buscar_tudo():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()
    return df

def registrar_venda(prod_id, qtd_venda):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT quantidade FROM produtos WHERE id = ?", (prod_id,))
    resultado = cursor.fetchone()
    
    if resultado and resultado[0] >= qtd_venda:
        novo_qtd = resultado[0] - qtd_venda
        cursor.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (novo_qtd, prod_id))
        cursor.execute("INSERT INTO logs (acao, data) VALUES (?, ?)", 
                       (f"Venda: ID {prod_id} (-{qtd_venda})", datetime.now().strftime("%d/%m/%Y %H:%M")))
        conn.commit()
        conn.close()
        return True
    conn.close()
    return False

def buscar_logs():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM logs ORDER BY id DESC", conn)
    conn.close()
    return df

def buscar_produtos_proximos_vencimento():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM produtos WHERE validade != ''", conn)
    conn.close()
    return df

def excluir_produto(id_produto):
    conn = conectar() # Corrigido aqui
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
    conn.commit()
    conn.close()