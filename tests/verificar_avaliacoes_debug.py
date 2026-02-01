import mysql.connector
from mysql.connector import Error

def verificar_tabela_avaliacoes():
    try:
        # Configuração da base de dados
        connection = mysql.connector.connect(
            host='localhost',
            database='cinevibe',
            user='root',
            password=''
        )
        
        if connection.is_connected():
            cursor = connection.cursor()
            
            # Verificar se a tabela existe
            cursor.execute("SHOW TABLES LIKE 'avaliacoes_filmes'")
            result = cursor.fetchone()
            
            if result:
                print("✅ Tabela 'avaliacoes_filmes' existe")
                
                # Verificar estrutura da tabela
                cursor.execute("DESCRIBE avaliacoes_filmes")
                columns = cursor.fetchall()
                print("\n📋 Estrutura da tabela:")
                for column in columns:
                    print(f"  - {column[0]} ({column[1]})")
                
                # Verificar dados existentes
                cursor.execute("SELECT COUNT(*) FROM avaliacoes_filmes")
                count = cursor.fetchone()[0]
                print(f"\n📊 Total de avaliações: {count}")
                
                # Mostrar algumas avaliações
                cursor.execute("SELECT * FROM avaliacoes_filmes LIMIT 5")
                avaliacoes = cursor.fetchall()
                print("\n🎬 Últimas avaliações:")
                for av in avaliacoes:
                    print(f"  - User {av[1]}, Filme {av[2]}, Rating {av[3]}, Comentário: '{av[4]}'")
                    
            else:
                print("❌ Tabela 'avaliacoes_filmes' NÃO existe!")
                print("Criando tabela...")
                
                cursor.execute("""
                    CREATE TABLE avaliacoes_filmes (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        usuario_id INT NOT NULL,
                        filme_id INT NOT NULL,
                        rating DECIMAL(2,1) NOT NULL,
                        comentario TEXT,
                        data_avaliacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                        FOREIGN KEY (filme_id) REFERENCES filmes(id),
                        UNIQUE KEY unique_user_filme (usuario_id, filme_id)
                    )
                """)
                connection.commit()
                print("✅ Tabela criada com sucesso!")
                
    except Error as e:
        print(f"❌ Erro: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    verificar_tabela_avaliacoes()