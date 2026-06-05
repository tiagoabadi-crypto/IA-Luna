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
            nome TEXT,
            categoria TEXT,
            preco REAL,
            quantidade INTEGER,
            validade TEXT,
            preco_referencia REAL
        )
    ''')
    # Tabela de Logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            acao TEXT,
            data TEXT
        )
    ''')
    conn.commit()
    conn.close()

def salvar_produto_inteligente(nome, cat, preco, qtd, val, ref):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, quantidade FROM produtos WHERE nome = ?", (nome,))
    resultado = cursor.fetchone()
    
    if resultado:
        novo_total = resultado[1] + qtd
        cursor.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (novo_total, resultado[0]))
        acao = f"Atualizado: {nome} (+{qtd})"
    else:
        cursor.execute("INSERT INTO produtos (nome, categoria, preco, quantidade, validade, preco_referencia) VALUES (?, ?, ?, ?, ?, ?)", 
                       (nome, cat, preco, qtd, val, ref))
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
        cursor.execute("INSERT INTO logs (acao, data) VALUES (?, ?)", (f"Venda: ID {prod_id} (-{qtd_venda})", datetime.now().strftime("%d/%m/%Y %H:%M")))
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