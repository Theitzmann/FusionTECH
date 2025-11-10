"""
Automação de Boletos - Fusion Tech
Extrai dados de boletos em PDF e atualiza planilha automaticamente

Autor: Projeto Fusion Tech - IBMEC 2025.02
"""

import pdfplumber
import pandas as pd
import os
import re
from datetime import datetime


def _resolver_subpasta(base, nome_canonico):
    """
    Resolve a subpasta independentemente do diretório de execução
    e tenta respeitar nomes já existentes com variação de caixa.
    """
    candidatos = [nome_canonico, nome_canonico.lower(), nome_canonico.upper()]
    vistos = set()
    for candidato in candidatos:
        if candidato in vistos:
            continue
        vistos.add(candidato)
        caminho = os.path.join(base, candidato)
        if os.path.exists(caminho):
            return caminho
    return os.path.join(base, nome_canonico)


# Configurações absolutas baseadas na localização deste arquivo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJETO_RAIZ = os.path.dirname(BASE_DIR)
DIRETORIO_DADOS = os.path.join(PROJETO_RAIZ, 'dados')

PASTA_BOLETOS = _resolver_subpasta(DIRETORIO_DADOS, 'Boletos')
PASTA_PROCESSADOS = _resolver_subpasta(DIRETORIO_DADOS, 'boletos_processados')
ARQUIVO_EXCEL = os.path.join(DIRETORIO_DADOS, 'contasapagar_automacao.xlsx')
ARQUIVO_LOG = os.path.join(DIRETORIO_DADOS, 'log_processamento.txt')

COLUMNS_PADRAO = [
    'Número',
    'Fornecedor',
    'Plano de contas',
    'Histórico',
    'Dt. Emissão',
    'Dt. Vencimento',
    'Dt. Pagamento',
    'Vr. Título',
    'Vr. Dev/Pag',
    'Valor Total a Pagar',
    'Forma de Pgto.'
]

def criar_pastas():
    """Cria as pastas necessárias se não existirem"""
    pastas = [PASTA_BOLETOS, PASTA_PROCESSADOS, os.path.dirname(ARQUIVO_LOG)]
    
    for pasta in pastas:
        if pasta and not os.path.exists(pasta):
            os.makedirs(pasta, exist_ok=True)
            print(f"Pasta criada: {pasta}")
    
    garantir_planilha_base()


def garantir_planilha_base():
    """Garante que a planilha de automação exista com as colunas padrão."""
    if os.path.exists(ARQUIVO_EXCEL):
        return

    df_vazio = pd.DataFrame(columns=COLUMNS_PADRAO)
    df_vazio.to_excel(ARQUIVO_EXCEL, index=False)
    print(f"Planilha criada: {ARQUIVO_EXCEL}")

def extrair_valor(texto):
    """Extrai o valor do boleto do texto"""
    # Padrões comuns para valores em boletos - do mais específico ao mais genérico
    padroes = [
        # ALTA PRIORIDADE: Valor líquido final (evita valores de tabelas)
        r'VALOR\s+L.QUIDO\s+R\$\s*\n?\s*([\d.,]+)',  # Braspress - valor final (aceita quebra de linha)
        # Safra - formato com R$ antes: "(=) Valor do Documento\n01 R$ 1.217,77"
        r'\(=\)\s*Valor\s+do\s+Documento\s*\n.*?R\$\s*([\d.,]+)',  # Safra com R$
        r'\(=\)\s*Valor\s+do\s+Documento\s*\n\s*([\d.,]+)',  # Safra - linha abaixo
        r'Valor\s+do\s+Documento\s*\n.*?R\$\s*([\d.,]+)',  # Safra alternativo com R$
        r'Valor\s+do\s+Documento\s*\n\s*([\d.,]+)',  # Safra alternativo
        # MÉDIA PRIORIDADE: Padrões específicos
        r'\(=\)\s*Valor\s+do\s+Doc\.\s+([\d.,]+)',  # Boletos padrão
        r'Valor\s+do\s+Documento[:\s]*([\d.,]+)',  # Mesmo nível
        r'Valor\s+Cobrado.*?\n.*?([\d.,]+)',
        # BAIXA PRIORIDADE: Braspress tabular
        r'^([\d]+,\d{2})\s+DM',  # Braspress tabela (pode ser subtotal)
        r'^\s*([\d.]+,\d{2})\s*$',  # Valor sozinho na linha
    ]
    
    valores_encontrados = []
    
    for padrao in padroes:
        matches = re.findall(padrao, texto, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            valor_str = match.replace('.', '').replace(',', '.')
            try:
                valor = float(valor_str)
                # Validar se é um valor razoável (entre R$10 e R$1.000.000)
                if 10 <= valor <= 1000000:
                    valores_encontrados.append(valor)
            except:
                continue
    
    # Retornar o valor mais comum ou o último
    if valores_encontrados:
        return max(set(valores_encontrados), key=valores_encontrados.count)
    return None

def extrair_data_emissao(texto):
    """Extrai a data de emissão do boleto"""
    # Padrões comuns para data de emissão
    padroes = [
        # Safra - formato: "Data Documento Vencimento ... 11/06/2025 11/08/2025" (primeira data)
        r'Data\s+Documento\s+Vencimento.*?\n.*?\n(\d{2}/\d{2}/\d{4})',
        # Safra - formato: "Data do Documento ... 11/06/2025"
        r'Data\s+do\s+Documento[^\n]*\n\s*(\d{2}/\d{2}/\d{4})',
        # Braspress - formato: "Emissão: 14 de Outubro de 2025"
        r'Emiss[ãa]o:\s+(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})',
        # Formato genérico: Data de Emissão / Data Documento
        r'Data\s+(?:de\s+)?Emiss[ãa]o[:\s]*(\d{2})[\/\-](\d{2})[\/\-](\d{4})',
        r'Data\s+Documento[:\s]*(\d{2})[\/\-](\d{2})[\/\-](\d{4})',
    ]

    meses = {
        'janeiro': '01', 'fevereiro': '02', 'março': '03', 'marco': '03',
        'abril': '04', 'maio': '05', 'junho': '06',
        'julho': '07', 'agosto': '08', 'setembro': '09',
        'outubro': '10', 'novembro': '11', 'dezembro': '12'
    }

    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            try:
                grupos = match.groups()
                if len(grupos) == 1:
                    # Data completa DD/MM/YYYY
                    return grupos[0]
                elif len(grupos) == 3:
                    # Pode ser formato por extenso ou DD MM YYYY
                    if grupos[1].lower() in meses:
                        # Formato por extenso: "14 de Outubro de 2025"
                        dia = grupos[0].zfill(2)
                        mes = meses[grupos[1].lower()]
                        ano = grupos[2]
                        return f"{dia}/{mes}/{ano}"
                    else:
                        # Formato separado DD MM YYYY
                        dia, mes, ano = grupos
                        return f"{dia}/{mes}/{ano}"
            except:
                continue
    return None

def extrair_vencimento(texto):
    """Extrai a data de vencimento do texto"""
    # Padrões comuns para datas - do mais específico ao mais genérico
    padroes = [
        # Safra - formato: "Data Documento Vencimento ... 11/06/2025 11/08/2025" (pega a segunda data)
        r'Data\s+Documento\s+Vencimento.*?\n.*?\n\d{2}/\d{2}/\d{4}\s+(\d{2}/\d{2}/\d{4})',
        r'Vencimento\s*\n\s*(\d{2}/\d{2}/\d{4})',  # Safra - linha abaixo direto
        r'(\d{2}/\d{2}/\d{4})\s+(?:REAL|Ag\./Cód)',  # Braspress - antes de REAL ou Ag./Cód
        r'Vencimento[:\s]*(\d{2})[\/\-](\d{2})[\/\-](\d{4})',  # Mesmo nível
        r'Data[:\s]*(?:de\s*)?Vencimento[:\s]*(\d{2})[\/\-](\d{2})[\/\-](\d{4})',  # Genérico
    ]
    
    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            try:
                grupos = match.groups()
                if len(grupos) == 1:
                    # Formato DD/MM/YYYY completo
                    return grupos[0]
                else:
                    # Formato separado
                    dia, mes, ano = grupos
                    return f"{dia}/{mes}/{ano}"
            except:
                continue
    return None

def extrair_fornecedor(texto):
    """Extrai o nome do fornecedor/beneficiário do texto"""
    padroes = [
        # ALTA PRIORIDADE: Formatos Safra (mais específicos primeiro)
        # Safra - formato: "Beneficiário CNPJ / CPF Ag./Cód.Beneficiário\nSUMAY DO BRASIL LTDA"
        r'Benefici[áa]rio\s+CNPJ\s*/\s*CPF[^\n]+\n\s*([A-ZÀ-Ú][A-ZÀ-Ú\s&.-]+)',  # Safra quebra de linha
        # Safra - formato: "Beneficiário Ag./Cód... Motivos...\nSUMAY DO BRASIL LTDA"
        r'Benefici[áa]rio\s+Ag\./C[óo]d\.[^\n]+\n\s*([A-ZÀ-Ú][A-ZÀ-Ú\s&.-]+)',  # Safra com Ag.
        # Braspress - só pega se tiver "Final" E não tiver "Compensa"
        r'Benefici[áa]rio\s+Final[^\n]*\n\s*([A-ZÀ-Ú][A-ZÀ-Ú\s&.-]+?)(?:\s+\d|\s+CNPJ)',  # Braspress
        r'Benefici[áa]rio\s*\n\s*([A-ZÀ-Ú][A-ZÀ-Ú\s&.-]+)',  # Safra - linha nova
        # MÉDIA PRIORIDADE: Mesmo nível
        r'Benefici[áa]rio[:\s]*([A-ZÀ-Ú0-9.,\s&/-]+)',
        r'Cedente[:\s]*([A-ZÀ-Ú][A-ZÀ-Ú\s&.-]+)',
        r'Sacador[:\s]*([A-ZÀ-Ú][A-ZÀ-Ú\s&.-]+)',
    ]

    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE | re.MULTILINE)
        if match:
            fornecedor = match.group(1).strip()
            # Remover possíveis quebras de linha e caracteres extras
            fornecedor = ' '.join(fornecedor.split())
            fornecedor = fornecedor.split('\n')[0]  # Pegar só primeira linha
            # Filtrar nomes inválidos
            if 'Ficha' in fornecedor or 'Compensa' in fornecedor:
                continue  # Pular e tentar próximo padrão
            # Limitar tamanho
            if len(fornecedor) > 60:
                fornecedor = fornecedor[:60]
            # Validar que não é só espaços ou muito curto
            if len(fornecedor) > 5:
                return fornecedor
    return "Fornecedor não identificado"

def extrair_numero_documento(texto):
    """Extrai o número do documento/fatura"""
    padroes = [
        r'N[úu]mero\s+do\s+Doc[.:]\s*([\w\/.-]+)',
        r'Nº\s+do\s+Doc[.:]\s*([\w\/.-]+)',
        r'N[úu]mero\s+do\s+Documento[:\s]*([\w\/.-]+)',
        r'N[úu]mero\s+da\s+Fatura[:\s]*([\w\/.-]+)',
        r'Nº\s+Fatura[:\s]*([\w\/.-]+)',
    ]
    
    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE)
        if match:
            return match.group(1)
    return None

def processar_pdf(caminho_pdf):
    """
    Processa um arquivo PDF de boleto e extrai as informações
    
    Returns:
        dict: Dicionário com os dados extraídos ou None se falhar
    """
    print(f"\n{'='*60}")
    print(f"Processando: {os.path.basename(caminho_pdf)}")
    print(f"{'='*60}")
    
    try:
        # Abrir PDF e extrair texto
        with pdfplumber.open(caminho_pdf) as pdf:
            texto_completo = ""
            for pagina in pdf.pages:
                texto = pagina.extract_text()
                if texto:
                    texto_completo += texto + "\n"
        
        if not texto_completo:
            print("⚠️  PDF vazio ou não foi possível extrair texto")
            return None
        
        # Extrair informações
        valor = extrair_valor(texto_completo)
        vencimento = extrair_vencimento(texto_completo)
        data_emissao = extrair_data_emissao(texto_completo)
        fornecedor = extrair_fornecedor(texto_completo)
        numero_doc = extrair_numero_documento(texto_completo)

        # Verificar se conseguiu extrair dados mínimos
        if not valor or not vencimento:
            print("⚠️  Não foi possível extrair informações suficientes do PDF")
            print(f"   Valor extraído: {valor}")
            print(f"   Vencimento extraído: {vencimento}")
            return None

        dados = {
            'Fornecedor': fornecedor,
            'Valor': valor,
            'Vencimento': vencimento,
            'Data_Emissao': data_emissao,  # Adicionar data de emissão extraída
            'Numero_Documento': numero_doc,
            'Arquivo_PDF': os.path.basename(caminho_pdf),
            'Data_Processamento': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
        # Mostrar dados extraídos
        print("\n✓ Dados extraídos com sucesso:")
        print(f"  Fornecedor: {dados['Fornecedor']}")
        print(f"  Valor: R$ {dados['Valor']:.2f}")
        print(f"  Data Emissão: {dados['Data_Emissao'] if dados['Data_Emissao'] else 'Não identificada'}")
        print(f"  Vencimento: {dados['Vencimento']}")
        if dados['Numero_Documento']:
            print(f"  Nº Documento: {dados['Numero_Documento']}")
        
        return dados
        
    except Exception as e:
        print(f"❌ Erro ao processar PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

def adicionar_na_planilha(dados):
    """
    Adiciona os dados extraídos na planilha Excel
    """
    try:
        garantir_planilha_base()

        # Carregar planilha existente
        df = pd.read_excel(ARQUIVO_EXCEL)
        if df.empty:
            df = pd.DataFrame(columns=COLUMNS_PADRAO)
        
        # Gerar próximo número
        numeros_existentes = df['Número'].dropna()
        if len(numeros_existentes) > 0:
            # Extrair números e encontrar o maior
            try:
                numeros = []
                for n in numeros_existentes:
                    num_str = str(n).replace('000', '').strip()
                    if num_str.isdigit():
                        numeros.append(int(num_str))
                
                if numeros:
                    ultimo_num = max(numeros)
                    proximo_numero = f"{ultimo_num + 1:06d}"
                else:
                    proximo_numero = "000052"
            except:
                proximo_numero = "000052"
        else:
            proximo_numero = "000001"
        
        # Criar histórico
        historico = f"Boleto processado automaticamente"
        if dados.get('Numero_Documento'):
            historico += f" - Doc: {dados['Numero_Documento']}"
        historico += f" - {dados['Arquivo_PDF']}"
        
        # Usar data de emissão extraída ou data atual como fallback
        if dados.get('Data_Emissao'):
            dt_emissao = pd.to_datetime(dados['Data_Emissao'], format='%d/%m/%Y')
        else:
            dt_emissao = datetime.now().strftime('%Y-%m-%d')

        # Criar nova linha
        nova_linha = {
            'Número': proximo_numero,
            'Fornecedor': dados['Fornecedor'],
            'Plano de contas': 'CONTAS A PAGAR',
            'Histórico': historico,
            'Dt. Emissão': dt_emissao,  # Usar data extraída do boleto
            'Dt. Vencimento': pd.to_datetime(dados['Vencimento'], format='%d/%m/%Y'),
            'Dt. Pagamento': None,  # Vazio até ser pago
            'Vr. Título': dados['Valor'],
            'Vr. Dev/Pag': dados['Valor'],
            'Valor Total a Pagar': dados['Valor'],  # Valor total (mesmo que Vr. Título por padrão)
            'Forma de Pgto.': '3 - BOLETO'
        }
        
        # Adicionar nova linha
        df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
        df = df.reindex(columns=COLUMNS_PADRAO)
        
        # Salvar planilha
        df.to_excel(ARQUIVO_EXCEL, index=False)
        
        print(f"\n✓ Registro adicionado à planilha com número: {proximo_numero}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar planilha: {e}")
        import traceback
        traceback.print_exc()
        return False

def mover_para_processados(caminho_pdf):
    """Move o PDF para a pasta de processados"""
    try:
        nome_arquivo = os.path.basename(caminho_pdf)
        destino = os.path.join(PASTA_PROCESSADOS, nome_arquivo)
        
        # Se já existe, adicionar timestamp
        if os.path.exists(destino):
            nome, ext = os.path.splitext(nome_arquivo)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            destino = os.path.join(PASTA_PROCESSADOS, f"{nome}_{timestamp}{ext}")
        
        # Mover arquivo
        import shutil
        shutil.move(caminho_pdf, destino)
        print(f"✓ Arquivo movido para: {destino}")
        
    except Exception as e:
        print(f"⚠️  Não foi possível mover o arquivo: {e}")

def salvar_log(mensagem):
    """Salva log do processamento"""
    try:
        with open(ARQUIVO_LOG, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            f.write(f"[{timestamp}] {mensagem}\n")
    except:
        pass

def main():
    """Função principal - processa todos os boletos na pasta"""
    print("\n" + "="*60)
    print("AUTOMAÇÃO DE BOLETOS - FUSION TECH")
    print("="*60)
    
    # Criar pastas necessárias
    criar_pastas()
    
    # Verificar se há PDFs para processar
    if not os.path.exists(PASTA_BOLETOS):
        print(f"\n❌ Pasta de boletos não encontrada: {PASTA_BOLETOS}")
        return
    
    arquivos_pdf = [f for f in os.listdir(PASTA_BOLETOS) if f.lower().endswith('.pdf')]
    
    if not arquivos_pdf:
        print(f"\n⚠️  Nenhum arquivo PDF encontrado em: {PASTA_BOLETOS}")
        print(f"   Coloque os PDFs de boletos nesta pasta e execute novamente.")
        return
    
    print(f"\n✓ Encontrados {len(arquivos_pdf)} arquivo(s) PDF para processar\n")
    
    # Processar cada PDF
    processados = 0
    erros = 0
    
    for arquivo in arquivos_pdf:
        caminho_completo = os.path.join(PASTA_BOLETOS, arquivo)
        
        # Extrair dados do PDF
        dados = processar_pdf(caminho_completo)
        
        if dados:
            # Adicionar na planilha
            if adicionar_na_planilha(dados):
                # Mover para pasta de processados
                mover_para_processados(caminho_completo)
                processados += 1
                salvar_log(f"✓ Processado: {arquivo} - R$ {dados['Valor']:.2f}")
            else:
                erros += 1
                salvar_log(f"✗ Erro ao adicionar na planilha: {arquivo}")
        else:
            erros += 1
            salvar_log(f"✗ Erro ao extrair dados: {arquivo}")
    
    # Resumo
    print("\n" + "="*60)
    print("RESUMO DO PROCESSAMENTO")
    print("="*60)
    print(f"✓ Processados com sucesso: {processados}")
    print(f"✗ Erros: {erros}")
    print(f"Total: {len(arquivos_pdf)}")
    if os.path.exists(ARQUIVO_LOG):
        print(f"\n✓ Log salvo em: {ARQUIVO_LOG}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
