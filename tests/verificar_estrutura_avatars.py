#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        database='cinevibe',
        user='root',
        password='Kevin@15'
    )

def verificar_estrutura():
    print("=== VERIFICAÇÃO DA ESTRUTURA DA TABELA AVATARS ===")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar a estrutura da tabela avatars
        print("\n1. Estrutura da tabela avatars:")
        cursor.execute("DESCRIBE avatars")
        colunas = cursor.fetchall()
        
        for coluna in colunas:
            print(f"- {coluna[0]}: {coluna[1]} | Null: {coluna[2]} | Key: {coluna[3]} | Default: {coluna[4]}")
        
        # Verificar as restrições de chave estrangeira
        print("\n2. Restrições de chave estrangeira:")
        cursor.execute("""
            SELECT 
                CONSTRAINT_NAME,
                COLUMN_NAME,
                REFERENCED_TABLE_NAME,
                REFERENCED_COLUMN_NAME,
                DELETE_RULE,
                UPDATE_RULE
            FROM information_schema.KEY_COLUMN_USAGE 
            WHERE TABLE_SCHEMA = 'cinevibe' 
            AND TABLE_NAME = 'avatars' 
            AND REFERENCED_TABLE_NAME IS NOT NULL
        """)
        
        restricoes = cursor.fetchall()
        for restricao in restricoes:
            print(f"- Constraint: {restricao[0]}")
            print(f"  Coluna: {restricao[1]} -> {restricao[2]}.{restricao[3]}")
            print(f"  Delete Rule: {restricao[4]}, Update Rule: {restricao[5]}")
        
        # Verificar se categoria_id permite NULL
        print("\n3. Verificando se categoria_id permite NULL:")
        cursor.execute("SHOW COLUMNS FROM avatars LIKE 'categoria_id'")
        coluna_info = cursor.fetchone()
        if coluna_info:
            print(f"categoria_id: {coluna_info[1]} | Null: {coluna_info[2]}")
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    verificar_estrutura()