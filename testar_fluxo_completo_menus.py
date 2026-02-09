import json

print("=" * 60)
print("TESTE: Simular fluxo completo com diferentes menus")
print("=" * 60)

# Simular dados que o JavaScript envia
testes = [
    {
        'nome': 'Menu Combo (ID 1)',
        'dados': '[{"id": "1", "quantidade": 1, "tipo": "menu"}]'
    },
    {
        'nome': 'Menu Kids (ID 3)',
        'dados': '[{"id": "3", "quantidade": 1, "tipo": "menu"}]'
    },
    {
        'nome': 'Menu Combo Duplo (ID 5)',
        'dados': '[{"id": "5", "quantidade": 1, "tipo": "menu"}]'
    },
    {
        'nome': 'Pipocas Salgadas (ID 1 bar)',
        'dados': '[{"id": "1", "quantidade": 1, "tipo": "bar"}]'
    },
    {
        'nome': 'Menu Combo + Pipocas',
        'dados': '[{"id": "1", "quantidade": 1, "tipo": "menu"}, {"id": "1", "quantidade": 1, "tipo": "bar"}]'
    }
]

for teste in testes:
    print(f"\n📦 {teste['nome']}")
    print(f"   JSON: {teste['dados']}")
    
    produtos = json.loads(teste['dados'])
    print(f"   Produtos parseados: {len(produtos)}")
    
    for p in produtos:
        print(f"      - ID: {p['id']}, Tipo: {p['tipo']}, Qtd: {p['quantidade']}")

print("\n✅ Teste concluído!")
print("\nCom esta estrutura, o backend consegue distinguir:")
print("  - Menu Combo (tipo='menu', id=1)")
print("  - Pipocas Salgadas (tipo='bar', id=1)")
