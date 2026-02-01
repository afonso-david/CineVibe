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
        
        # 3. Simular a remoção da categoria (exatamente como no app.py)
        print("\n2. Simulando remoção da categoria...")
        
        # Verificar se a categoria existe antes de fazer qualquer operação
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
        
        # Atualizar avatares para categoria_id = NULL antes de remover a categoria
        if total_avatares > 0:
            cursor.execute("UPDATE avatars SET categoria_id = NULL WHERE categoria_id = %s", (categoria_id,))
            print(f"Atualizados {cursor.rowcount} avatares para categoria NULL")
        
        # Agora remover a categoria
        cursor.execute("DELETE FROM avatar_categories WHERE id = %s", (categoria_id,))
        
        if cursor.rowcount == 0:
            print("❌ Erro: Categoria não foi removida da base de dados.")
        else:
            # Commit de todas as operações
            conn.commit()
            if total_avatares > 0:
                print(f"✅ Categoria '{categoria_nome}' removida com sucesso! {total_avatares} avatares ficaram sem categoria.")
            else:
                print(f"✅ Categoria '{categoria_nome}' removida com sucesso!")
        
        # 4. Verificar se foi removida
        print("\n3. Verificando remoção...")
        cursor.execute("SELECT * FROM avatar_categories WHERE id = %s", (categoria_id,))
        categoria_removida = cursor.fetchone()
        
        if categoria_removida is None:
            print("✅ Categoria foi removida com sucesso da base de dados!")
        else:
            print(f"❌ Categoria ainda existe: {categoria_removida}")
        
        print("\n✅ TESTE CONCLUÍDO!")
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    testar_remocao_categoria()