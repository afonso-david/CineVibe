#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
from mysql.connector import Error

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        database='cinevibe',
        user='root',
        password=''
    )

def testar_remocao_categoria():
    print("=== TESTE DE REMOÇÃO DE CATEGORIA ===")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Criar uma categoria de teste
        print("\n1. Criando categoria de teste...")
        cursor.execute("INSERT INTO avatar_categories (nome) VALUES ('TESTE_REMOCAO')")
        categoria_id = cursor.lastrowid
        conn.commit()
        print(f"Categoria criada com ID: {categoria_id}")
        
        # 2. Verificar se foi criada
        cursor.execute("SELECT * FROM avatar_categories WHERE id = %s", (categoria_id,))
        categoria = cursor.fetchone()
        print(f"Categoria encontrada: {categoria}")
        
        # 3. Criar um avatar de teste nesta categoria
        print("\n2. Criando avatar de teste...")
        cursor.execute("""
            INSERT INTO avatars (nome, caminho, categoria_id) 
            VALUES ('avatar_teste', '/static/avatars/teste.png', %s)
        """, (categoria_id,))
        avatar_id = cursor.lastrowid
        conn.commit()
        print(f"Avatar criado com ID: {avatar_id}")
        
        # 4. Verificar quantos avatares usam esta categoria
        cursor.execute("SELECT COUNT(*) as total FROM avatars WHERE categoria_id = %s", (categoria_id,))
        result = cursor.fetchone()
        total_avatares = result[0] if result else 0
        print(f"Total de avatares na categoria: {total_avatares}")
        
        # 5. Simular a remoção da categoria (como no código do app.py)
        print("\n3. Removendo categoria...")
        
        # Atualizar avatares para categoria_id = NULL
        if total_avatares > 0:
            cursor.execute("UPDATE avatars SET categoria_id = NULL WHERE categoria_id = %s", (categoria_id,))
            print(f"Atualizados {cursor.rowcount} avatares para categoria NULL")
        
        # Remover a categoria
        cursor.execute("DELETE FROM avatar_categories WHERE id = %s", (categoria_id,))
        print(f"Linhas afetadas na remoção: {cursor.rowcount}")
        
        conn.commit()
        
        # 6. Verificar se foi removida
        print("\n4. Verificando remoção...")
        cursor.execute("SELECT * FROM avatar_categories WHERE id = %s", (categoria_id,))
        categoria_removida = cursor.fetchone()
        print(f"Categoria após remoção: {categoria_removida}")
        
        # 7. Verificar se o avatar ficou sem categoria
        cursor.execute("SELECT * FROM avatars WHERE id = %s", (avatar_id,))
        avatar_atualizado = cursor.fetchone()
        print(f"Avatar após remoção da categoria: {avatar_atualizado}")
        
        # 8. Limpar dados de teste
        print("\n5. Limpando dados de teste...")
        cursor.execute("DELETE FROM avatars WHERE id = %s", (avatar_id,))
        conn.commit()
        print("Avatar de teste removido")
        
        print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    testar_remocao_categoria()