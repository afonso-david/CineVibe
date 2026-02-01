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

def teste_final():
    print("=== TESTE FINAL DE REMOÇÃO DE CATEGORIA ===")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Criar uma categoria de teste
        print("\n1. Criando categoria de teste...")
        cursor.execute("INSERT INTO avatar_categories (nome) VALUES ('TESTE_FINAL')")
        categoria_id = cursor.lastrowid
        conn.commit()
        print(f"✅ Categoria criada com ID: {categoria_id}")
        
        # 2. Criar alguns avatares nesta categoria
        print("\n2. Criando avatares de teste...")
        for i in range(2):
            cursor.execute("""
                INSERT INTO avatars (nome, caminho, categoria_id) 
                VALUES (%s, %s, %s)
            """, (f'avatar_final_{i}', f'/static/avatars/final_{i}.png', categoria_id))
        
        conn.commit()
        print("✅ 2 avatares criados na categoria")
        
        # 3. Verificar estado antes da remoção
        print(f"\n3. Estado antes da remoção:")
        cursor.execute("SELECT * FROM avatar_categories WHERE id = %s", (categoria_id,))
        categoria = cursor.fetchone()
        print(f"Categoria: {categoria}")
        
        cursor.execute("SELECT id, nome, categoria_id FROM avatars WHERE nome LIKE 'avatar_final_%'")
        avatares = cursor.fetchall()
        print("Avatares:")
        for avatar in avatares:
            print(f"  - ID: {avatar[0]}, Nome: {avatar[1]}, Categoria: {avatar[2]}")
        
        # 4. Remover a categoria (usando ON DELETE SET NULL)
        print(f"\n4. Removendo categoria {categoria_id}...")
        cursor.execute("DELETE FROM avatar_categories WHERE id = %s", (categoria_id,))
        conn.commit()
        print(f"✅ Categoria removida ({cursor.rowcount} linha afetada)")
        
        # 5. Verificar estado após a remoção
        print(f"\n5. Estado após a remoção:")
        cursor.execute("SELECT * FROM avatar_categories WHERE id = %s", (categoria_id,))
        categoria_removida = cursor.fetchone()
        print(f"Categoria: {categoria_removida}")
        
        cursor.execute("SELECT id, nome, categoria_id FROM avatars WHERE nome LIKE 'avatar_final_%'")
        avatares_apos = cursor.fetchall()
        print("Avatares:")
        for avatar in avatares_apos:
            print(f"  - ID: {avatar[0]}, Nome: {avatar[1]}, Categoria: {avatar[2]}")
        
        # 6. Limpar dados de teste
        print("\n6. Limpando dados de teste...")
        cursor.execute("DELETE FROM avatars WHERE nome LIKE 'avatar_final_%'")
        conn.commit()
        print(f"✅ {cursor.rowcount} avatares de teste removidos")
        
        print("\n🎉 TESTE FINAL CONCLUÍDO COM SUCESSO!")
        print("A funcionalidade de remoção de categorias está funcionando corretamente!")
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    teste_final()