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

def verificar_categorias():
    print("=== VERIFICAÇÃO DE CATEGORIAS ===")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Listar todas as categorias
        cursor.execute("SELECT * FROM avatar_categories ORDER BY id")
        categorias = cursor.fetchall()
        
        print(f"\nTotal de categorias: {len(categorias)}")
        print("\nCategorias existentes:")
        for categoria in categorias:
            print(f"ID: {categoria[0]}, Nome: {categoria[1]}")
        
        # Verificar avatares por categoria
        print("\nAvatares por categoria:")
        cursor.execute("""
            SELECT 
                COALESCE(ac.nome, 'Sem categoria') as categoria,
                COUNT(a.id) as total_avatares
            FROM avatars a
            LEFT JOIN avatar_categories ac ON a.categoria_id = ac.id
            GROUP BY ac.id, ac.nome
            ORDER BY ac.id
        """)
        
        stats = cursor.fetchall()
        for stat in stats:
            print(f"- {stat[0]}: {stat[1]} avatares")
            
    except Exception as e:
        print(f"Erro: {str(e)}")
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    verificar_categorias()