# FusionTech - Sistema de Análise Financeira e Automação de Boletos

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Status](https://img.shields.io/badge/Status-Ativo-success)

## 📋 Sobre o Projeto

FusionTech é um sistema completo de análise financeira e automação de processos para gestão de contas a pagar. O projeto identifica ineficiências nos processos financeiros, automatiza a extração de dados de boletos em PDF e fornece dashboards interativos com insights em tempo real.

### Problemas Resolvidos
- ✅ **69% dos registros sem data de pagamento** - Automação de preenchimento
- ✅ **53% das contas em atraso** - Alertas e acompanhamento visual
- ✅ **Nomes inconsistentes de fornecedores** - Validação de dados
- ✅ **Múltiplas lacunas nos dados** - Identificação automática de problemas

## 🚀 Funcionalidades

### Dashboard Interativo
- 📊 Visualização em tempo real de métricas financeiras
- 📈 Análise de status de pagamentos
- 💳 Distribuição por formas de pagamento
- 📅 Timeline de vencimentos
- ⚠️ Alertas de contas em atraso

### Automação de Boletos
- 📄 Extração automática de dados de PDFs de boletos
- 🔄 Preenchimento automático de planilhas Excel
- 📝 Log de processamento para auditoria
- ✅ Validação de dados extraídos

### Análise de Qualidade de Dados
- 🔍 Identificação de dados faltantes
- 📊 Geração de gráficos de análise
- 📈 Métricas de qualidade de dados
- 💾 Exportação de relatórios visuais

## 🛠️ Tecnologias Utilizadas

### Core
- **Python 3.7+** - Linguagem principal
- **Streamlit** - Framework para dashboards interativos

### Processamento de Dados
- **Pandas** - Manipulação de dados e Excel
- **NumPy** - Computação numérica
- **OpenPyXL** - Operações em arquivos Excel

### Visualização
- **Matplotlib** - Geração de gráficos
- **Seaborn** - Visualizações estatísticas

### Automação
- **PDFPlumber** - Extração de texto de PDFs

## 📁 Estrutura do Projeto

```
FusionTech/
├── codigo/                                    # Código-fonte
│   ├── automacao_boletos.py                  # Automação de extração de PDFs
│   ├── analise_contas_pagar.py               # Análise de qualidade de dados
│   ├── dashboard_fusion_tech_integrado.py    # Dashboard integrado
│   └── teste_ambiente.py                     # Verificador de dependências
├── dados/                                     # Dados e arquivos
│   ├── contasapagar_1.xlsx                   # Planilha principal
│   ├── contasapagar_automacao.xlsx           # Saída da automação
│   ├── boletos_processados/                  # PDFs processados
│   └── log_processamento.txt                 # Logs de processamento
├── analises/                                  # Gráficos gerados
│   ├── 01_status_pagamentos.png
│   ├── 02_formas_pagamento.png
│   ├── 03_dados_vazios.png
│   └── 04_timeline_vencimentos.png
├── documentacao/                              # Documentação adicional
├── dashboard_fusion_tech.py                   # Ponto de entrada principal
├── requirements.txt                           # Dependências do projeto
└── README.md                                  # Este arquivo
```

## 💻 Instalação

### Pré-requisitos
- Python 3.7 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone o repositório**
```bash
git clone https://github.com/Theitzmann/FusionTECH.git
cd FusionTech
```

2. **Crie um ambiente virtual (recomendado)**
```bash
python -m venv venv
```

3. **Ative o ambiente virtual**
- Windows:
```bash
venv\Scripts\activate
```
- Linux/Mac:
```bash
source venv/bin/activate
```

4. **Instale as dependências**
```bash
pip install -r requirements.txt
```

5. **Verifique a instalação**
```bash
python codigo/teste_ambiente.py
```

## 🎯 Como Usar

### 1. Dashboard Principal

Execute o dashboard interativo:
```bash
streamlit run dashboard_fusion_tech.py
```

O dashboard abrirá no navegador (geralmente em `http://localhost:8501`) e exibirá:
- Métricas gerais de contas a pagar
- Gráficos de status de pagamentos
- Análise de formas de pagamento
- Timeline de vencimentos

### 2. Automação de Boletos

Para processar boletos em PDF:
```bash
python codigo/automacao_boletos.py
```

O script irá:
1. Ler todos os PDFs da pasta `dados/boletos_processados/`
2. Extrair informações (número, fornecedor, valor, data de vencimento)
3. Atualizar a planilha `dados/contasapagar_automacao.xlsx`
4. Gerar log em `dados/log_processamento.txt`

### 3. Análise de Qualidade de Dados

Para executar análise completa:
```bash
python codigo/analise_contas_pagar.py
```

Isso gera 4 gráficos na pasta `analises/`:
- Status de pagamentos (pizza)
- Formas de pagamento (barras)
- Análise de dados vazios
- Timeline de vencimentos

### 4. Dashboard Integrado

Para o dashboard com automação integrada:
```bash
streamlit run codigo/dashboard_fusion_tech_integrado.py
```

## 📊 Formato dos Dados

### Estrutura da Planilha Excel

| Coluna | Descrição | Tipo |
|--------|-----------|------|
| Número | Número do boleto/título | Texto |
| Fornecedor | Nome do fornecedor | Texto |
| Plano de contas | Classificação contábil | Texto |
| Histórico | Descrição do pagamento | Texto |
| Dt. Emissão | Data de emissão | Data |
| Dt. Vencimento | Data de vencimento | Data |
| Dt. Pagamento | Data do pagamento | Data |
| Vr. Título | Valor do título | Numérico |
| Vr. Dev/Pag | Valor pago | Numérico |
| Forma de Pgto. | Forma de pagamento | Texto |

### Requisitos para PDFs de Boletos

Os PDFs devem conter:
- Número do documento
- Nome do fornecedor/beneficiário
- Valor do boleto
- Data de vencimento

## 🔧 Troubleshooting

### Erro ao importar bibliotecas

**Problema:** `ModuleNotFoundError: No module named 'pandas'`

**Solução:**
```bash
pip install -r requirements.txt
```

### Erro ao processar PDFs

**Problema:** PDFs não são processados corretamente

**Soluções:**
- Verifique se os PDFs estão na pasta `dados/boletos_processados/`
- Confirme que os PDFs não estão protegidos por senha
- Verifique o log em `dados/log_processamento.txt`

### Dashboard não abre no navegador

**Problema:** Streamlit não inicia

**Solução:**
```bash
# Verifique se o Streamlit está instalado
pip install streamlit --upgrade

# Execute com porta específica
streamlit run dashboard_fusion_tech.py --server.port 8501
```

### Erros de encoding em arquivos Excel

**Problema:** Caracteres especiais aparecem incorretamente

**Solução:** O código usa `encoding='latin1'` por padrão. Se necessário, ajuste no arquivo de código para `encoding='utf-8'`.

## 📈 Métricas e KPIs

O sistema monitora:
- **Taxa de completude de dados** - Percentual de campos preenchidos
- **Taxa de atraso** - Percentual de contas vencidas
- **Volume por fornecedor** - Ranking de fornecedores
- **Distribuição de pagamentos** - Por método de pagamento
- **Timeline financeiro** - Previsão de vencimentos

## 🔜 Melhorias Futuras

- [ ] Integração com APIs bancárias
- [ ] Notificações automáticas de vencimentos
- [ ] Machine Learning para previsão de atrasos
- [ ] Export para Power BI
- [ ] API REST para integração com outros sistemas
- [ ] Autenticação e controle de acesso
- [ ] Histórico de alterações (audit trail)
- [ ] Relatórios em PDF automatizados

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto é proprietário da FusionTech.

## 👤 Autor

**Tiago Itzmann** - [@Theitzmann](https://github.com/Theitzmann)

## 📧 Contato

Para dúvidas ou sugestões, abra uma [issue](https://github.com/Theitzmann/FusionTECH/issues) no repositório.

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no GitHub!
