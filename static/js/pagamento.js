function escolher(tipo) {
  console.log('=== FUNÇÃO ESCOLHER CHAMADA ===');
  console.log('Tipo:', tipo);
  
  var metodos = document.getElementById('metodos');
  var formularios = document.getElementById('formularios');
  
  console.log('Elemento metodos:', metodos);
  console.log('Elemento formularios:', formularios);
  
  if (metodos) {
    metodos.style.display = 'none';
    console.log('Métodos escondidos');
  } else {
    console.error('ERRO: Elemento metodos não encontrado!');
  }
  
  if (formularios) {
    formularios.style.display = 'block';
    console.log('Formulários mostrados');
  } else {
    console.error('ERRO: Elemento formularios não encontrado!');
  }
  
  var forms = document.querySelectorAll('[id^="f-"]');
  console.log('Formulários encontrados:', forms.length);
  
  for(var i = 0; i < forms.length; i++) {
    forms[i].style.display = 'none';
    console.log('Formulário escondido:', forms[i].id);
  }
  
  var formEspecifico = document.getElementById('f-' + tipo);
  console.log('Formulário específico:', formEspecifico);
  
  if (formEspecifico) {
    formEspecifico.style.display = 'block';
    console.log('Formulário mostrado:', 'f-' + tipo);
  } else {
    console.error('ERRO: Formulário específico não encontrado:', 'f-' + tipo);
  }
  
  console.log('=== FIM DA FUNÇÃO ESCOLHER ===');
}

function voltar() {
  console.log('=== FUNÇÃO VOLTAR CHAMADA ===');
  
  var formularios = document.getElementById('formularios');
  var metodos = document.getElementById('metodos');
  
  if (formularios) {
    formularios.style.display = 'none';
    console.log('Formulários escondidos');
  }
  
  if (metodos) {
    metodos.style.display = 'block';
    console.log('Métodos mostrados');
  }
  
  console.log('=== FIM DA FUNÇÃO VOLTAR ===');
}

// Verificar se o JavaScript carregou
console.log('JavaScript de pagamento carregado!');

// Verificar elementos quando DOM carregar
document.addEventListener('DOMContentLoaded', function() {
  console.log('DOM carregado!');
  console.log('Elemento metodos:', document.getElementById('metodos'));
  console.log('Elemento formularios:', document.getElementById('formularios'));
  console.log('Cards encontrados:', document.querySelectorAll('.payment-method-image-card').length);
});