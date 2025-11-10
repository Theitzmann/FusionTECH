import pdfplumber
import re

# Copiar a função do dashboard com debug
def extrair_valor_melhorado_debug(texto):
    """Extrai o valor do boleto - COM DEBUG"""
    padroes = [
        # ALTA PRIORIDADE: Valor líquido final (evita valores de tabelas)
        r'VALOR\s+L.QUIDO\s+R\$\s*\n?\s*([\d.,]+)',  # Braspress - valor final (aceita quebra de linha)
        # Safra - formato com R$ antes: "(=) Valor do Documento\n01 R$ 1.217,77"
        r'\(=\)\s*Valor\s+do\s+Documento\s*\n.*?R\$\s*([\d.,]+)',  # Safra com R$
        r'\(=\)\s*Valor\s+do\s+Documento\s*\n\s*([\d.,]+)',  # Safra - linha abaixo
        r'Valor\s+do\s+Documento\s*\n.*?R\$\s*([\d.,]+)',  # Safra alternativo com R$
        r'Valor\s+do\s+Documento\s*\n\s*([\d.,]+)',  # Safra alternativo
        # MÉDIA PRIORIDADE: Padrões específicos
        r'\(=\)\s*Valor\s+do\s+Doc[.:]\s+([\d.,]+)',  # Boletos padrão
        r'Valor\s+do\s+Documento[:\s]*([\d.,]+)',  # Mesmo nível
        r'Valor\s+do\s+Doc[.:]\s*([\d.,]+)',
        r'Documento\s*\n\s*([\d.,]+)',  # Valor sozinho após "Documento"
        # BAIXA PRIORIDADE: Braspress tabular
        r'^([\d]+,\d{2})\s+DM',  # Braspress tabela (pode ser subtotal)
        r'^\s*([\d.]+,\d{2})\s*$',  # Valor sozinho na linha
    ]

    valores_encontrados = []

    for i, padrao in enumerate(padroes):
        matches = re.findall(padrao, texto, re.IGNORECASE | re.MULTILINE)
        if matches:
            print(f"\nPadrão {i}: {padrao}")
            print(f"  Matches encontrados: {matches}")

        for match in matches:
            valor_str = match.strip().replace('.', '').replace(',', '.')
            try:
                valor = float(valor_str)
                # Validar valor razoável
                if 10 <= valor <= 1000000:
                    valores_encontrados.append(valor)
                    print(f"  -> Valor válido adicionado: {valor}")
                else:
                    print(f"  -> Valor fora do intervalo: {valor}")
            except Exception as e:
                print(f"  -> Erro ao converter '{match}': {e}")
                continue

    print(f"\n=== TODOS OS VALORES ENCONTRADOS: {valores_encontrados}")

    if valores_encontrados:
        # Contar frequência de cada valor
        from collections import Counter
        contagem = Counter(valores_encontrados)
        print(f"=== CONTAGEM DE VALORES: {dict(contagem)}")

        # Retornar o valor mais comum
        valor_final = max(set(valores_encontrados), key=valores_encontrados.count)
        print(f"=== VALOR FINAL (mais comum): {valor_final}")
        return valor_final
    return None

# Testar com Braspress
with pdfplumber.open('dados/boletos_processados/fatura_47191977 (1).pdf') as pdf:
    texto = ''
    for p in pdf.pages:
        texto += p.extract_text() + '\n'

print("="*80)
print("TESTANDO BRASPRESS COM DEBUG")
print("="*80)
valor = extrair_valor_melhorado_debug(texto)
print(f"\n>>> RESULTADO FINAL: {valor}")
