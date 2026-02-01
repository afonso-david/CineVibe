import mysql.connector
from mysql.connector import Error

def testar_query_terror():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            database='cinevibe',
            user='root',
            password='Kevin@15'
        )
        
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            
            print("=== TESTE DA QUERY DE FILMES DE TERROR ===\n")
            
            # Testar a query exata que está no app.py
            cursor.execute("""
                SELECT 
                    f.id, 
                    f.titulo, 
                    f.poster_url, 
                    f.poster_hover,
                    f.trailer_url,
                    f.duracao,
                    f.imdb_rating as rating,
                    g.nome as genero_nome,
                    COUNT(r.id) as num_reservas
                FROM filmes f
                JOIN filme_generos fg ON f.id = fg.filme_id
                JOIN generos g ON fg.genero_id = g.id
                LEFT JOIN reservas r ON f.id = r.filme_id
                WHERE g.nome IN ('Terror', 'Horror', 'Suspense')
                AND f.estado = 'em_exibicao'
                GROUP BY f.id, f.titulo, f.poster_url, f.poster_hover, f.trailer_url, f.duracao, f.imdb_rating, g.nome
                ORDER BY num_reservas DESC, f.imdb_rating DESC
                LIMIT 20
            """)
            
            filmes_terror = cursor.fetchall()
            
            print(f"FILMES DE TERROR EM EXIBIÇÃO: {len(filmes_terror)}")
            for filme in filmes_terror:
                print(f"   ID: {filme['id']} - {filme['titulo']}")
                print(f"      Género: {filme['genero_nome']}")
                print(f"      Poster: {filme['poster_url']}")
                print(f"      Rating: {filme['rating']}")
                print(f"      Reservas: {filme['num_reservas']}")
                print()
            
            # Se não houver filmes em exibição, testar sem filtro de estado
            if not filmes_terror:
                print("Nenhum filme em exibição. Testando todos os filmes de terror...")
                cursor.execute("""
                    SELECT 
                        f.id, 
                        f.titulo, 
                        f.poster_url, 
                        f.poster_hover,
                        f.trailer_url,
                        f.duracao,
                        f.imdb_rating as rating,
                        g.nome as genero_nome,
                        COUNT(r.id) as num_reservas
                    FROM filmes f
                    JOIN filme_generos fg ON f.id = fg.filme_id
                    JOIN generos g ON fg.genero_id = g.id
                    LEFT JOIN reservas r ON f.id = r.filme_id
                    WHERE g.nome IN ('Terror', 'Horror', 'Suspense')
                    GROUP BY f.id, f.titulo, f.poster_url, f.poster_hover, f.trailer_url, f.duracao, f.imdb_rating, g.nome
                    ORDER BY num_reservas DESC, f.imdb_rating DESC
                    LIMIT 20
                """)
                
                filmes_terror = cursor.fetchall()
                
                print(f"\nTODOS OS FILMES DE TERROR: {len(filmes_terror)}")
                for filme in filmes_terror:
                    print(f"   ID: {filme['id']} - {filme['titulo']}")
                    print(f"      Género: {filme['genero_nome']}")
                    print(f"      Poster: {filme['poster_url']}")
                    print(f"      Rating: {filme['rating']}")
                    print(f"      Reservas: {filme['num_reservas']}")
                    print()
            
    except Error as e:
        print(f"Erro: {e}")
    
    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    testar_query_terror()