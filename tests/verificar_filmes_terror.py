import mysql.connector
from mysql.connector import Error

def verificar_filmes_terror():
    try:
        # Configuração da base de dados
        connection = mysql.connector.connect(
            host='localhost',
            database='cinevibe',
            user='root',
            password='Kevin@15'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            print("=== VERIFICAÇÃO DE FILMES DE TERROR ===\n")
            
            # 1. Verificar todas as tabelas
            print("1. TABELAS DISPONÍVEIS:")
            cursor.execute("SHOW TABLES")
            tabelas = cursor.fetchall()
            for tabela in tabelas:
                print(f"   {list(tabela.values())[0]}")
            
            print("\n" + "="*50 + "\n")
            
            # 2. Verificar se existe tabela filme_generos
            print("2. VERIFICAR TABELA FILME_GENEROS:")
            try:
                cursor.execute("DESCRIBE filme_generos")
                colunas = cursor.fetchall()
                print("   Estrutura da tabela filme_generos:")
                for coluna in colunas:
                    print(f"      {coluna['Field']} - {coluna['Type']}")
                
                # Verificar filmes de terror via tabela de relacionamento
                print("\n   FILMES DE TERROR (via filme_generos):")
                cursor.execute("""
                    SELECT f.id, f.titulo, g.nome as genero
                    FROM filmes f
                    JOIN filme_generos fg ON f.id = fg.filme_id
                    JOIN generos g ON fg.genero_id = g.id
                    WHERE g.nome IN ('Terror', 'Horror', 'Suspense')
                    ORDER BY f.titulo
                """)
                filmes_terror = cursor.fetchall()
                
                if filmes_terror:
                    for filme in filmes_terror:
                        print(f"      ID: {filme['id']} - {filme['titulo']} ({filme['genero']})")
                else:
                    print("      Nenhum filme de terror encontrado")
                    
            except Exception as e:
                print(f"   Tabela filme_generos não existe: {e}")
            
            print("\n" + "="*50 + "\n")
            
            # 3. Verificar total de filmes
            print("3. TOTAL DE FILMES:")
            cursor.execute("SELECT COUNT(*) as total FROM filmes")
            total = cursor.fetchone()
            print(f"   Total de filmes: {total['total']}")
            
            # 4. Mostrar alguns filmes
            print("\n4. ALGUNS FILMES EXISTENTES:")
            cursor.execute("SELECT id, titulo FROM filmes LIMIT 10")
            alguns_filmes = cursor.fetchall()
            for filme in alguns_filmes:
                print(f"   ID: {filme['id']} - {filme['titulo']}")
            
            # 5. Sugerir criação de filmes de terror se não existirem
            print("\n" + "="*50)
            print("SUGESTÃO: Como adicionar filmes de terror")
            print("="*50)
            print("\n5. PARA ADICIONAR FILMES DE TERROR:")
            print("   1. Adicionar filme na tabela 'filmes'")
            print("   2. Relacionar com género Terror (ID: 5) na tabela 'filme_generos'")
            print("   3. Exemplo de SQL:")
            print("      INSERT INTO filmes (titulo, sinopse, diretor, duracao, poster_url) VALUES")
            print("      ('O Exorcista', 'Filme de terror clássico...', 'William Friedkin', 122, 'imgs/exorcista.jpg');")
            print("      INSERT INTO filme_generos (filme_id, genero_id) VALUES (LAST_INSERT_ID(), 5);")
            
    except Error as e:
        print(f"Erro ao conectar à base de dados: {e}")
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print(f"\nConexão à base de dados encerrada.")

if __name__ == "__main__":
    verificar_filmes_terror()