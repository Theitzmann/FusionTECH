"""
Análise Inicial - Contas a Pagar Fusion Tech
Análise de qualidade dos dados e insights básicos

Projeto: Análise de Dados - Fusion Tech
Disciplina: Programação Estruturada
Instituição: IBMEC 2025.02
"""

import pandas as pd
import numpy as np
import os
import sys
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# Importar configurações
try:
    from config import ARQUIVO_CONTAS_PAGAR, NOME_EMPRESA
except ImportError:
    print("⚠️  Arquivo config.py não encontrado. Usando caminho relativo.")
    ARQUIVO_CONTAS_PAGAR = 'dados\contasapagar_1.xlsx'
    NOME_EMPRESA = "Fusion Tech"

def carregar_dados():
    """Carrega a planilha de contas a pagar"""
    print(f"Carregando dados de: {ARQUIVO_CONTAS_PAGAR}")
    
    if not os.path.exists(ARQUIVO_CONTAS_PAGAR):
        print(f"❌ ERRO: Arquivo não encontrado!")
        print(f"   Caminho esperado: {ARQUIVO_CONTAS_PAGAR}")
        print(f"   Diretório atual: {os.getcwd()}")
        sys.exit(1)
    
    try:
        df = pd.read_excel(ARQUIVO_CONTAS_PAGAR)
        print(f"✓ Dados carregados com sucesso! ({len(df)} registros)\n")
        return df
    except Exception as e:
        print(f"❌ Erro ao carregar arquivo: {e}")
        sys.exit(1)

def analisar_dados_vazios(df):
    """Analisa quantidade de dados não preenchidos"""
    print("[2] ANÁLISE DE DADOS NÃO PREENCHIDOS")
    print("-" * 70)
    
    dados_vazios = df.isnull().sum()
    percentual_vazios = (df.isnull().sum() / len(df)) * 100
    
    resumo_vazios = pd.DataFrame({
        'Coluna': dados_vazios.index,
        'Qtd. Vazios': dados_vazios.values,
        'Percentual': percentual_vazios.values
    })
    
    print(resumo_vazios.to_string(index=False))
    
    # Identificar colunas problemáticas (>20% de dados vazios)
    colunas_problematicas = resumo_vazios[resumo_vazios['Percentual'] > 20]
    if len(colunas_problematicas) > 0:
        print(f"\n⚠️  ATENÇÃO: {len(colunas_problematicas)} coluna(s) com mais de 20% de dados vazios:")
        for _, row in colunas_problematicas.iterrows():
            print(f"   - {row['Coluna']}: {row['Percentual']:.1f}% vazios")
    
    return resumo_vazios, colunas_problematicas

def analisar_financeiro(df):
    """Analisa informações financeiras básicas"""
    print("\n[3] ANÁLISE FINANCEIRA BÁSICA")
    print("-" * 70)
    
    # Verificar se há valores não preenchidos
    valores_titulo_vazios = df['Vr. Título'].isnull().sum()
    valores_pago_vazios = df['Vr. Dev/Pag'].isnull().sum()
    
    print(f"Valores de Título não preenchidos: {valores_titulo_vazios}")
    print(f"Valores Pagos não preenchidos: {valores_pago_vazios}")
    
    # Calcular totais (ignorando valores nulos)
    total_titulos = df['Vr. Título'].sum()
    total_pago = df['Vr. Dev/Pag'].sum()
    
    print(f"\nTotal em Títulos: R$ {total_titulos:,.2f}")
    print(f"Total Pago: R$ {total_pago:,.2f}")
    print(f"Diferença: R$ {(total_titulos - total_pago):,.2f}")
    
    return {
        'total_titulos': total_titulos,
        'total_pago': total_pago,
        'valores_titulo_vazios': valores_titulo_vazios,
        'valores_pago_vazios': valores_pago_vazios
    }

def analisar_pagamentos(df):
    """Analisa status dos pagamentos"""
    print("\n[4] ANÁLISE DE PAGAMENTOS")
    print("-" * 70)
    
    # Contas pagas (com data de pagamento)
    contas_pagas = df['Dt. Pagamento'].notna().sum()
    contas_pendentes = df['Dt. Pagamento'].isna().sum()
    
    print(f"Contas pagas: {contas_pagas} ({(contas_pagas/len(df)*100):.1f}%)")
    print(f"Contas pendentes: {contas_pendentes} ({(contas_pendentes/len(df)*100):.1f}%)")
    
    # Verificar contas vencidas (data vencimento passou e sem data de pagamento)
    hoje = pd.Timestamp.now()
    contas_vencidas = df[(df['Dt. Pagamento'].isna()) & (df['Dt. Vencimento'] < hoje)]
    print(f"Contas vencidas (não pagas): {len(contas_vencidas)}")
    
    if len(contas_vencidas) > 0:
        valor_vencido = contas_vencidas['Vr. Título'].sum()
        print(f"Valor total vencido: R$ {valor_vencido:,.2f}")
    
    return {
        'contas_pagas': contas_pagas,
        'contas_pendentes': contas_pendentes,
        'contas_vencidas': len(contas_vencidas)
    }

def analisar_fornecedores(df):
    """Analisa informações sobre fornecedores"""
    print("\n[5] ANÁLISE DE FORNECEDORES")
    print("-" * 70)
    
    fornecedores_unicos = df['Fornecedor'].nunique()
    fornecedores_vazios = df['Fornecedor'].isnull().sum()
    
    print(f"Fornecedores únicos: {fornecedores_unicos}")
    print(f"Registros sem fornecedor: {fornecedores_vazios}")
    
    if fornecedores_vazios == 0:
        top_fornecedores = df['Fornecedor'].value_counts().head(5)
        print("\nTop 5 fornecedores (por quantidade de registros):")
        for fornecedor, count in top_fornecedores.items():
            print(f"   - {fornecedor}: {count} registro(s)")
    
    return fornecedores_unicos, fornecedores_vazios

def analisar_formas_pagamento(df):
    """Analisa distribuição das formas de pagamento"""
    print("\n[6] FORMAS DE PAGAMENTO")
    print("-" * 70)
    
    formas_pgto = df['Forma de Pgto.'].value_counts()
    print("Distribuição por forma de pagamento:")
    for forma, count in formas_pgto.items():
        print(f"   - {forma}: {count} registro(s) ({(count/len(df)*100):.1f}%)")
    
    return formas_pgto

def gerar_resumo_executivo(df, resultados_financeiro, resultados_pagamentos, 
                          colunas_problematicas, fornecedores_vazios):
    """Gera resumo executivo com principais problemas identificados"""
    print("\n" + "="*70)
    print("RESUMO EXECUTIVO - PRINCIPAIS PROBLEMAS IDENTIFICADOS")
    print("="*70)
    
    problemas = []
    
    # Verificar dados vazios críticos
    if resultados_financeiro['valores_titulo_vazios'] > 0:
        problemas.append(f"• {resultados_financeiro['valores_titulo_vazios']} registro(s) sem valor de título")
    
    if fornecedores_vazios > 0:
        problemas.append(f"• {fornecedores_vazios} registro(s) sem fornecedor identificado")
    
    if len(colunas_problematicas) > 0:
        problemas.append(f"• {len(colunas_problematicas)} coluna(s) com mais de 20% de dados vazios")
    
    if resultados_pagamentos['contas_vencidas'] > 0:
        problemas.append(f"• {resultados_pagamentos['contas_vencidas']} conta(s) vencida(s) e não paga(s)")
    
    if len(problemas) > 0:
        print("\nProblemas identificados:")
        for problema in problemas:
            print(problema)
    else:
        print("\n✓ Nenhum problema crítico identificado!")
    
    print("\n" + "="*70)

def criar_visualizacoes(df, resultados_pagamentos):
    """Cria visualizações gráficas dos dados"""
    print("\n" + "="*70)
    print("GERANDO VISUALIZAÇÕES")
    print("="*70)
    
    # Configurar estilo dos gráficos
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (12, 8)
    
    # Criar pasta de análises se não existir
    try:
        from config import PASTA_ANALISES
        pasta_graficos = PASTA_ANALISES
    except:
        pasta_graficos = '../analises'
    
    if not os.path.exists(pasta_graficos):
        os.makedirs(pasta_graficos)
    
    # GRÁFICO 1: Status dos Pagamentos (Pizza)
    print("\n[1] Criando gráfico de status dos pagamentos...")
    fig, ax = plt.subplots(figsize=(10, 7))
    
    status_data = [
        resultados_pagamentos['contas_pagas'],
        resultados_pagamentos['contas_vencidas'],
        resultados_pagamentos['contas_pendentes'] - resultados_pagamentos['contas_vencidas']
    ]
    labels = ['Pagas', 'Vencidas', 'A Vencer']
    colors = ['#2ecc71', '#e74c3c', '#f39c12']
    explode = (0.05, 0.1, 0)
    
    ax.pie(status_data, labels=labels, autopct='%1.1f%%', startangle=90,
           colors=colors, explode=explode, shadow=True)
    ax.set_title('Status das Contas - Fusion Tech', fontsize=16, fontweight='bold', pad=20)
    
    plt.tight_layout()
    caminho1 = os.path.join(pasta_graficos, '01_status_pagamentos.png')
    plt.savefig(caminho1, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"    ✓ Salvo em: {caminho1}")
    
    # GRÁFICO 2: Formas de Pagamento (Barras)
    print("\n[2] Criando gráfico de formas de pagamento...")
    fig, ax = plt.subplots(figsize=(10, 6))
    
    formas_pgto = df['Forma de Pgto.'].value_counts()
    colors_bar = ['#3498db', '#9b59b6', '#1abc9c']
    
    formas_pgto.plot(kind='bar', ax=ax, color=colors_bar, edgecolor='black', linewidth=1.2)
    ax.set_title('Distribuição por Forma de Pagamento', fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Forma de Pagamento', fontsize=12, fontweight='bold')
    ax.set_ylabel('Quantidade', fontsize=12, fontweight='bold')
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
    
    # Adicionar valores em cima das barras
    for i, v in enumerate(formas_pgto.values):
        ax.text(i, v + 0.3, str(v), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    caminho2 = os.path.join(pasta_graficos, '02_formas_pagamento.png')
    plt.savefig(caminho2, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"    ✓ Salvo em: {caminho2}")
    
    # GRÁFICO 3: Dados Vazios (Barras Horizontais)
    print("\n[3] Criando gráfico de dados vazios...")
    fig, ax = plt.subplots(figsize=(10, 8))
    
    dados_vazios = df.isnull().sum().sort_values(ascending=True)
    percentual = (dados_vazios / len(df) * 100).round(1)
    
    colors_vazios = ['#e74c3c' if x > 20 else '#3498db' for x in percentual]
    
    y_pos = range(len(dados_vazios))
    ax.barh(y_pos, dados_vazios.values, color=colors_vazios, edgecolor='black', linewidth=1)
    ax.set_yticks(y_pos)
    ax.set_yticklabels(dados_vazios.index)
    ax.set_xlabel('Quantidade de Dados Vazios', fontsize=12, fontweight='bold')
    ax.set_title('Análise de Dados Não Preenchidos', fontsize=16, fontweight='bold', pad=20)
    
    # Adicionar percentuais
    for i, (v, p) in enumerate(zip(dados_vazios.values, percentual.values)):
        ax.text(v + 0.5, i, f'{v} ({p}%)', va='center', fontweight='bold')
    
    # Linha de referência 20%
    max_val = dados_vazios.max()
    ref_line = len(df) * 0.2
    ax.axvline(x=ref_line, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Limite 20%')
    ax.legend()
    
    plt.tight_layout()
    caminho3 = os.path.join(pasta_graficos, '03_dados_vazios.png')
    plt.savefig(caminho3, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"    ✓ Salvo em: {caminho3}")
    
    # GRÁFICO 4: Timeline de Vencimentos
    print("\n[4] Criando timeline de vencimentos...")
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Preparar dados
    df_timeline = df[df['Dt. Vencimento'].notna()].copy()
    df_timeline['Mes_Venc'] = df_timeline['Dt. Vencimento'].dt.to_period('M')
    vencimentos_mes = df_timeline.groupby('Mes_Venc').size().sort_index()
    
    # Converter período para string para plotar
    meses_str = [str(m) for m in vencimentos_mes.index]
    
    ax.plot(range(len(vencimentos_mes)), vencimentos_mes.values, marker='o', 
            linewidth=2.5, markersize=8, color='#e74c3c', markerfacecolor='#c0392b')
    ax.fill_between(range(len(vencimentos_mes)), vencimentos_mes.values, alpha=0.3, color='#e74c3c')
    
    ax.set_xticks(range(len(vencimentos_mes)))
    ax.set_xticklabels(meses_str, rotation=45, ha='right')
    ax.set_xlabel('Mês de Vencimento', fontsize=12, fontweight='bold')
    ax.set_ylabel('Quantidade de Contas', fontsize=12, fontweight='bold')
    ax.set_title('Timeline de Vencimentos', fontsize=16, fontweight='bold', pad=20)
    ax.grid(True, alpha=0.3)
    
    # Adicionar valores nos pontos
    for i, v in enumerate(vencimentos_mes.values):
        ax.text(i, v + 0.2, str(v), ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    caminho4 = os.path.join(pasta_graficos, '04_timeline_vencimentos.png')
    plt.savefig(caminho4, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"    ✓ Salvo em: {caminho4}")
    
    print("\n✓ Todas as visualizações foram criadas com sucesso!")
    print(f"✓ Arquivos salvos em: {pasta_graficos}")
    print("="*70)

def main():
    """Função principal que executa todas as análises"""
    print("\n" + "="*70)
    print(f"ANÁLISE DE DADOS - CONTAS A PAGAR {NOME_EMPRESA}")
    print("="*70)
    
    df = carregar_dados()
    
    print("[1] INFORMAÇÕES GERAIS")
    print("-" * 70)
    print(f"Total de registros: {len(df)}")
    print(f"Total de colunas: {len(df.columns)}")
    print(f"Período dos dados: {df['Dt. Emissão'].min().strftime('%d/%m/%Y')} a {df['Dt. Emissão'].max().strftime('%d/%m/%Y')}")
    print()
    
    resumo_vazios, colunas_problematicas = analisar_dados_vazios(df)
    
    resultados_financeiro = analisar_financeiro(df)
    
    resultados_pagamentos = analisar_pagamentos(df)
    
    fornecedores_unicos, fornecedores_vazios = analisar_fornecedores(df)
    
    analisar_formas_pagamento(df)
    
    gerar_resumo_executivo(df, resultados_financeiro, resultados_pagamentos, 
                          colunas_problematicas, fornecedores_vazios)
    
    print("Análise concluída!")
    print("="*70)
    
    # 8. Criar visualizações
    criar_visualizacoes(df, resultados_pagamentos)
    
    print("\n💡 Análise completa! Verifique os gráficos na pasta 'analises/'\n")

if __name__ == "__main__":
    main()
