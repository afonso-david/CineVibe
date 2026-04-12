console.log('Avatar modal JS carregado');

function abrirModalAvatar() {
    console.log('Abrindo modal de avatar...');
    const modal = document.getElementById('avatarModal');
    if (modal) {
        const container = document.querySelector('.avatar-categories');
        if (container) {
            container.innerHTML = '<div class="loading">Carregando avatares...</div>';
        }
        modal.style.display = 'flex';
        carregarAvatares();
    } else {
        console.error('Modal não encontrado!');
    }
}

function fecharModalAvatar() {
    const modal = document.getElementById('avatarModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function carregarAvatares() {
    console.log('Carregando avatares da base de dados...');
    const container = document.querySelector('.avatar-categories');
    if (!container) {
        console.error('Container de categorias não encontrado!');
        return;
    }
    
    fetch('/api/avatars/all')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                container.innerHTML = '<div class="error">Erro ao carregar avatares</div>';
                return;
            }
            
            let html = '';
            
            data.forEach(categoria => {
                if (categoria.avatars && categoria.avatars.length > 0) {
                    html += `
                        <div class="avatar-category">
                            <div class="category-header">
                                <h3>${categoria.categoria.toUpperCase()}</h3>
                                <div class="category-subtitle">personagens icônicos</div>
                            </div>
                            <div class="avatars-grid">
                    `;
                    
                    categoria.avatars.forEach(avatar => {
                        html += `
                            <div class="avatar-option" onclick="selecionarAvatar(${avatar.id}, '${avatar.caminho}', '${avatar.nome}', this)">
                                <img src="static/${avatar.caminho}" alt="${avatar.nome}" loading="eager" />
                            </div>
                        `;
                    });
                    
                    html += `
                            </div>
                        </div>
                    `;
                }
            });
            
            container.innerHTML = html;
        })
        .catch(error => {
            console.error('Erro ao carregar avatares:', error);
            container.innerHTML = '<div class="error">Erro ao carregar avatares</div>';
        });
}

function selecionarAvatar(avatarId, caminhoAvatar, nomeAvatar, elemento) {
    console.log('Avatar selecionado:', avatarId, caminhoAvatar);
    
    // Marcar como selecionado visualmente
    document.querySelectorAll('.avatar-option').forEach(option => {
        option.classList.remove('selected');
    });
    elemento.classList.add('selected');
    
    // Atualizar imediatamente na interface
    const userAvatar = document.querySelector('.user-avatar');
    const userPic = document.querySelector('.user-pic');
    const avatarUrl = caminhoAvatar.startsWith('static/') ? caminhoAvatar : 'static/' + caminhoAvatar;
    
    if (userAvatar) {
        userAvatar.src = avatarUrl;
    }
    if (userPic) {
        userPic.src = avatarUrl;
    }
    
    // Fechar o modal imediatamente
    fecharModalAvatar();
    
    // Enviar para o servidor em background
    fetch('/api/atualizar-avatar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            avatar_id: avatarId
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Avatar atualizado com sucesso no servidor!');
            // Atualizar com o caminho correto do servidor se necessário
            if (data.avatar_path) {
                const correctUrl = data.avatar_path.startsWith('static/') ? data.avatar_path : 'static/' + data.avatar_path;
                if (userAvatar) userAvatar.src = correctUrl;
                if (userPic) userPic.src = correctUrl;
            }
        } else {
            console.error('Erro ao atualizar avatar:', data.message);
            // Reverter em caso de erro
            alert('Erro ao atualizar avatar: ' + data.message);
            location.reload();
        }
    })
    .catch(error => {
        console.error('Erro:', error);
        alert('Erro de conexão ao atualizar avatar');
        location.reload();
    });
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM carregado - Avatar modal');
    
    document.addEventListener('click', function(e) {
        // Fechar modal ao clicar no overlay
        const modal = document.getElementById('avatarModal');
        if (e.target === modal) {
            fecharModalAvatar();
        }
        
        // Botão cancelar
        if (e.target.classList.contains('btn-cancelar-avatar')) {
            fecharModalAvatar();
        }
    });
    
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            fecharModalAvatar();
        }
    });
});
