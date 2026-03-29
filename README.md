# 🏗️ Assistente Técnico de Engenharia Civil no Telegram

> **Projeto Acadêmico (TCC + Projetos Integradores I, II e III) – Engenharia Civil**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://core.telegram.org/bots)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini-orange.svg)](https://ai.google.dev/)
[![Clean Architecture](https://img.shields.io/badge/Architecture-Clean-success.svg)](#)
[![Pytest](https://img.shields.io/badge/Tests-37%20passed-brightgreen.svg)](#)
[![Deploy](https://img.shields.io/badge/Deploy-Azure%20Container%20Apps-0078D4.svg)](https://azure.microsoft.com/)

---

## 📋 Visão Geral

Bot de Telegram que atua como **mentor técnico** para **engenheiros e arquitetos recém-formados**, simulando o papel de um "colega sênior" disponível 24h. Construído sob os princípios da **Clean Architecture** e **Domain-Driven Design (DDD)**, integra a API do Google Gemini para análise inteligente e orientação técnica.

O bot cobre **quatro módulos acadêmicos**, cada um vinculado a um trabalho de conclusão:

| # | Módulo | Projeto | Norma |
|---|--------|---------|-------|
| 📸 | Patologias Construtivas | TCC | NBR 9575, 15575, 13752 |
| 🌱 | Sustentabilidade e Reuso de Água | Projeto Integrador I | ABNT NBR 15527 |
| 🏢 | Avaliação Pós-Ocupação (APO) | Projeto Integrador II | NBR 15575 |
| 📋 | Regularização de Imóveis | Projeto Integrador III | Lei 13.465/2017; Lei 6.766/79 |

---

## 🚀 Funcionalidades

### 📸 Patologias Construtivas (TCC)
- Análise de fotos de vistoria diretamente pelo chat do Telegram
- Classificação preliminar: fissura, trinca, rachadura ou infiltração
- Referência normativa automática (NBR 9575, 13752, 15575)
- Linguagem técnica orientada à composição de laudos de campo

### 🌱 Reuso de Água Pluvial (PI I)
- Coleta de dados via fluxo conversacional guiado (cidade, área, moradores)
- **Cálculo local** em Python seguindo o Método de Azevedo Netto (NBR 15527)
- Fórmulas exibidas passo a passo no chat antes da análise da IA
- Validação e complementação via Gemini: ajuste de pluviometria real por município, dimensionamento comercial de cisterna, estimativa de ROI

### 🏢 Avaliação Pós-Ocupação — APO (PI II)
- **Visão do Morador**: traduz relato leigo para categorias técnicas de desempenho (NBR 15575)
- **Visão do Especialista (Walkthrough)**: checklist técnico de vistoria in loco com recomendação de ensaios (termografia, percussão, medição de umidade)

### 📋 Regularização de Imóveis (PI III)
- Fluxo interativo com 3 cenários: Imóvel Existente, Aprovação de Projeto e Consulta Livre
- Checklist de documentação com `☐` e indicação de onde obter cada documento
- Follow-up técnico para dúvidas específicas após o checklist
- Base legal: Lei 13.465/2017 (Reurb-S/E), Lei 6.766/79, Código de Obras municipal

---

## 🏛️ Arquitetura (Clean Architecture + DDD)

O projeto segue separação estrita de responsabilidades em 3 camadas:

```text
patologias_bot/
├── main.py                        # Entrypoint minimalista (load_dotenv + bootstrap)
├── Dockerfile                     # Imagem Python 3.11-slim para Azure
├── deploy_azure.ps1               # Script PowerShell de CI/CD para Azure Container Instances
├── requirements.txt
│
├── tests/                         # Suite de 37 testes com pytest
│   ├── test_prompts.py            # Valida keywords e placeholders de todos os prompts
│   ├── test_models.py             # Testes de domínio: States, Enums, dataclasses
│   └── test_message_formatter.py  # Testa split_long_message e _polish_ai_text
│
└── src/
    ├── config.py                  # Settings via pydantic/dotenv, setup_logging
    │
    ├── domain/                    # Regras de negócio puras (sem dependências externas)
    │   ├── models.py              # Dataclasses tipadas: RegularizacaoState, ApoState, ReusoState
    │   └── prompts/               # Constantes de Prompt separadas por módulo
    │       ├── patologia.py
    │       ├── regularizacao.py
    │       ├── apo.py
    │       └── reuso.py
    │
    ├── services/                  # Casos de uso — orquestração IA
    │   └── ai_service.py          # GeminiService: wrapper único e injetável via bot_data
    │
    └── infrastructure/            # Adaptadores externos (Telegram API)
        └── telegram/
            ├── bot.py             # ApplicationBuilder, registro de handlers
            ├── keyboards.py       # ReplyKeyboardMarkup e InlineKeyboardMarkup centralizados
            ├── formatters.py      # Pós-processamento de texto: _polish_ai_text, send_ai_response
            ├── error_handler.py   # Captura global de exceções com log de traceback
            └── conversations/     # ConversationHandlers isolados por módulo
                ├── patologia.py
                ├── regularizacao.py
                ├── apo.py
                └── reuso.py
```

---

## 🎨 Pipeline de Formatação de Texto (UI do Chat)

O módulo `formatters.py` implementa um pipeline de pós-processamento que transforma a saída bruta do Gemini em texto limpo e legível no Telegram:

| Problema | Transformação |
|---|---|
| `### 1. 🌧️ Seção` gerado pelo Gemini | → `*🌧️ Seção*` (negrito Telegram) |
| `**texto**` Markdown padrão | → `*texto*` (Markdown v1 Telegram) |
| `- item` / `* item` como bullet | → `• item` (bullet Unicode) |
| 3+ linhas em branco consecutivas | → Máximo 2 linhas |
| Parse Mode falha (caracteres especiais) | → Fallback automático para texto plano |
| Resposta longa excedendo limite | → Divisão inteligente por parágrafo com separador `〰〰〰〰〰〰〰〰〰〰` |

---

## 🛠️ Tecnologias

| Tecnologia | Uso |
|---|---|
| Python 3.11+ | Linguagem principal |
| `python-telegram-bot` v22+ | Framework do bot |
| `google-genai` (Gemini Flash) | Motor de IA |
| `Pillow` | Processamento de imagens para análise de patologias |
| `python-dotenv` | Gerenciamento de variáveis de ambiente |
| `pytest` | Suite de testes automatizados (37 testes) |
| Docker + Azure Container Instances | Deploy em nuvem |

---

## 📦 Execução Local

### 1) Clonar o projeto
```bash
git clone <url-do-repositorio>
cd patologias_bot
```

### 2) Variáveis de Ambiente
Crie um arquivo `.env` na raiz:
```env
TELEGRAM_TOKEN=seu_token_aqui
GOOGLE_API_KEY=sua_chave_gemini_aqui
```

### 3) Instalar dependências e Executar
```bash
pip install -r requirements.txt
python main.py
```

---

## 🧪 Testes Automatizados

```bash
python -m pytest tests/ -v
```

A suite cobre:
- **37 testes** em 3 arquivos
- Integridade de todos os prompts (keywords, placeholders, regras de formatação)
- Modelos de domínio e estados de conversação
- Lógica de split e pós-processamento de texto

---

## ☁️ Deploy na Nuvem (Azure Container Apps)

Para bot de Telegram em polling, `Azure Container Apps` e uma opcao melhor que ACI:
- revisoes e rollout mais seguros
- controle de segredos e variaveis por app
- logs e operacao mais simples

O script `deploy_azure_containerapps.sh` automatiza o deploy:

1. Cria Resource Group e Azure Container Registry (ACR)
2. Faz build da imagem direto no ACR (`az acr build`)
3. Cria/atualiza Container Apps Environment
4. Cria/atualiza o app com secrets (`TELEGRAM_TOKEN`, `GOOGLE_API_KEY`)

**Pre-requisitos**: Azure CLI autenticado (`az login`) e permissao na assinatura.

```bash
# Na raiz do projeto
export TELEGRAM_TOKEN="SEU_TOKEN"
export GOOGLE_API_KEY="SUA_KEY"

# Opcional: customizar nomes
export RESOURCE_GROUP="rg-patologias-bot"
export LOCATION="brazilsouth"
export APP_NAME="patologias-bot"

# Deploy
./deploy_azure_containerapps.sh
```

Para ver logs em tempo real:

```bash
az containerapp logs show --name patologias-bot --resource-group rg-patologias-bot --follow
```

---

## ⚠️ Limitações e Responsabilidade Técnica

- A qualidade da foto e do relato textual influencia diretamente a precisão da IA.
- O bot **não substitui** vistoria in loco, ensaios laboratoriais e a responsabilidade técnica do profissional (ART/RRT).
- Deve ser utilizado estritamente como ferramenta acadêmica e de apoio à prática profissional.
