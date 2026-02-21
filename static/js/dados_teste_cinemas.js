const DADOS_TESTE_CINEMAS = {
  "success": true,
  "cinemas": [
    {
      "id": 1,
      "nome": "CineVibe Lisboa",
      "localizacao": "Lisboa",
      "tipos_sessao": [
        {
          "id": 1,
          "nome": "2D",
          "preco": 8.5,
          "sessoes": [
            {
              "id": 1,
              "horario": "14:30",
              "sala": "Sala 1"
            },
            {
              "id": 2,
              "horario": "17:00",
              "sala": "Sala 1"
            },
            {
              "id": 3,
              "horario": "19:30",
              "sala": "Sala 2"
            }
          ]
        },
        {
          "id": 2,
          "nome": "IMAX",
          "preco": 15.0,
          "sessoes": [
            {
              "id": 4,
              "horario": "15:00",
              "sala": "Sala IMAX"
            },
            {
              "id": 5,
              "horario": "18:00",
              "sala": "Sala IMAX"
            },
            {
              "id": 6,
              "horario": "21:00",
              "sala": "Sala IMAX"
            }
          ]
        }
      ],
      "total_sessoes": 6
    },
    {
      "id": 2,
      "nome": "CineVibe Porto",
      "localizacao": "Porto",
      "tipos_sessao": [
        {
          "id": 1,
          "nome": "2D",
          "preco": 8.5,
          "sessoes": [
            {
              "id": 7,
              "horario": "16:00",
              "sala": "Sala 3"
            },
            {
              "id": 8,
              "horario": "20:00",
              "sala": "Sala 3"
            }
          ]
        },
        {
          "id": 3,
          "nome": "4DX",
          "preco": 15.0,
          "sessoes": [
            {
              "id": 9,
              "horario": "18:30",
              "sala": "Sala 4DX"
            }
          ]
        }
      ],
      "total_sessoes": 3
    }
  ]
};
function carregarDadosTeste() {
    console.log('🧪 Carregando dados de teste...');
    cinemasData = DADOS_TESTE_CINEMAS.cinemas;
    renderizarCinemas();
    console.log('✅ Dados de teste carregados:', cinemasData.length, 'cinemas');
}
const carregarCinemasSessoesOriginal = carregarCinemasSessoes;
carregarCinemasSessoes = function() {
    console.log('🔄 Tentando carregar dados reais...');
    fetch(`/admin/filmes/${filmeId}/cinemas-sessoes`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('✅ Dados reais carregados');
                cinemasData = data.cinemas;
                renderizarCinemas();
            } else {
                console.log('⚠️ Erro nos dados reais, usando dados de teste');
                carregarDadosTeste();
            }
        })
        .catch(error => {
            console.log('⚠️ Erro de conexão, usando dados de teste');
            carregarDadosTeste();
        });
};
