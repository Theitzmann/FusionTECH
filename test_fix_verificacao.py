import pdfplumber
import re
import sys
sys.path.insert(0, r'G:\Meu Drive\IBMEC\2025.02\Programação Estruturada\FusionTech\codigo')

# Importar a função atualizada do dashboard
from dashboard_fusion_tech_integrado import extrair_valor_melhorado

# Testar com Braspress
print("="*80)
print("TESTANDO BRASPRESS COM A FUNÇÃO ATUALIZADA")
print("="*80)

with pdfplumber.open('dados/boletos_processados/fatura_47191977 (1).pdf') as pdf:
    texto = ''
    for p in pdf.pages:
        texto += p.extract_text() + '\n'

valor = extrair_valor_melhorado(texto)
print(f"\nValor extraído: {valor}")

if valor == 1829.65:
    print("✓ SUCESSO! O valor está correto (1829.65)")
else:
    print(f"✗ ERRO! Valor incorreto. Esperado: 1829.65, Obtido: {valor}")
