import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = 'estoque.db'

def conectar(): return sqlite3.connect(DB_NAME)

def garantir_estrutura():
    conn = conectar()
    cursor = conn.cursor()
    # Tabela de produtos
    cursor.execute('''CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, categoria TEXT, 
        preco REAL, quantidade INTEGER, validade TEXT, preco_referencia REAL DEFAULT 0.0)''')
    
    # Tabela de logs
    cursor.execute('''CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT, acao TEXT, detalhe TEXT, data TEXT)''')
    conn.commit()
    conn.close()

def adicionar_log(acao, detalhe):
    conn = conectar()
    cursor = conn.cursor()
    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO logs (acao, detalhe, data) VALUES (?, ?, ?)", (acao, detalhe, data))
    conn.commit()
    conn.close()

def adicionar_produto(nome, cat, preco, qtd, val, ref):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO produtos (nome, categoria, preco, quantidade, validade, preco_referencia) VALUES (?, ?, ?, ?, ?, ?)", 
                   (nome, cat, preco, qtd, val, ref))
    conn.commit()
    adicionar_log("Cadastro", f"Produto {nome} adicionado.")
    conn.close()

def remover_produto(id_produto):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE id = ?", (id_produto,))
    conn.commit()
    adicionar_log("Remoção", f"Produto ID {id_produto} removido.")
    conn.close()

def registrar_venda(id_produto, qtd_vendida):
    conn = conectar()
    cursor = conn.cursor()
    # Verifica estoque atual
    cursor.execute("SELECT quantidade, nome FROM produtos WHERE id = ?", (id_produto,))
    row = cursor.fetchone()
    if row and row[0] >= qtd_vendida:
        cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?", (qtd_vendida, id_produto))
        conn.commit()
        adicionar_log("Venda", f"Venda de {qtd_vendida} unidades de {row[1]}")
        conn.close()
        return True
    conn.close()
    return False

def buscar_tudo():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM produtos", conn)
    conn.close()
    return df

def buscar_logs():
    conn = conectar()
    df = pd.read_sql_query("SELECT * FROM logs ORDER BY data DESC", conn)
    conn.close()
    return df