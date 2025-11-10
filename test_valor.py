import pdfplumber
import re

with pdfplumber.open('dados/boletos_processados/fatura_47191977 (1).pdf') as pdf:
    texto = ''
    for p in pdf.pages:
        texto += p.extract_text() + '\n'

# Testar o padrão específico
padrao = r'VALOR\s+L.QUIDO\s+R\$\s*\n?\s*([\d.,]+)'
matches = re.findall(padrao, texto, re.IGNORECASE | re.MULTILINE)
print(f'Padrao: {padrao}')
print(f'Matches encontrados: {matches}')

if matches:
    valores = []
    for match in matches:
        valor_str = match.strip().replace('.', '').replace(',', '.')
        try:
            valor = float(valor_str)
            if 10 <= valor <= 1000000:
                valores.append(valor)
        except:
            continue

    print(f'Valores validos: {valores}')
    if valores:
        valor_final = max(set(valores), key=valores.count)
        print(f'Valor final: {valor_final}')
