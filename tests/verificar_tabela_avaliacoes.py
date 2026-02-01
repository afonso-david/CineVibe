import mysql.connector
from mysql.connector import Error

def verificar_tabela():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='cinevibe',
            user='root',
            password=''
        )
        
        cursor = connection.cursor()
        
        # Verificar estrutura da tabela
        cursor.execute("DESCRIBE avaliacoes_filmes")
        estrutura = cursor.fetchall()
        
        print("Estrutura da tabela avaliacoes_filmes:")
        for campo in estrutura:
            print(campo)
        
        print("\n" + "="*50)
        
        # Verificar índices/chaves
        cursor.execute("SHOW INDEX FROM avaliacoes_filmes")
        indices = cursor.fetchall()
        
        print("Índices da tabela:")
        for indice in indices:
            print(indice)
            
        print("\n" + "="*50)
        
        # Verificar se existe chave única para (usuario_id, filme_id)
        cursor.execute("""
            SELECT COUNT(*) as tem_chave_unica
            FROM information_schema.statistics 
            WHERE table_schema = 'cinevibe' 
            AND table_name = 'avaliacoes_filmes' 
            AND non_unique = 0
            AND column_name IN ('usuario_id', 'filme_id')
        """)
        
        resultado = cursor.fetchone()
        print(f"Tem chave única para usuario_id/filme_id: {resultado[0] > 0}")
        
    except Error as e:
        print(f"Erro: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    verificar_tabela()