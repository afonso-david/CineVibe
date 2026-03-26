import os, glob

fixed = 0
for path in glob.glob('templates/*.html'):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
    except:
        try:
            with open(path, 'r', encoding='latin-1') as f:
                content = f.read()
        except:
            continue

    original = content

    # Corrigir aspas escapadas geradas pelo script anterior
    content = content.replace(
        "<link rel=\"stylesheet\" href=\"{{ url_for(\\'static\\', filename=\\'css/mobile-menu.css\\') }}\">",
        "<link rel=\"stylesheet\" href=\"{{ url_for('static', filename='css/mobile-menu.css') }}\">"
    )
    content = content.replace(
        "<script src=\"{{ url_for(\\'static\\', filename=\\'js/hamburger-menu.js\\') }}\"></script>",
        "<script src=\"{{ url_for('static', filename='js/hamburger-menu.js') }}\"></script>"
    )

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'FIXED: {os.path.basename(path)}')
        fixed += 1

print(f'\nTotal fixed: {fixed}')
