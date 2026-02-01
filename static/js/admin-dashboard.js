// ========================================
// SIDEBAR
// ========================================

function toggleSidebar() {
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('sidebarOverlay');
  sidebar.classList.toggle('active');
  overlay.classList.toggle('active');
}

// Fechar sidebar ao clicar em um link (mobile)
document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', function() {
    if (window.innerWidth <= 1024) {
      toggleSidebar();
    }
  });
});

// Marcar item ativo baseado na URL
const currentPath = window.location.pathname;
document.querySelectorAll('.nav-item').forEach(item => {
  if (item.getAttribute('href') === currentPath) {
    item.classList.add('active');
  }
});

// ========================================
// GRÁFICOS
// ========================================

// Gráfico de Reservas Diárias
const reservasData = {
  labels: reservasDiariasLabels,
  datasets: [{
    label: 'Reservas',
    data: reservasDiariasData,
    backgroundColor: 'rgba(255, 214, 10, 0.2)',
    borderColor: '#FFD60A',
    borderWidth: 2,
    tension: 0.4,
    fill: true
  }]
};

const reservasConfig = {
  type: 'line',
  data: reservasData,
  options: {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: { display: false }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          color: '#aaa',
          stepSize: 1
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      x: {
        ticks: { color: '#aaa' },
        grid: { color: 'rgba(255, 255, 255, 0.1)' }
      }
    }
  }
};

const reservasChart = new Chart(
  document.getElementById('reservasChart'),
  reservasConfig
);

// Gráfico de Vendas por Cinema
const cinemasData = {
  labels: vendasCinemasLabels,
  datasets: [{
    label: 'Vendas (€)',
    data: vendasCinemasData,
    backgroundColor: [
      'rgba(255, 214, 10, 0.8)',
      'rgba(255, 152, 0, 0.8)',
      'rgba(76, 175, 80, 0.8)',
      'rgba(33, 150, 243, 0.8)',
      'rgba(156, 39, 176, 0.8)'
    ],
    borderColor: '#FFD60A',
    borderWidth: 2
  }]
};

const cinemasConfig = {
  type: 'bar',
  data: cinemasData,
  options: {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: { display: false }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          color: '#aaa',
          callback: function(value) {
            return value + '€';
          }
        },
        grid: {
          color: 'rgba(255, 255, 255, 0.1)'
        }
      },
      x: {
        ticks: { color: '#aaa' },
        grid: { display: false }
      }
    }
  }
};

const cinemasChart = new Chart(
  document.getElementById('cinemasChart'),
  cinemasConfig
);

// ========================================
// EXPORTAÇÃO DE RELATÓRIOS
// ========================================

function exportarRelatorio(tipo) {
  const hoje = new Date().toISOString().split('T')[0];
  const horaAtual = new Date().toLocaleTimeString('pt-PT');
  const filename = `CineVibe_Relatorio_${tipo}_${hoje}.csv`;
  let csvContent = '';

  switch(tipo) {
    case 'vendas':
      // Cabeçalho do relatório
      csvContent = '=== CINEVIBE - RELATÓRIO DE VENDAS POR CINEMA ===\n';
      csvContent += `Data de Geração:,${hoje}\n`;
      csvContent += `Hora:,${horaAtual}\n`;
      csvContent += `Período:,Últimos 7 dias\n`;
      csvContent += '\n';
      
      // Dados
      csvContent += 'Ranking,Cinema,Total Vendas (€),Percentagem do Total\n';
      const totalVendas = vendasCinemasData.reduce((a, b) => a + b, 0);
      vendasCinemasLabels.forEach((cinema, index) => {
        const vendas = vendasCinemasData[index];
        const percentagem = ((vendas / totalVendas) * 100).toFixed(2);
        csvContent += `${index + 1},${cinema},${vendas.toFixed(2)},${percentagem}%\n`;
      });
      
      // Resumo
      csvContent += '\n=== RESUMO ===\n';
      csvContent += `Total de Cinemas:,${vendasCinemasLabels.length}\n`;
      csvContent += `Receita Total:,${totalVendas.toFixed(2)} €\n`;
      csvContent += `Média por Cinema:,${(totalVendas / vendasCinemasLabels.length).toFixed(2)} €\n`;
      csvContent += `Cinema com Maior Receita:,${vendasCinemasLabels[0]}\n`;
      break;

    case 'reservas':
      csvContent = '=== CINEVIBE - RELATÓRIO DE RESERVAS ===\n';
      csvContent += `Data de Geração:,${hoje}\n`;
      csvContent += `Hora:,${horaAtual}\n`;
      csvContent += '\n';
      csvContent += 'Data,Total Reservas,Variação\n';
      
      reservasDiariasLabels.forEach((data, index) => {
        const reservas = reservasDiariasData[index];
        const variacao = index > 0 ? reservasDiariasData[index] - reservasDiariasData[index - 1] : 0;
        const sinal = variacao > 0 ? '+' : '';
        csvContent += `${data},${reservas},${sinal}${variacao}\n`;
      });
      
      const totalReservas = reservasDiariasData.reduce((a, b) => a + b, 0);
      csvContent += '\n=== RESUMO ===\n';
      csvContent += `Total de Reservas:,${totalReservas}\n`;
      csvContent += `Média Diária:,${(totalReservas / reservasDiariasData.length).toFixed(1)}\n`;
      break;

    case 'usuarios':
      csvContent = '=== CINEVIBE - RELATÓRIO DE USUÁRIOS ===\n';
      csvContent += `Data de Geração:,${hoje}\n`;
      csvContent += `Hora:,${horaAtual}\n`;
      csvContent += '\n';
      csvContent += 'Métrica,Valor,Observações\n';
      csvContent += `Total de Usuários,${totalUsuarios},Base total registada\n`;
      csvContent += `Novos Usuários (7 dias),${novosUsuarios},Crescimento recente\n`;
      csvContent += `Usuários Ativos (30 dias),${usuariosAtivos},Engagement mensal\n`;
      csvContent += `Taxa de Retorno,${taxaRetorno}%,Fidelização\n`;
      
      csvContent += '\n=== ANÁLISE ===\n';
      const taxaCrescimento = ((novosUsuarios / totalUsuarios) * 100).toFixed(2);
      csvContent += `Taxa de Crescimento Semanal:,${taxaCrescimento}%\n`;
      csvContent += `Taxa de Atividade:,${((usuariosAtivos / totalUsuarios) * 100).toFixed(2)}%\n`;
      break;

    case 'produtos':
      csvContent = '=== CINEVIBE - RELATÓRIO DE PRODUTOS DO BAR ===\n';
      csvContent += `Data de Geração:,${hoje}\n`;
      csvContent += `Hora:,${horaAtual}\n`;
      csvContent += '\n';
      csvContent += 'Ranking,Produto,Vendas,Percentagem\n';
      
      const totalProdutos = topSnacks.reduce((acc, snack) => acc + snack.vendas, 0);
      topSnacks.forEach((snack, index) => {
        const percentagem = ((snack.vendas / totalProdutos) * 100).toFixed(2);
        csvContent += `${index + 1},${snack.produto},${snack.vendas},${percentagem}%\n`;
      });
      
      csvContent += '\n=== RESUMO ===\n';
      csvContent += `Total de Vendas:,${totalProdutos}\n`;
      csvContent += `Produto Mais Vendido:,${topSnacks[0].produto}\n`;
      break;
  }

  // Criar e fazer download do arquivo
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const link = document.createElement('a');
  const url = URL.createObjectURL(blob);
  
  link.setAttribute('href', url);
  link.setAttribute('download', filename);
  link.style.visibility = 'hidden';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);

  // Feedback visual
  const btn = event.target;
  const originalText = btn.innerHTML;
  btn.innerHTML = '✓ Exportado!';
  btn.style.background = 'rgba(76, 175, 80, 0.3)';
  
  setTimeout(() => {
    btn.innerHTML = originalText;
    btn.style.background = '';
  }, 2000);
}

// Hover effects para botões de exportação
document.querySelectorAll('[onclick^="exportarRelatorio"]').forEach(btn => {
  btn.addEventListener('mouseenter', function() {
    this.style.transform = 'translateY(-2px)';
    this.style.boxShadow = '0 4px 15px rgba(0,0,0,0.3)';
  });
  
  btn.addEventListener('mouseleave', function() {
    this.style.transform = 'translateY(0)';
    this.style.boxShadow = 'none';
  });
});

// ========================================
// TIMESTAMP
// ========================================

function updateTimestamp() {
  const now = new Date();
  const formatted = now.toLocaleString('pt-PT', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
  document.getElementById('lastUpdate').textContent = formatted;
}

updateTimestamp();

// ========================================
// FILTROS DE PERÍODO
// ========================================

document.querySelectorAll('.period-btn').forEach(btn => {
  btn.addEventListener('click', function() {
    document.querySelectorAll('.period-btn').forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    
    const period = this.getAttribute('data-period');
    
    // Feedback visual
    const originalText = this.textContent;
    this.textContent = '⏳ Carregando...';
    
    setTimeout(() => {
      this.textContent = originalText;
      alert('Funcionalidade de filtro será implementada em breve!');
    }, 500);
  });
});
