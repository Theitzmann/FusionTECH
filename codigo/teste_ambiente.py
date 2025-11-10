"""
Teste de Ambiente - Projeto Fusion Tech
Verifica se todas as bibliotecas estão instaladas e funcionando
"""

import sys

print("=" * 70)
print("TESTANDO AMBIENTE PYTHON - PROJETO FUSION TECH")
print("=" * 70)
print()

# Teste 1: Versão do Python
print("[1] Verificando versão do Python...")
print(f"    Python {sys.version}")
print(f"    ✓ Python funcionando!\n")

# Teste 2: Importar bibliotecas
print("[2] Testando importação de bibliotecas...")

bibliotecas = {
    'pandas': None,
    'numpy': None,
    'matplotlib': None,
    'seaborn': None,
    'openpyxl': None
}

erros = []

for biblioteca in bibliotecas.keys():
    try:
        if biblioteca == 'pandas':
            import pandas as pd
            bibliotecas['pandas'] = pd.__version__
            print(f"    ✓ pandas {pd.__version__}")
        elif biblioteca == 'numpy':
            import numpy as np
            bibliotecas['numpy'] = np.__version__
            print(f"    ✓ numpy {np.__version__}")
        elif biblioteca == 'matplotlib':
            import matplotlib.pyplot as plt
            bibliotecas['matplotlib'] = plt.matplotlib.__version__
            print(f"    ✓ matplotlib {plt.matplotlib.__version__}")
        elif biblioteca == 'seaborn':
            import seaborn as sns
            bibliotecas['seaborn'] = sns.__version__
            print(f"    ✓ seaborn {sns.__version__}")
        elif biblioteca == 'openpyxl':
            import openpyxl
            bibliotecas['openpyxl'] = openpyxl.__version__
            print(f"    ✓ openpyxl {openpyxl.__version__}")
    except ImportError as e:
        erros.append(biblioteca)
        print(f"    ✗ {biblioteca} NÃO INSTALADO")

print()

# Teste 3: Verificar arquivo Excel
print("[3] Testando leitura do arquivo Excel...")
try:
    import pandas as pd
    import os
    
    # Tentar diferentes caminhos possíveis
    caminhos_possiveis = [
        '../dados/contasapagar_1.xlsx',
        'dados/contasapagar_1.xlsx',
        './dados/contasapagar_1.xlsx'
    ]
    
    arquivo_encontrado = False
    caminho_correto = None
    
    for caminho in caminhos_possiveis:
        if os.path.exists(caminho):
            arquivo_encontrado = True
            caminho_correto = caminho
            break
    
    if arquivo_encontrado:
        df = pd.read_excel(caminho_correto)
        print(f"    ✓ Arquivo Excel encontrado!")
        print(f"    ✓ Caminho: {caminho_correto}")
        print(f"    ✓ Dados carregados: {len(df)} registros, {len(df.columns)} colunas")
    else:
        print(f"    ✗ Arquivo Excel NÃO encontrado")
        print(f"    ℹ️  Caminhos testados:")
        for caminho in caminhos_possiveis:
            print(f"       - {caminho}")
        print(f"    ℹ️  Diretório atual: {os.getcwd()}")
        
except Exception as e:
    print(f"    ✗ Erro ao carregar Excel: {e}")

print()

# Resumo final
print("=" * 70)
print("RESUMO DO TESTE")
print("=" * 70)

if len(erros) == 0:
    print("✓ Todas as bibliotecas estão instaladas e funcionando!")
else:
    print(f"✗ {len(erros)} biblioteca(s) com problema:")
    for erro in erros:
        print(f"  - {erro}")
    print("\nPara instalar, execute:")
    print(f"pip install {' '.join(erros)}")

print()
print("=" * 70)
print("AMBIENTE PRONTO PARA USO!" if len(erros) == 0 else "CORRIJA OS ERROS ACIMA")
print("=" * 70)