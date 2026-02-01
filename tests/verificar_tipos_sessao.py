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

def verificar_tipos_sessao():
    print("=== VERIFICAÇÃO DOS TIPOS DE SESSÃO ===")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Verificar se a tabela existe
        cursor.execute("SHOW TABLES LIKE 'tipos_sessao'")
        tabela_existe = cursor.fetchone()
        
        if not tabela_existe:
            print("❌ Tabela 'tipos_sessao' não existe")
            
            # Verificar outras possíveis tabelas
            cursor.execute("SHOW TABLES LIKE '%sessao%'")
            tabelas_sessao = cursor.fetchall()
            print("Tabelas relacionadas com sessão:")
            for tabela in tabelas_sessao:
                print(f"- {tabela[0]}")
            return
        
        print("✅ Tabela 'tipos_sessao' encontrada")
        
        # Verificar estrutura
        cursor.execute("DESCRIBE tipos_sessao")
        colunas = cursor.fetchall()
        
        print("\nEstrutura da tabela:")
        for coluna in colunas:
            print(f"- {coluna[0]}: {coluna[1]} | Null: {coluna[2]} | Key: {coluna[3]} | Default: {coluna[4]}")
        
        # Verificar dados existentes
        cursor.execute("SELECT * FROM tipos_sessao")
        tipos = cursor.fetchall()
        
        print(f"\nTotal de tipos de sessão: {len(tipos)}")
        print("\nTipos existentes:")
        for tipo in tipos:
            print(f"- ID: {tipo[0]}, Nome: {tipo[1]}")
            
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    verificar_tipos_sessao()