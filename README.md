# 🏗️ Assistente Técnico de Engenharia Civil no Telegram

> **Projeto Acadêmico (TCC + Projeto Integrador) – Engenharia Civil**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://core.telegram.org/bots)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini-orange.svg)](https://ai.google.dev/)
[![Clean Architecture](https://img.shields.io/badge/Architecture-Clean-success.svg)](#)
[![Pytest](https://img.shields.io/badge/Testing-Pytest-yellow.svg)](#)

## 📋 Visão Geral

Este projeto implementa um bot de Telegram que atua como **mentor técnico** para **engenheiros e arquitetos recém-formados**. Construído sob os princípios da **Clean Architecture**, o bot possui três módulos principais:

1. **📸 Patologias Construtivas (TCC)**: Apoio ao diagnóstico preliminar por análise de imagens (visão computacional via IA).
2. **🏢 Avaliação Pós-Ocupação (Projeto Integrador II)**: Análise de desempenho habitacional sob duas óticas: a percepção do morador e o checklist do especialista (Base: NBR 15575).
3. **📋 Regularização de Imóveis (Projeto Integrador III)**: Roteiro prático orientando a condução de processos burocráticos municipais.

O foco não é orientar leigos, mas atuar como um "colega sênior", fornecendo uma base técnica para a elaboração de laudos e condução de projetos do profissional júnior.

---

## 🚀 Funcionalidades

### Patologias
- ✅ Análise de fotos de vistoria via Telegram.
- ✅ Classificação preliminar (fissura, trinca, rachadura, infiltração) com referências normativas (NBR 9575, 13752).

### Regularização (Fluxo Interativo)
- ✅ Imóvel Existente, Projeto Novo ou Consulta Livre.
- ✅ Geração de checklist da documentação (Escritura, ART, Habite-se).
- ✅ Dúvidas em cascata (Ex: detalhar itens ou adaptar para a legislação de uma cidade específica).

### Avaliação Pós-Ocupação (APO)
- ✅ **Visão do Morador**: Análise do relato de conforto e funcionalidade.
- ✅ **Visão do Especialista (Walkthrough)**: Orientação técnica baseada nas anomalias identificadas in loco.

---

## 🏛️ Arquitetura e Estrutura (Clean Architecture)

O projeto foi refatorado para garantir testabilidade, escalabilidade e facilidade de manutenção, adotando Domain-Driven Design (DDD) e Clean Architecture:

```text
patologias_bot/
├── main.py                     # Entrypoint minimalista
├── deploy_azure.ps1            # Script de automação para deploy no Azure
├── requirements.txt            # Dependências incluindo Pytest
├── tests/                      # Suite de testes
│   ├── test_prompts.py         # Testes de integridade de IA
│   ├── test_models.py          # Testes de domínio/states
│   └── test_message_formatter.py
└── src/
    ├── config.py               # Centralização de variáveis de ambiente
    ├── domain/                 # Regras de Negócio e Prompts
    │   ├── models.py           # Dataclasses tipadas e Enums (State)
    │   └── prompts/            # Prompts do Gemini extraídos
    ├── services/               # Casos de Uso
    │   └── ai_service.py       # Wrapper do Gemini encapsulado
    └── infrastructure/         # Adaptadores Externos
        └── telegram/           
            ├── bot.py          # Setup da Application API 
            ├── keyboards.py    # Menus e botões inline
            ├── error_handler.py# Tratamento e log de exceções
            └── conversations/  # ConversationHandlers isolados
                ├── patologia.py
                ├── regularizacao.py
                └── apo.py
```

---

## 🛠️ Tecnologias

- **Linguagem**: Python 3.11+
- **Bot Framework**: `python-telegram-bot` (v20+)
- **Inteligência Artificial**: API do Google Gemini (`google-generativeai`)
- **Processamento de Imagem**: `Pillow`
- **Testes**: `pytest`
- **Deploy/Nuvem**: Azure Container Instances / Docker

---

## 📦 Execução Local

### 1) Clonar o projeto
```bash
git clone <url-do-repositorio>
cd patologias_bot
```

### 2) Variáveis de Ambiente
Crie um arquivo `.env` na raiz do projeto:
```env
TELEGRAM_TOKEN=seu_token_aqui
GOOGLE_API_KEY=sua_chave_gemini_aqui
```

### 3) Instalar dependências e Executar
Recomendado usar ambiente virtual (venv):
```bash
pip install -r requirements.txt
python main.py
```

---

## 🧪 Testes Automatizados

O sistema conta com testes automatizados utilizando `pytest` para garantir a integridade da arquitetura de estados e integridade estrutural dos prompts orientados a engenharia.

Para rodar os testes:
```bash
python -m pytest tests/ -v
```

---

## ☁️ Deploy na Nuvem (Azure)

O repositório possui um script automatizado (`deploy_azure.ps1`) otimizado para contas **Azure for Students**. Ele faz o build da imagem Docker localmente e sobe para o **Azure Container Instances (ACI)** com recursos limitados (0.5 CPU / 0.5 GB RAM) para economizar créditos.

**Requisitos**: Docker Desktop aberto e Azure CLI (`az`) logado.

1. Defina as credenciais diretamente no terminal:
```powershell
$env:TELEGRAM_TOKEN="SEU_TOKEN"
$env:GOOGLE_API_KEY="SUA_KEY"
```

2. Execute o script:
```powershell
.\deploy_azure.ps1
```

---

## ⚠️ Limitações e Responsabilidade Legal

- A qualidade da foto e do texto influencia fortemente o diagnóstico da IA.
- O bot **não substitui** vistoria in loco, ensaios laboratoriais e a Anotação de Responsabilidade Técnica (ART/RRT).
- Deve ser usado estritamente como ferramenta acadêmica e de apoio profissional.
