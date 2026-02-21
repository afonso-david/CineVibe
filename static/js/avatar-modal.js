console.log('Avatar modal JS carregado');
let avatarSelecionado = null;
function abrirModalAvatar() {
    console.log('Abrindo modal de avatar...');
    const modal = document.getElementById('avatarModal');
    if (modal) {
        const container = document.querySelector('.avatar-categories');
        if (container) {
            container.innerHTML = '';
        }
        modal.style.display = 'flex';
        carregarAvatares();
        resetarSelecao();
    } else {
        console.error('Modal não encontrado!');
    }
}
function fecharModalAvatar() {
    const modal = document.getElementById('avatarModal');
    if (modal) {
        modal.style.display = 'none';
        resetarSelecao();
    }
}
function resetarSelecao() {
    avatarSelecionado = null;
    const preview = document.querySelector('.selected-avatar-preview');
    const btnConfirmar = document.querySelector('.btn-confirmar-avatar');
    if (preview) preview.classList.remove('show');
    if (btnConfirmar) btnConfirmar.classList.remove('enabled');
    document.querySelectorAll('.avatar-option').forEach(option => {
        option.classList.remove('selected');
    });
}
function carregarAvatares() {
    console.log('Carregando avatares...');
    const container = document.querySelector('.avatar-categories');
    if (!container) {
        console.error('Container de categorias não encontrado!');
        return;
    }
    container.innerHTML = `
        <div class="upload-section">
            <h3><i class="fas fa-upload"></i> Carregar do Computador</h3>
            <p>Escolhe uma imagem do teu computador para usar como avatar</p>
            <div class="file-input-wrapper">
                <input type="file" id="avatarUpload" accept="image/*" onchange="handleFileUpload(event)">
                <button class="btn-upload">
                    <i class="fas fa-folder-open"></i>
                    Escolher Ficheiro
                </button>
            </div>
        </div>
        <div class="avatar-category">
            <div class="category-header">
                <h3>SUPER-HERÓIS</h3>
                <div class="category-subtitle">personagens icônicos</div>
            </div>
            <div class="avatars-grid">
                <div class="avatar-option" onclick="selecionarAvatar('imgs/profile/super-herois/Superman (Superman 2025).jpg', this)">
                    <img src="static/imgs/profile/super-herois/Superman (Superman 2025).jpg" alt="Superman" />
                </div>
                <div class="avatar-option" onclick="selecionarAvatar('imgs/profile/super-herois/SUPERMAN.jpg', this)">
                    <img src="static/imgs/profile/super-herois/SUPERMAN.jpg" alt="Superman 2" />
                </div>
                <div class="avatar-option" onclick="selecionarAvatar('imgs/profile/super-herois/Gal_Gadot-removebg-preview.png', this)">
                    <img src="static/imgs/profile/super-herois/Gal_Gadot-removebg-preview.png" alt="Wonder Woman" />
                </div>
                <div class="avatar-option" onclick="selecionarAvatar('imgs/profile/super-herois/657-6577079_spiderman-mask-png-transparent-spider-man-homecoming-suit-removebg-preview.png', this)">
                    <img src="static/imgs/profile/super-herois/657-6577079_spiderman-mask-png-transparent-spider-man-homecoming-suit-removebg-preview.png" alt="Spider-Man" />
                </div>
            </div>
        </div>
        <div class="avatar-category">
            <div class="category-header">
                <h3>TERROR</h3>
                <div class="category-subtitle">personagens assombrados</div>
            </div>
            <div class="avatars-grid">
                <div class="avatar-option" onclick="selecionarAvatar('imgs/profile/terror/chucky-tv-series-removebg-preview.png', this)">
                    <img src="static/imgs/profile/terror/chucky-tv-series-removebg-preview.png" alt="Chucky" />
                </div>
                <div class="avatar-option" onclick="selecionarAvatar('imgs/profile/terror/freddy-krueger-icon-5-removebg-preview.png', this)">
                    <img src="static/imgs/profile/terror/freddy-krueger-icon-5-removebg-preview.png" alt="Freddy Krueger" />
                </div>
                <div class="avatar-option" onclick="selecionarAvatar('imgs/profile/terror/The-Nun-1-removebg-preview.png', this)">
                    <img src="static/imgs/profile/terror/The-Nun-1-removebg-preview.png" alt="The Nun" />
                </div>
                <div class="avatar-option" onclick="selecionarAvatar('imgs/profile/terror/SMILEFF_11MAIN-1-removebg-preview.png', this)">
                    <img src="static/imgs/profile/terror/SMILEFF_11MAIN-1-removebg-preview.png" alt="Smile" />
                </div>
            </div>
        </div>
    `;
}
function selecionarAvatar(caminhoAvatar, elemento) {
    console.log('Avatar selecionado:', caminhoAvatar);
    document.querySelectorAll('.avatar-option').forEach(option => {
        option.classList.remove('selected');
    });
    elemento.classList.add('selected');
    avatarSelecionado = caminhoAvatar;
    mostrarPreview(caminhoAvatar, elemento.querySelector('img').alt);
    const btnConfirmar = document.querySelector('.btn-confirmar-avatar');
    if (btnConfirmar) {
        btnConfirmar.classList.add('enabled');
    }
}
function handleFileUpload(event) {
    const file = event.target.files[0];
    if (file) {
        if (!file.type.startsWith('image/')) {
            return;
        }
        if (file.size > 5 * 1024 * 1024) {
            return;
        }
        const formData = new FormData();
        formData.append('avatar', file);
        fetch('/api/upload-avatar', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                avatarSelecionado = data.avatar_path;
                mostrarPreview('static/' + data.avatar_path, 'Imagem Personalizada');
                const btnConfirmar = document.querySelector('.btn-confirmar-avatar');
                if (btnConfirmar) {
                    btnConfirmar.classList.add('enabled');
                }
            }
        })
        .catch(error => {
            console.error('Erro:', error);
        });
    }
}
function mostrarPreview(caminhoAvatar, nomeAvatar) {
    const preview = document.querySelector('.selected-avatar-preview');
    if (preview) {
        const img = preview.querySelector('img');
        const span = preview.querySelector('span');
        if (img) img.src = caminhoAvatar.startsWith('static/') ? caminhoAvatar : 'static/' + caminhoAvatar;
        if (span) span.textContent = nomeAvatar;
        preview.classList.add('show');
    }
}
function confirmarAvatar() {
    if (!avatarSelecionado) return;
    console.log('Confirmando avatar:', avatarSelecionado);
    const userAvatar = document.querySelector('.user-avatar');
    const userPic = document.querySelector('.user-pic');
    const avatarUrl = avatarSelecionado.startsWith('static/') ? avatarSelecionado : 'static/' + avatarSelecionado;
    if (userAvatar) {
        userAvatar.src = avatarUrl;
    }
    if (userPic) {
        userPic.src = avatarUrl;
    }
    fecharModalAvatar();
    fetch('/api/atualizar-avatar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            avatar: avatarSelecionado
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            console.log('Avatar atualizado com sucesso!');
        } else {
            console.error('Erro ao atualizar avatar:', data.message);
        }
    })
    .catch(error => {
        console.error('Erro:', error);
    });
}
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM carregado - Avatar modal');
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-confirmar-avatar') && e.target.classList.contains('enabled')) {
            confirmarAvatar();
        }
        if (e.target.classList.contains('btn-cancelar-avatar')) {
            fecharModalAvatar();
        }
        const modal = document.getElementById('avatarModal');
        if (e.target === modal) {
            fecharModalAvatar();
        }
    });
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            fecharModalAvatar();
        }
    });
});