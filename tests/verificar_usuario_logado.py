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

def verificar_usuarios_admin():
    print("=== VERIFICAÇÃO DE USUÁRIOS ADMINISTRADORES ===")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # Buscar usuários administradores
        cursor.execute("""
            SELECT u.id, u.nome, u.email, u.is_admin,
                   u.avatar_personalizado,
                   a.caminho as avatar_galeria,
                   COALESCE(u.avatar_personalizado, a.caminho) as avatar_url
            FROM usuarios u
            LEFT JOIN avatars a ON u.avatar_id = a.id
            WHERE u.is_admin = 1
            ORDER BY u.id
        """)
        
        admins = cursor.fetchall()
        
        print(f"\n📊 Total de administradores: {len(admins)}")
        
        for admin in admins:
            print(f"\n👤 Admin ID {admin['id']}:")
            print(f"   Nome: {admin['nome']}")
            print(f"   Email: {admin['email']}")
            print(f"   Avatar Personalizado: {admin['avatar_personalizado'] or 'Não'}")
            print(f"   Avatar da Galeria: {admin['avatar_galeria'] or 'Não'}")
            print(f"   Avatar URL Final: {admin['avatar_url'] or 'Nenhum'}")
        
        if not admins:
            print("\n⚠️ Nenhum usuário administrador encontrado!")
            print("Criando usuário admin de teste...")
            
            # Criar usuário admin de teste
            cursor.execute("""
                INSERT INTO usuarios (nome, email, senha, is_admin) 
                VALUES ('Admin Teste', 'admin@cinevibe.com', 'senha123', 1)
            """)
            conn.commit()
            print("✅ Usuário admin criado: admin@cinevibe.com / senha123")
        
        print(f"\n🔍 Para testar a seção de perfil:")
        print("1. Acesse http://localhost:5000/login")
        print("2. Faça login com um usuário administrador")
        print("3. Vá para http://localhost:5000/admin/tipos-sessao")
        print("4. Verifique se a seção de perfil aparece no sidebar")
        
    except Exception as e:
        print(f"❌ Erro: {str(e)}")
        conn.rollback()
    
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    verificar_usuarios_admin()