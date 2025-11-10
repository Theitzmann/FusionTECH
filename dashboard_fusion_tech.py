"""
Dashboard Interativo - Análise de Contas a Pagar
Fusion Tech - Projeto de Análise de Dados

Para executar: streamlit run dashboard_fusion_tech.py
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime
import os

# Configuração da página
st.set_page_config(
    page_title="Dashboard Fusion Tech",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

MENU_OPTIONS = ["Dashboard Analítico", "Automação de Boletos"]
menu_principal = st.sidebar.radio("Menu Principal", MENU_OPTIONS, index=0)

if menu_principal == "Automação de Boletos":
    from codigo.dashboard_fusion_tech_integrado import render_dashboard_integrado

    render_dashboard_integrado(embed=True)
    st.stop()

# Estilo CSS customizado
st.markdown("""
    <style>
    .main-header {
        font-size: 48px;
        font-weight: bold;
        color: #ecf0f1;
        text-align: center;
        padding: 20px;
        background: linear-gradient(90deg, #3498db, #2ecc71);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .insight-box {
        background-color: #34495e;
        border-left: 5px solid #e74c3c;
        padding: 20px;
        margin: 10px 0;
        border-radius: 8px;
        color: #ecf0f1;
    }
    .insight-box h3 {
        color: #ecf0f1;
        margin-top: 0;
        font-weight: bold;
    }
    .insight-box p, .insight-box ul, .insight-box li {
        color: #bdc3c7;
        line-height: 1.6;
    }
    .insight-box strong {
        color: #ecf0f1;
    }
    .metric-card {
        background-color: #2c3e50;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        text-align: center;
    }
    </style>
""", unsafe_allow_html=True)

# Função para carregar dados
@st.cache_data
def carregar_dados():
    """Carrega os dados da planilha"""
    try:
        # Tentar diferentes caminhos
        caminhos = ['../dados/contasapagar_1.xlsx', 'dados/contasapagar_1.xlsx']
        for caminho in caminhos:
            if os.path.exists(caminho):
                return pd.read_excel(caminho)
        st.error("❌ Arquivo não encontrado! Verifique se contasapagar_1.xlsx está na pasta 'dados/'")
        return None
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None


def format_brl(valor: float) -> str:
    """Formata valores monetários para o padrão brasileiro."""
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Carregar dados
df = carregar_dados()

if df is not None:
    df = df.replace(r'^\s*$', pd.NA, regex=True)

    # Preparar dados
    df = df.copy()
    colunas_datas = ['Dt. Emissão', 'Dt. Vencimento', 'Dt. Pagamento']
    for coluna in colunas_datas:
        if coluna in df.columns:
            df[coluna] = pd.to_datetime(df[coluna], errors='coerce')
    
    if 'Vr. Título' in df.columns:
        df['Vr. Título'] = pd.to_numeric(df['Vr. Título'], errors='coerce')
    if 'Vr. Dev/Pag' in df.columns:
        df['Vr. Dev/Pag'] = pd.to_numeric(df['Vr. Dev/Pag'], errors='coerce')

    def format_brl(valor: float) -> str:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    # CABEÇALHO
    st.markdown('<p class="main-header">📊 Dashboard Financeiro - Fusion Tech</p>', unsafe_allow_html=True)
    st.markdown("---")
    
    # SIDEBAR - Informações do Projeto
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100/3498db/ffffff?text=Fusion+Tech", use_container_width=True)
        st.title("ℹ️ Sobre o Projeto")
        st.markdown("""
        **Empresa:** Fusion Tech  
        **Setor:** Projetores e Acessórios de TI  
        **Período:** Jan - Out 2025  
        **Objetivo:** Análise de Contas a Pagar
        """)
        
        st.markdown("---")
        st.markdown("**📅 Data da Análise**")
        st.info(datetime.now().strftime("%d/%m/%Y"))
        
        st.markdown("---")
        st.markdown("**👥 Equipe**")
        st.markdown("IBMEC 2025.02  \nProgramação Estruturada")
    
    # CALCULAR MÉTRICAS
    total_registros = len(df)
    contas_pagas = df['Dt. Pagamento'].notna().sum()
    contas_pendentes = df['Dt. Pagamento'].isna().sum()
    hoje = pd.Timestamp.now()
    contas_vencidas = df[(df['Dt. Pagamento'].isna()) & (df['Dt. Vencimento'] < hoje)]
    total_vencido = contas_vencidas['Vr. Título'].sum()
    total_titulos = df['Vr. Título'].sum()
    dados_vazios_critical = df['Dt. Pagamento'].isnull().sum()
    perc_sem_pagamento = (dados_vazios_critical / total_registros * 100) if total_registros else 0
    perc_vencidas = (len(contas_vencidas) / total_registros * 100) if total_registros else 0
    fornecedores_faltantes = df['Fornecedor'].isna().sum() if 'Fornecedor' in df.columns else 0
    historicos_faltantes = df['Histórico'].isna().sum() if 'Histórico' in df.columns else 0
    valores_faltantes = df['Vr. Título'].isna().sum() if 'Vr. Título' in df.columns else 0
    
    # SEÇÃO 1: KPIs PRINCIPAIS
    st.header("📈 Indicadores Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total de Contas",
            value=total_registros,
            delta=None
        )
    
    with col2:
        st.metric(
            label="Contas Vencidas",
            value=len(contas_vencidas)
        )
    
    with col3:
        st.metric(
            label="Valor Vencido",
            value=format_brl(total_vencido),
            delta="Risco Financeiro",
            delta_color="inverse"
        )
    
    with col4:
        st.metric(
            label="Dados Vazios",
            value=f"{dados_vazios_critical} ({(dados_vazios_critical/total_registros*100):.1f}%)"
        )

    st.info(
        f"Alerta financeiro: {format_brl(total_vencido)} permanecem vencidos sem registro de quitação. "
        "Se a planilha não for atualizada em tempo hábil, o acompanhamento perde precisão e decisões críticas "
        "ficam baseadas em dados desatualizados."
    )
    
    st.markdown("---")
    
    # SEÇÃO 2: VISUALIZAÇÕES (MOVIDA PARA ANTES DOS INSIGHTS)
    st.header("📊 Visualizações dos Dados")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Status das Contas", "Formas de Pagamento", "Dados Vazios", "Timeline"])
    
    with tab1:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig, ax = plt.subplots(figsize=(6, 6))
            status_data = [contas_pagas, len(contas_vencidas), contas_pendentes - len(contas_vencidas)]
            labels = ['Pagas', 'Vencidas', 'A Vencer']
            colors = ['#2ecc71', '#e74c3c', '#f39c12']
            explode = (0.05, 0.1, 0)
            
            ax.pie(status_data, labels=labels, autopct='%1.1f%%', startangle=90,
                   colors=colors, explode=explode, shadow=True, textprops={'fontsize': 12, 'weight': 'bold'})
            ax.set_title('Status das Contas - Fusion Tech', fontsize=16, fontweight='bold', pad=20)
            st.pyplot(fig)
        
        with col2:
            st.markdown("### 📌 Análise")
            st.markdown(f"""
            - **{contas_pagas} contas pagas** ({(contas_pagas/total_registros*100):.1f}%)
            - **{len(contas_vencidas)} contas vencidas** ({(len(contas_vencidas)/total_registros*100):.1f}%)
            - **{contas_pendentes - len(contas_vencidas)} contas a vencer** ({((contas_pendentes - len(contas_vencidas))/total_registros*100):.1f}%)
            
            **🔴 Alerta:** Mais da metade das contas estão vencidas!
            """)
    
    with tab2:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            fig, ax = plt.subplots(figsize=(10, 6))
            if 'Forma de Pgto.' in df.columns:
                formas_pgto = df['Forma de Pgto.'].dropna().astype(str).value_counts()
            else:
                formas_pgto = pd.Series(dtype=int)
            colors_bar = ['#3498db', '#9b59b6', '#1abc9c']
            
            if not formas_pgto.empty:
                formas_pgto.plot(kind='bar', ax=ax, color=colors_bar, edgecolor='black', linewidth=1.2)
                ax.set_title('Distribuição por Forma de Pagamento', fontsize=16, fontweight='bold', pad=20)
                ax.set_xlabel('Forma de Pagamento', fontsize=12, fontweight='bold')
                ax.set_ylabel('Quantidade', fontsize=12, fontweight='bold')
                ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
                
                for i, v in enumerate(formas_pgto.values):
                    ax.text(i, v + 0.3, str(v), ha='center', va='bottom', fontweight='bold')
                
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.info("Não há dados suficientes para gerar o gráfico de formas de pagamento.")
        
        with col2:
            st.markdown("### 📌 Análise")
            if not formas_pgto.empty:
                top_formas = formas_pgto.head(3)
                linhas = []
                for idx, (nome, qtd) in enumerate(top_formas.items(), start=1):
                    percentual = (qtd / total_registros * 100) if total_registros else 0
                    linhas.append(f"{idx}. **{nome}:** {qtd} ({percentual:.1f}%)")
                itens = "\n".join(linhas)
                st.markdown(
                    "**Formas de pagamento mais recorrentes:**\n\n"
                    f"{itens}\n\n"
                    "A concentração em poucas modalidades reforça a necessidade de automação para controle."
                )
            else:
                st.markdown("Não foram identificadas formas de pagamento registradas na planilha.")
    
    with tab3:
        col1, col2 = st.columns([2, 1])
        
        with col1:
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
            
            for i, (v, p) in enumerate(zip(dados_vazios.values, percentual.values)):
                ax.text(v + 0.5, i, f'{v} ({p}%)', va='center', fontweight='bold')
            
            ref_line = len(df) * 0.2
            ax.axvline(x=ref_line, color='red', linestyle='--', linewidth=2, alpha=0.7, label='Limite 20%')
            ax.legend()
            
            plt.tight_layout()
            st.pyplot(fig)
        
        with col2:
            st.markdown("### 📌 Análise")
            st.markdown(f"""
            **Problema crítico:**
            
            🔴 **Dt. Pagamento:** {perc_sem_pagamento:.1f}% vazio
            
            Todas as outras colunas estão com menos de 6% de dados vazios, o que é aceitável.
            
            O problema está concentrado no **registro de pagamentos**, confirmando a necessidade de automação.
            """)
    
    with tab4:
        possui_vencimento = 'Dt. Vencimento' in df.columns
        if possui_vencimento:
            df_timeline = df[df['Dt. Vencimento'].notna()].copy()
            df_timeline['Mes_Venc'] = df_timeline['Dt. Vencimento'].dt.to_period('M')
            vencimentos_mes = df_timeline.groupby('Mes_Venc').size().sort_index()
        else:
            vencimentos_mes = pd.Series(dtype=int)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if not vencimentos_mes.empty:
                fig, ax = plt.subplots(figsize=(12, 6))
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
                
                for i, v in enumerate(vencimentos_mes.values):
                    ax.text(i, v + 0.2, str(v), ha='center', va='bottom', fontweight='bold')
                
                plt.tight_layout()
                st.pyplot(fig)
            else:
                mensagem = (
                    "Não há registros de vencimento suficientes para montar a timeline."
                    if possui_vencimento
                    else "A planilha não contém a coluna 'Dt. Vencimento'."
                )
                st.info(mensagem)
        
        with col2:
            st.markdown("### 📌 Análise")
            if not vencimentos_mes.empty:
                top_meses = vencimentos_mes.sort_values(ascending=False).head(3)
                linhas = [f"- {str(mes)} ({qtd} conta(s))" for mes, qtd in top_meses.items()]
                itens = "\n".join(linhas) if linhas else "- Distribuição uniforme"
                st.markdown(
                    "**Picos de vencimento identificados:**\n\n"
                    f"{itens}\n\n"
                    "A irregularidade reforça a importância de planejamento financeiro e automatização dos registros."
                )
            else:
                if possui_vencimento:
                    st.markdown("Não há dados suficientes para analisar o comportamento dos vencimentos.")
                else:
                    st.markdown("A planilha não possui informação de vencimentos para análise.")
    
    st.markdown("---")
    
    # SEÇÃO 3: PRINCIPAIS INSIGHTS (MOVIDA PARA DEPOIS DOS GRÁFICOS)
    st.header("🔍 Principais Insights do Problema")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="insight-box">
        <h3>🚨 Problema Crítico #1: Controle de Pagamentos</h3>
        <p><strong>{percent:.1f}% das contas não possuem data de pagamento registrada.</strong></p>
        <p>Isso impossibilita:</p>
        <ul>
            <li>Saber quais contas realmente foram pagas</li>
            <li>Fazer projeções de fluxo de caixa</li>
            <li>Identificar atrasos e pendências</li>
        </ul>
        <p><strong>Causa:</strong> Preenchimento manual da planilha pelo proprietário, sem tempo nem funcionários dedicados.</p>
        </div>
        """.format(percent=perc_sem_pagamento), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="insight-box">
        <h3>💰 Problema Crítico #2: Contas Vencidas</h3>
        <p><strong>{perc_vencidas:.1f}% das contas estão vencidas e não pagas ({valor_vencido}).</strong></p>
        <p>Riscos:</p>
        <ul>
            <li>Possíveis multas e juros acumulados</li>
            <li>Comprometimento do relacionamento com fornecedores</li>
            <li>Impacto negativo no crédito da empresa</li>
        </ul>
        <p><strong>Observação:</strong> Pode haver contas pagas mas não registradas na planilha.</p>
        </div>
        """.format(perc_vencidas=perc_vencidas, valor_vencido=format_brl(total_vencido)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="insight-box">
        <h3>📊 Problema #3: Inconsistência nos Dados</h3>
        <p><strong>Múltiplas colunas com informações incompletas:</strong></p>
        <ul>
            <li>{forn_sem} registro(s) sem fornecedor identificado</li>
            <li>{hist_sem} registro(s) sem histórico</li>
            <li>{valor_sem} registro(s) sem valor informado</li>
        </ul>
        <p>Isso gera <strong>incoerência na receita final</strong> devido à falta de informações sobre despesas reais.</p>
        </div>
        """.format(
            forn_sem=fornecedores_faltantes,
            hist_sem=historicos_faltantes,
            valor_sem=valores_faltantes
        ), unsafe_allow_html=True)
        
        st.markdown("""
        <div class="insight-box">
        <h3>⚙️ Raiz do Problema</h3>
        <p><strong>Falta de automação e processo manual</strong></p>
        <p>Confirmado pelo proprietário em visita técnica (27/10/2025):</p>
        <ul>
            <li>Planilha preenchida manualmente</li>
            <li>Falta de funcionários dedicados</li>
            <li>Sem sistema de gestão financeira</li>
            <li>Gargalo operacional significativo</li>
        </ul>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # SEÇÃO 4: PROPOSTA DE SOLUÇÃO
    st.header("💡 Proposta de Solução")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🎯 Solução Proposta: Sistema de Gestão Automatizado
        
        **Objetivo:** Automatizar o registro de contas a pagar através da captura e processamento de boletos em PDF.
        
        **Funcionalidades principais:**
        1. **Captura automática de dados** de boletos/PDFs
        2. **Preenchimento automático** da planilha financeira
        3. **Dashboard em tempo real** com:
           - Contas a Vencer
           - Contas Vencidas
           - Histórico de Pagamentos
        4. **Alertas automáticos** de vencimento
        
        **Benefícios esperados:**
        - ✅ Redução de 90% no tempo de preenchimento manual
        - ✅ Eliminação de erros humanos
        - ✅ Visão completa do fluxo financeiro
        - ✅ Melhor controle de contas vencidas
        - ✅ Dados consistentes para análise
        """)
    
    with col2:
        st.markdown("""
        ### 📊 Impacto Esperado
        
        **Situação Atual:**
        - 69% dos registros sem data de pagamento
        - 53% de contas vencidas
        - Controle financeiro precário
        - Risco de multas e juros
        
        **Com a Solução:**
        - 100% dos pagamentos registrados automaticamente
        - Alertas antes do vencimento
        - Dashboard visual para tomada de decisão
        - Histórico completo e organizado
        - Redução de custos operacionais
        - Melhor relacionamento com fornecedores
        """)
    
    st.markdown("---")
    
    # FOOTER
    st.markdown("""
    <div style='text-align: center; color: #7f8c8d; padding: 20px;'>
        <p><strong>Projeto Fusion Tech - Análise de Dados</strong></p>
        <p>IBMEC 2025.02 | Programação Estruturada</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.error("❌ Não foi possível carregar os dados. Verifique se o arquivo está na pasta correta.")
