import re, os

files = [
    'templates/home.html',
    'templates/pesquisa.html',
    'templates/sessao_vintage.html',
    'templates/sessao_terror.html',
    'templates/sessao_romance.html',
    'templates/lgp.html',
    'templates/legendagem.html',
    'templates/audiodescricao.html',
    'templates/cine_acessivel.html',
    'templates/cookies.html',
    'templates/termos_condicoes.html',
    'templates/politica_privacidade.html',
    'templates/bar.html',
    'templates/cinemas.html',
]

# Remove entire <script> blocks that contain location.href redirect to /pesquisa
# These are inline scripts that override search.js
script_pattern = re.compile(
    r'<script>\s*(?:(?!</script>).)*?location\.href\s*=\s*[`\'"`]/pesquisa\?q=(?:(?!</script>).)*?</script>',
    re.DOTALL
)

for f in files:
    if not os.path.exists(f):
        print(f'SKIP (not found): {f}')
        continue
    content = open(f, encoding='utf-8').read()
    if 'pesquisa?q=' not in content:
        print(f'SKIP (no match): {f}')
        continue

    new_content = script_pattern.sub('', content)
    if new_content != content:
        open(f, 'w', encoding='utf-8').write(new_content)
        removed = len(re.findall(script_pattern, content))
        print(f'FIXED: {f} (removed {removed} script block(s))')
    else:
        print(f'NO CHANGE (pattern not matched): {f}')
