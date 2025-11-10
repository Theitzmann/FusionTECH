import pdfplumber
import re
import sys
sys.path.insert(0, r'G:\Meu Drive\IBMEC\2025.02\Programação Estruturada\FusionTech\codigo')

from dashboard_fusion_tech_integrado import extrair_valor_melhorado, extrair_fornecedor_melhorado, extrair_data_emissao_melhorado

print("="*80)
print("TESTE COMPLETO - AMBOS OS BOLETOS")
print("="*80)

# Teste 1: Braspress
print("\n1. BRASPRESS")
print("-" * 40)
with pdfplumber.open('dados/boletos_processados/fatura_47191977 (1).pdf') as pdf:
    texto_braspress = ''
    for p in pdf.pages:
        texto_braspress += p.extract_text() + '\n'

valor_braspress = extrair_valor_melhorado(texto_braspress)
fornecedor_braspress = extrair_fornecedor_melhorado(texto_braspress)
emissao_braspress = extrair_data_emissao_melhorado(texto_braspress)

print(f"Fornecedor: {fornecedor_braspress}")
print(f"Valor: R$ {valor_braspress}")
print(f"Data emissao: {emissao_braspress}")
print(f"Status: {'OK' if valor_braspress == 1829.65 else 'ERRO - esperado 1829.65'}")

# Teste 2: Safra
print("\n2. BANCO SAFRA")
print("-" * 40)
with pdfplumber.open('boleto (1) (1).pdf') as pdf:
    texto_safra = ''
    for p in pdf.pages:
        texto_safra += p.extract_text() + '\n'

valor_safra = extrair_valor_melhorado(texto_safra)
fornecedor_safra = extrair_fornecedor_melhorado(texto_safra)
emissao_safra = extrair_data_emissao_melhorado(texto_safra)

print(f"Fornecedor: {fornecedor_safra}")
print(f"Valor: R$ {valor_safra}")
print(f"Data emissao: {emissao_safra}")
print(f"Status: {'OK' if valor_safra == 1217.77 else 'ERRO - esperado 1217.77'}")

print("\n" + "="*80)
print("RESUMO")
print("="*80)
print(f"Braspress: {'PASS' if valor_braspress == 1829.65 else 'FAIL'}")
print(f"Safra: {'PASS' if valor_safra == 1217.77 else 'FAIL'}")
