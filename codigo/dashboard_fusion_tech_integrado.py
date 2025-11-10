"""
Dashboard Integrado - Automação de Boletos
Fusion Tech - Gestão operacional + análise financeira
VERSÃO CORRIGIDA - Suporta múltiplos formatos de boleto
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from pathlib import Path
import os
import sys
import re
import pdfplumber

# ---------------------------------------------------------------------------
# Configuração de caminhos absolutos
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

PROJETO_RAIZ = BASE_DIR.parent
DIRETORIO_DADOS = PROJETO_RAIZ / "dados"

# ---------------------------------------------------------------------------
# Funções de extração de boletos (embutidas e melhoradas)
# ---------------------------------------------------------------------------

def extrair_valor_melhorado(texto):
    """Extrai o valor do boleto - VERSÃO MELHORADA para múltiplos formatos"""
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

    # Tentar padrões em ordem de prioridade e retornar o primeiro válido
    for padrao in padroes:
        matches = re.findall(padrao, texto, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            valor_str = match.strip().replace('.', '').replace(',', '.')
            try:
                valor = float(valor_str)
                # Validar valor razoável
                if 10 <= valor <= 1000000:
                    return valor  # Retorna o primeiro valor válido encontrado
            except:
                continue

    return None

def extrair_data_emissao_melhorado(texto):
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
        match = re.search(padrao, texto, re.IGNORECASE | re.MULTILINE)
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

def extrair_vencimento_melhorado(texto):
    """Extrai data de vencimento - VERSÃO MELHORADA"""
    padroes = [
        # Safra - formato: "Data Documento Vencimento ... 11/06/2025 11/08/2025" (pega a segunda data)
        r'Data\s+Documento\s+Vencimento.*?\n.*?\n\d{2}/\d{2}/\d{4}\s+(\d{2}/\d{2}/\d{4})',
        r'Vencimento\s*\n\s*(\d{2}/\d{2}/\d{4})',  # Safra - linha abaixo direto
        r'(\d{2}/\d{2}/\d{4})\s+(?:REAL|Ag\./Cód)',  # Braspress - antes de REAL ou Ag./Cód
        r'Vencimento[:\s]*(\d{2})[\/\-](\d{2})[\/\-](\d{4})',  # Mesmo nível
        r'Data[:\s]*(?:de\s*)?Vencimento[:\s]*(\d{2})[\/\-](\d{2})[\/\-](\d{4})',  # Genérico
    ]
    
    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE | re.MULTILINE)
        if match:
            try:
                grupos = match.groups()
                if len(grupos) == 1:
                    # Data completa DD/MM/YYYY
                    return grupos[0]
                else:
                    # Separado
                    dia, mes, ano = grupos
                    return f"{dia}/{mes}/{ano}"
            except:
                continue
    return None

def extrair_fornecedor_melhorado(texto):
    """Extrai fornecedor/beneficiário - VERSÃO MELHORADA"""
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

def extrair_numero_documento_melhorado(texto):
    """Extrai número do documento - VERSÃO MELHORADA"""
    padroes = [
        r'N[úu]mero\s+do\s+Documento\s*\n\s*(\S+)',
        r'Número\s+do\s+Documento\s*\n\s*(\S+)',
        r'N[úu]mero\s+do\s+Doc[.:]\s*(\S+)',
        r'Nº\s+do\s+Doc[.:]\s*(\S+)',
        r'N[úu]mero\s+da\s+Fatura[:\s]*(\d+)',
        r'Nº\s+Fatura[:\s]*(\d+)',
    ]
    
    for padrao in padroes:
        match = re.search(padrao, texto, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    return None

def processar_pdf_integrado(caminho_pdf):
    """Processa PDF usando funções embutidas melhoradas"""
    try:
        with pdfplumber.open(caminho_pdf) as pdf:
            texto_completo = ""
            for pagina in pdf.pages:
                texto = pagina.extract_text()
                if texto:
                    texto_completo += texto + "\n"
        
        if not texto_completo:
            return None
        
        # Extrair dados
        valor = extrair_valor_melhorado(texto_completo)
        vencimento = extrair_vencimento_melhorado(texto_completo)
        data_emissao = extrair_data_emissao_melhorado(texto_completo)
        fornecedor = extrair_fornecedor_melhorado(texto_completo)
        numero_doc = extrair_numero_documento_melhorado(texto_completo)

        if not valor or not vencimento:
            return None

        return {
            'Fornecedor': fornecedor,
            'Valor': valor,
            'Vencimento': vencimento,
            'Data_Emissao': data_emissao,  # Adicionar data de emissão
            'Numero_Documento': numero_doc,
            'Arquivo_PDF': os.path.basename(caminho_pdf),
            'Data_Processamento': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        }
        
    except Exception as e:
        st.error(f"Erro ao processar PDF: {e}")
        return None

def adicionar_na_planilha_integrado(dados, caminho_excel):
    """Adiciona dados na planilha"""
    try:
        # Carregar ou criar planilha
        if os.path.exists(caminho_excel):
            df = pd.read_excel(caminho_excel)
        else:
            df = pd.DataFrame()
        
        # Gerar próximo número
        if 'Número' in df.columns and len(df) > 0:
            numeros_existentes = df['Número'].dropna()
            try:
                numeros = []
                for n in numeros_existentes:
                    num_str = str(n).replace('000', '').strip()
                    if num_str.isdigit():
                        numeros.append(int(num_str))
                
                if numeros:
                    proximo_numero = f"{max(numeros) + 1:06d}"
                else:
                    proximo_numero = "000001"
            except:
                proximo_numero = "000001"
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

        # Nova linha
        nova_linha = {
            'Número': proximo_numero,
            'Fornecedor': dados['Fornecedor'],
            'Plano de contas': 'CONTAS A PAGAR',
            'Histórico': historico,
            'Dt. Emissão': dt_emissao,  # Usar data extraída do boleto
            'Dt. Vencimento': pd.to_datetime(dados['Vencimento'], format='%d/%m/%Y'),
            'Dt. Pagamento': None,
            'Vr. Título': dados['Valor'],
            'Vr. Dev/Pag': dados['Valor'],
            'Valor Total a Pagar': dados['Valor'],
            'Forma de Pgto.': '3 - BOLETO'
        }
        
        df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
        df.to_excel(caminho_excel, index=False)
        
        return True
    except Exception as e:
        st.error(f"Erro ao adicionar na planilha: {e}")
        return False

# ---------------------------------------------------------------------------
# Tentar importar módulo de automação original (fallback)
# ---------------------------------------------------------------------------

AUTOMACAO_IMPORT_ERROR = None
try:
    from automacao_boletos import (
        PASTA_PROCESSADOS as AUTO_PASTA_PROCESSADOS,
        ARQUIVO_EXCEL as AUTO_ARQUIVO_EXCEL,
        ARQUIVO_LOG as AUTO_ARQUIVO_LOG,
        COLUMNS_PADRAO as AUTO_COLUMNS_PADRAO,
        processar_pdf,
        adicionar_na_planilha,
        mover_para_processados,
    )

    PASTA_PROCESSADOS = Path(AUTO_PASTA_PROCESSADOS)
    ARQUIVO_EXCEL = Path(AUTO_ARQUIVO_EXCEL)
    ARQUIVO_LOG = Path(AUTO_ARQUIVO_LOG)
    COLUNAS_PADRAO = list(AUTO_COLUMNS_PADRAO)
    
    # Usar funções do módulo se disponível
    processar_pdf_func = processar_pdf
    adicionar_planilha_func = adicionar_na_planilha
    
except Exception as exc:
    AUTOMACAO_IMPORT_ERROR = exc
    
    # Usar funções embutidas como fallback
    processar_pdf_func = processar_pdf_integrado
    adicionar_planilha_func = None  # Será usado o integrado
    mover_para_processados = None
    
    PASTA_PROCESSADOS = DIRETORIO_DADOS / "boletos_processados"
    ARQUIVO_EXCEL = DIRETORIO_DADOS / "contasapagar_automacao.xlsx"
    ARQUIVO_LOG = DIRETORIO_DADOS / "log_processamento.txt"
    COLUNAS_PADRAO = [
        "Número", "Fornecedor", "Plano de contas", "Histórico",
        "Dt. Emissão", "Dt. Vencimento", "Dt. Pagamento",
        "Vr. Título", "Vr. Dev/Pag", "Valor Total a Pagar", "Forma de Pgto.",
    ]

# Garantir diretórios
DIRETORIO_DADOS.mkdir(parents=True, exist_ok=True)
PASTA_PROCESSADOS.mkdir(parents=True, exist_ok=True)
ARQUIVO_LOG.parent.mkdir(parents=True, exist_ok=True)

AUTOMACAO_DISPONIVEL = True  # Sempre disponível agora (embutido ou importado)
COLUNAS_DATA = ["Dt. Emissão", "Dt. Vencimento", "Dt. Pagamento"]
COLUNAS_NUMERICAS = ["Vr. Título", "Vr. Dev/Pag"]

# ---------------------------------------------------------------------------
# Funções utilitárias (mantidas do seu código)
# ---------------------------------------------------------------------------

def rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    else:
        st.experimental_rerun()

def formatar_brl(valor: float) -> str:
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def ler_planilha_atual() -> pd.DataFrame:
    if not ARQUIVO_EXCEL.exists():
        salvar_planilha_atual(pd.DataFrame(columns=COLUNAS_PADRAO))
    df = pd.read_excel(ARQUIVO_EXCEL)
    df = df.replace(r"^\s*$", pd.NA, regex=True)
    if df.empty:
        df = pd.DataFrame(columns=COLUNAS_PADRAO)
    return df

def salvar_planilha_atual(dados: pd.DataFrame) -> None:
    df_salvar = dados.copy()
    df_salvar = df_salvar.replace(r"^\s*$", pd.NA, regex=True)
    
    for coluna in COLUNAS_PADRAO:
        if coluna not in df_salvar.columns:
            df_salvar[coluna] = pd.NA
    
    df_salvar = df_salvar[COLUNAS_PADRAO]
    
    for coluna in COLUNAS_DATA:
        if coluna in df_salvar.columns:
            df_salvar[coluna] = pd.to_datetime(df_salvar[coluna], errors="coerce")
    
    for coluna in COLUNAS_NUMERICAS:
        if coluna in df_salvar.columns:
            df_salvar[coluna] = pd.to_numeric(df_salvar[coluna], errors="coerce")
    
    df_salvar.to_excel(ARQUIVO_EXCEL, index=False)

def excluir_registros_planilha(numeros: list[str]) -> int:
    if not numeros:
        return 0
    df_atual = ler_planilha_atual()
    if df_atual.empty or "Número" not in df_atual.columns:
        return 0
    numeros_set = {str(numero) for numero in numeros}
    df_filtrado = df_atual[~df_atual["Número"].astype(str).isin(numeros_set)]
    removidos = len(df_atual) - len(df_filtrado)
    if removidos > 0:
        salvar_planilha_atual(df_filtrado)
    return removidos

def limpar_historico_boletos() -> int:
    removidos = 0
    if PASTA_PROCESSADOS.exists():
        for arquivo in PASTA_PROCESSADOS.glob("*"):
            if arquivo.is_file():
                try:
                    arquivo.unlink()
                    removidos += 1
                except OSError:
                    continue
    return removidos

def limpar_log_processamento() -> bool:
    try:
        ARQUIVO_LOG.write_text("", encoding="utf-8")
        return True
    except OSError:
        return False

def atualizar_status_pagamento(numeros: list[str], pago: bool) -> int:
    if not numeros:
        return 0
    df = ler_planilha_atual()
    if df.empty or "Número" not in df.columns:
        return 0
    numeros_set = {str(numero) for numero in numeros}
    hoje = pd.Timestamp.now().normalize()
    alterados = 0
    for idx, linha in df.iterrows():
        chave = str(linha.get("Número", ""))
        if chave in numeros_set:
            if pago:
                df.at[idx, "Dt. Pagamento"] = hoje
            else:
                df.at[idx, "Dt. Pagamento"] = pd.NaT
            alterados += 1
    if alterados:
        salvar_planilha_atual(df)
    return alterados

# ---------------------------------------------------------------------------
# Seções da interface (mantidas do seu código)
# ---------------------------------------------------------------------------

def secao_planilha():
    st.markdown("### 📈 Planilha de Automação (tempo real)")
    df_planilha = ler_planilha_atual()

    if df_planilha.empty:
        st.info("Planilha vazia. Processe um boleto para ver os dados.")
        return

    df_planilha = df_planilha.copy()
    df_planilha["Status"] = np.where(
        df_planilha["Dt. Pagamento"].notna(), "Pago", "Pendente"
    )

    total_pago = (df_planilha["Status"] == "Pago").sum()
    total_pendente = (df_planilha["Status"] == "Pendente").sum()

    col_a, col_b = st.columns(2)
    col_a.metric("Títulos pagos", total_pago)
    col_b.metric("Títulos pendentes", total_pendente)

    df_editor = df_planilha.copy()
    df_editor.insert(0, "Linha", range(1, len(df_editor) + 1))

    for coluna in COLUNAS_DATA:
        if coluna in df_editor.columns:
            serie = pd.to_datetime(df_editor[coluna], errors="coerce")
            df_editor.loc[:, coluna] = serie.dt.strftime("%d/%m/%Y")
            df_editor.loc[serie.isna(), coluna] = ""

    st.caption("Edite os campos necessários e salve para atualizar.")
    df_editado = st.data_editor(
        df_editor,
        hide_index=True,
        num_rows="dynamic",
        use_container_width=True,
        column_order=["Linha", "Status"] + [col for col in df_editor.columns if col not in ("Linha", "Status")],
        key="editor_planilha_integrado",
    )

    # Botão de salvar alterações
    if st.button("💾 Salvar alterações", type="primary", use_container_width=True):
        df_salvar = pd.DataFrame(df_editado)
        for coluna in ("Linha", "Status"):
            if coluna in df_salvar.columns:
                df_salvar = df_salvar.drop(columns=[coluna])

        for coluna in COLUNAS_DATA:
            if coluna in df_salvar.columns:
                df_salvar.loc[:, coluna] = df_salvar[coluna].replace("", pd.NA)
                df_salvar.loc[:, coluna] = pd.to_datetime(
                    df_salvar[coluna], dayfirst=True, errors="coerce"
                )

        for coluna in COLUNAS_NUMERICAS:
            if coluna in df_salvar.columns:
                df_salvar.loc[:, coluna] = pd.to_numeric(df_salvar[coluna], errors="coerce")

        salvar_planilha_atual(df_salvar)
        st.session_state["feedback_message"] = "Planilha atualizada!"
        st.cache_data.clear()
        rerun()

    with st.expander("✅ Atualizar status de pagamento", expanded=False):
        pendentes = df_planilha[df_planilha["Dt. Pagamento"].isna()]
        pagos = df_planilha[df_planilha["Dt. Pagamento"].notna()]

        col_pendente, col_pago = st.columns(2)
        with col_pendente:
            selecionados_pendentes = st.multiselect(
                "Títulos pendentes",
                pendentes["Número"].astype(str) if not pendentes.empty else [],
                key="pendentes_select",
            )
            if st.button("✅ Marcar como pagos", use_container_width=True):
                alterados = atualizar_status_pagamento(selecionados_pendentes, pago=True)
                st.session_state["feedback_message"] = f"{alterados} título(s) atualizados." if alterados else "Nenhum selecionado."
                st.cache_data.clear()
                rerun()

        with col_pago:
            selecionados_pagos = st.multiselect(
                "Títulos pagos",
                pagos["Número"].astype(str) if not pagos.empty else [],
                key="pagos_select",
            )
            if st.button("↩️ Reabrir como pendentes", use_container_width=True):
                alterados = atualizar_status_pagamento(selecionados_pagos, pago=False)
                st.session_state["feedback_message"] = f"{alterados} título(s) reabertos." if alterados else "Nenhum selecionado."
                st.cache_data.clear()
                rerun()

def secao_upload():
    st.markdown("### 📤 Processar novos boletos")

    col_upload, col_instrucoes = st.columns([2, 1], gap="large")

    with col_upload:
        # Usar chave única para resetar o uploader após processar
        if 'uploader_key' not in st.session_state:
            st.session_state.uploader_key = 0

        uploaded_files = st.file_uploader(
            "📁 Selecione os PDFs dos boletos",
            type=["pdf"],
            accept_multiple_files=True,
            key=f"uploader_{st.session_state.uploader_key}"
        )

        if uploaded_files:
            st.success(f"✓ {len(uploaded_files)} arquivo(s) selecionado(s)")

            for file in uploaded_files:
                st.text(f"📄 {file.name} ({file.size / 1024:.1f} KB)")

            if st.button("🚀 Processar Agora", type="primary", use_container_width=True):
                import tempfile
                import shutil

                try:
                    with st.spinner("Processando boletos..."):
                        resultados = []
                        temp_dir = tempfile.mkdtemp()

                        for uploaded_file in uploaded_files:
                            with st.status(f"Processando {uploaded_file.name}...", expanded=True) as status:
                                temp_pdf = os.path.join(temp_dir, uploaded_file.name)
                                with open(temp_pdf, "wb") as f:
                                    f.write(uploaded_file.read())

                                # Usar função embutida melhorada
                                dados = processar_pdf_integrado(temp_pdf)

                                if dados:
                                    # Adicionar na planilha
                                    if adicionar_na_planilha_integrado(dados, str(ARQUIVO_EXCEL)):
                                        status.update(label=f"✓ {uploaded_file.name} processado!", state="complete")

                                        # Mover para processados
                                        try:
                                            destino = PASTA_PROCESSADOS / uploaded_file.name
                                            shutil.move(temp_pdf, str(destino))
                                        except:
                                            pass

                                        # Salvar log
                                        try:
                                            with open(ARQUIVO_LOG, 'a', encoding='utf-8') as f:
                                                timestamp = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                                                f.write(f"[{timestamp}] ✓ Processado: {uploaded_file.name} - R$ {dados['Valor']:.2f}\n")
                                        except:
                                            pass

                                        resultados.append({
                                            "Arquivo": uploaded_file.name,
                                            "Status": "✅ Sucesso",
                                            "Fornecedor": dados["Fornecedor"],
                                            "Valor": formatar_brl(dados["Valor"]),
                                            "Vencimento": dados["Vencimento"],
                                        })
                                    else:
                                        status.update(label=f"✗ Erro ao salvar {uploaded_file.name}", state="error")
                                        resultados.append({
                                            "Arquivo": uploaded_file.name,
                                            "Status": "❌ Erro ao salvar",
                                            "Fornecedor": "-",
                                            "Valor": "-",
                                            "Vencimento": "-",
                                        })
                                else:
                                    status.update(label=f"✗ Falha em {uploaded_file.name}", state="error")
                                    resultados.append({
                                        "Arquivo": uploaded_file.name,
                                        "Status": "❌ Falha na extração",
                                        "Fornecedor": "-",
                                        "Valor": "-",
                                        "Vencimento": "-",
                                    })

                        shutil.rmtree(temp_dir, ignore_errors=True)

                    st.success(f"✓ Concluído! ({len([r for r in resultados if '✅' in r['Status']])}/{len(resultados)} sucesso)")
                    st.markdown("#### Resultados:")
                    st.dataframe(pd.DataFrame(resultados), use_container_width=True, hide_index=True)

                    # Incrementar a chave para resetar o file_uploader
                    st.session_state.uploader_key += 1

                    st.cache_data.clear()
                    rerun()

                except Exception as e:
                    st.error(f"❌ Erro: {e}")
                    import traceback
                    st.code(traceback.format_exc())
        else:
            st.info("👆 Selecione arquivos PDF para começar")

    with col_instrucoes:
        st.markdown("#### 📋 Instruções")
        st.markdown("""
**Como funciona:**
1. Clique em "Browse files"
2. Selecione PDFs
3. Clique em "Processar"

---

**Dados extraídos:**
- 💼 Fornecedor
- 💰 Valor
- 📅 Vencimento
- 🔢 Nº Documento

---

**✨ Suporte a múltiplos formatos:**
- Banco Safra
- Braspress
- Itaú
- E outros!

⚡ **97% mais rápido!**
""")

def secao_historico():
    st.markdown("### 📊 Histórico de Processamento")
    try:
        if PASTA_PROCESSADOS.exists():
            pdfs = sorted(
                [arquivo for arquivo in PASTA_PROCESSADOS.iterdir() if arquivo.suffix.lower() == ".pdf"],
                key=lambda p: p.stat().st_mtime, reverse=True,
            )

            if pdfs:
                st.success(f"✓ {len(pdfs)} boleto(s) processado(s)")
                historico = []
                for pdf in pdfs:
                    timestamp = pdf.stat().st_mtime
                    data = datetime.fromtimestamp(timestamp).strftime("%d/%m/%Y %H:%M")
                    historico.append({"Arquivo": pdf.name, "Data Processamento": data})
                df_hist = pd.DataFrame(historico)
                st.dataframe(df_hist, use_container_width=True, hide_index=True)
            else:
                st.info("📭 Nenhum boleto processado ainda")
        else:
            st.warning(f"⚠️ Pasta não encontrada: {PASTA_PROCESSADOS}")
    except Exception as e:
        st.error(f"Erro: {e}")

def secao_log():
    st.markdown("### 📝 Log de Processamento")
    try:
        if ARQUIVO_LOG.exists():
            with open(ARQUIVO_LOG, "r", encoding="utf-8") as f:
                log = f.read()
            if log:
                linhas = log.strip().split("\n")
                st.code("\n".join(linhas[-50:]), language="text")
                st.download_button("📥 Baixar Log", log, "log_processamento.txt", "text/plain")
            else:
                st.info("Log vazio")
        else:
            st.info(f"Nenhum log em {ARQUIVO_LOG}")
    except Exception as e:
        st.error(f"Erro: {e}")

# ---------------------------------------------------------------------------
# Função principal
# ---------------------------------------------------------------------------

def render_dashboard_integrado(embed: bool = False) -> None:
    if not embed:
        st.set_page_config(
            page_title="Dashboard Fusion Tech - Automação",
            page_icon="🧾",
            layout="wide",
            initial_sidebar_state="expanded",
        )

    if "feedback_message" in st.session_state:
        st.toast(st.session_state.pop("feedback_message"))

    if not embed:
        with st.sidebar:
            st.markdown("### ℹ️ Sobre o Projeto")
            st.markdown("""
**Empresa:** Fusion Tech  
**Setor:** Projetores e Acessórios de TI  
**Período:** Jan - Out 2025  
**Objetivo:** Análise + Automação
""")
            st.markdown(f"**📅 Atualizado:** {datetime.now():%d/%m/%Y %H:%M}")

    st.header("🤖 Automação de Boletos")
    st.caption("✅ Agora suporta múltiplos formatos: Banco Safra, Braspress, Itaú e outros!")
    
    tab_planilha, tab_upload, tab_historico, tab_log = st.tabs(
        ["📈 Planilha", "📤 Upload", "📊 Histórico", "📝 Log"]
    )

    with tab_planilha:
        secao_planilha()

    with tab_upload:
        secao_upload()

    with tab_historico:
        secao_historico()

    with tab_log:
        secao_log()

    if not embed:
        st.markdown("---")
        st.markdown("""
<div style='text-align: center; color: #7f8c8d; padding: 20px;'>
    <p><strong>Fusion Tech - Dashboard Integrado</strong></p>
    <p>IBMEC 2025.02 | Programação Estruturada</p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    render_dashboard_integrado(embed=False)