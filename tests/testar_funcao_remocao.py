#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import mysql.connector
import sys
import os

# Adicionar o diretório atual ao path para importar o app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        database='cinevibe',
        user='root',
        password='Kevin@15'
    )

def testar_funcao_remocao_direta():
    """
    Testa a lógica de remoção diretamente, simulando o que acontece na função do app.py
    """
    print("=== TESTE DA FUNÇÃO DE REMOÇÃO ===")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. Criar uma categoria de teste
        print("\n1. Criando categoria de teste...")
        cursor.execute("INSERT INTO avatar_categories (nome) VALUES ('TESTE_FUNCAO')")
        categoria_id = cursor.lastrowid
        conn.commit()
        print(f"Categoria criada com ID: {categoria_id}")
        
        # 2. Criar alguns avatares nesta categoria
        print("\n2. Criando avatares de teste...")
        for i in range(3):
            cursor.execute("""
                INSERT INTO avatars (nome, caminho, categoria_id) 
                VALUES (%s, %s, %s)
            """, (f'avatar_teste_{i}', f'/static/avatars/teste_{i}.png', categoria_id))
        
        conn.commit()
        print("3 avatares criados na categoria")
        
        # 3. Executar a lógica de remoção (igual ao app.py)
        print(f"\n3. Executando lógica de remoção para categoria {categoria_id}...")
        
        # Verificar se a categoria existe
        cursor.execute("SELECT nome FROM avatar_categories WHERE id = %s", (categoria_id,))
        categoria = cursor.fetchone()
        
        if not categoria:
            print("❌ Categoria não encontrada!")
            return
        
        categoria_nome = categoria[0]
        print(f"Categoria encontrada: {categoria_nome}")
        
        # Verificar quantos avatares usam esta categoria
        cursor.execute("SELECT COUNT(*) as total FROM avatars WHERE categoria_id = %s", (categoria_id,))
        result = cursor.fetchone()
        total_avatares = result[0] if result else 0
        print(f"Total de avatares na categoria: {total_avatares}")
        
        # Atualizar avatares para categoria_id = NULL
        if total_avatares > 0:
            cursor.execute("UPDATE avatars SET categoria_id = NULL WHERE categoria_id = %s", (categoria_id,))
            print(f"Atualizados {cursor.rowcount} avatares para categoria NULL")
        
        # Remover a categoria
        cursor.execute("DELETE FROM avatar_categories WHERE id = %s", (categoria_id,))
        print(f"Linhas afetadas na remoção: {cursor.rowcount}")
        
        if cursor.rowcount == 0:
            print("❌ Erro: Categoria não foi removida")
        else:
            conn.commit()
            print(f"✅ Categoria '{categoria_nome}' removida com sucesso!")
        
        # 4. Verificar se foi removida
        print("\n4. Verificando remoção...")
        cursor.execute("SELECT * FROM avatar_categories WHERE id = %s", (categoria_id,))
        categoria_removida = cursor.fetchone()
        
        if categoria_removida is None:
            print("✅ Categoria foi removida da base de dados!")
        else:
            print(f"❌ Categoria ainda existe: {categoria_removida}")
        
        # 5. Verificar se os avatares ficaram sem categoria
        cursor.execute("SELECT id, nome, categoria_id FROM avatars WHERE nome LIKE 'avatar_teste_%'")
        avatares_teste = cursor.fetchall()
        
        print(f"\n5. Avatares de teste após remoção:")
        for avatar in avatares_teste:
            print(f"- ID: {avatar[0]}, Nome: {avatar[1]}, Categoria: {avatar[2]}")
        
        # 6. Limpar dados de teste
        print("\n6. Limpando dados de teste...")
        cursor.execute("DELETE FROM avatars WHERE nome LIKE 'avatar_teste_%'")
        print(f"Removidos {cursor.rowcount} avatares de teste")
        conn.commit()
        
        print("\n✅ TESTE CONCLUÍDO COM SUCESSO!")
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    testar_funcao_remocao_direta()