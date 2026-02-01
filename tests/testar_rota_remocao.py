#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        database='cinevibe',
        user='root',
        password='Kevin@15'
    )

def testar_rota_remocao():
    print("=== TESTE DA ROTA DE REMOÇÃO ===")
    
    # 1. Criar uma categoria de teste
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("\n1. Criando categoria de teste...")
        cursor.execute("INSERT INTO avatar_categories (nome) VALUES ('TESTE_ROTA')")
        categoria_id = cursor.lastrowid
        conn.commit()
        print(f"Categoria criada com ID: {categoria_id}")
        
        # 2. Fazer uma requisição POST para a rota de remoção
        print(f"\n2. Fazendo requisição para remover categoria {categoria_id}...")
        
        url = f"http://localhost:5000/admin/avatares/categorias/remover/{categoria_id}"
        
        # Criar uma sessão para manter cookies
        session = requests.Session()
        
        # Primeiro, fazer login (se necessário)
        # Para este teste, vamos assumir que não precisamos de autenticação
        
        try:
            response = session.post(url, allow_redirects=False)
            print(f"Status Code: {response.status_code}")
            print(f"Headers: {dict(response.headers)}")
            
            if response.status_code == 302:
                print(f"Redirecionamento para: {response.headers.get('Location', 'N/A')}")
            
        except requests.exceptions.ConnectionError:
            print("❌ Erro de conexão. Certifique-se de que a aplicação está a correr em localhost:5000")
            return
        
        # 3. Verificar se a categoria foi removida
        print("\n3. Verificando se a categoria foi removida...")
        cursor.execute("SELECT * FROM avatar_categories WHERE id = %s", (categoria_id,))
        categoria_removida = cursor.fetchone()
        
        if categoria_removida is None:
            print("✅ Categoria foi removida com sucesso!")
        else:
            print(f"❌ Categoria ainda existe: {categoria_removida}")
            # Limpar a categoria de teste
            cursor.execute("DELETE FROM avatar_categories WHERE id = %s", (categoria_id,))
            conn.commit()
            print("Categoria de teste removida manualmente")
        
    except Exception as e:
        print(f"❌ ERRO: {str(e)}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    testar_rota_remocao()