import re

files = ['static/css/terror.css', 'static/css/romance.css', 'static/css/vintage.css']

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = re.sub(r'box-shadow:[^;]+;', '', content)
    content = re.sub(r'text-shadow:[^;]+;', '', content)
    
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)

print("Removed all box-shadow and text-shadow from sessoes tematicas")
