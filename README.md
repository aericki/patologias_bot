# 🏗️ Assistente de Engenharia Civil no Telegram

> **Projeto acadêmico (TCC + Projeto Integrador) – Engenharia Civil**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://core.telegram.org/bots)
[![Google Gemini](https://img.shields.io/badge/Google-Gemini-orange.svg)](https://ai.google.dev/)

## 📋 Visão Geral

Este projeto implementa um bot de Telegram que atua como **mentor técnico** para **engenheiros e arquitetos recém-formados**, com dois módulos principais:

- **📸 Patologias construtivas**: apoio ao diagnóstico preliminar por imagem
- **📋 Regularização e aprovação de projetos**: roteiro prático para condução de processos em prefeitura

O foco não é orientar leigos, e sim apoiar o profissional no início da prática, com linguagem técnica e direcionamento de execução.

---

## 🎯 Público-Alvo

- Engenheiros civis recém-formados
- Arquitetos recém-formados
- Profissionais iniciando atuação em regularização, aprovação e diagnóstico preliminar

---

## 🚀 Funcionalidades

- ✅ Análise de imagens de patologias via Telegram
- ✅ Classificação preliminar com base técnica (fissura, trinca, rachadura, infiltração)
- ✅ Respostas com referência normativa (NBR)
- ✅ Guia de regularização com fluxo interativo:
  - 🏠 Regularizar imóvel existente
  - 📐 Aprovar projeto novo
  - 📄 Consulta livre
- ✅ Follow-up técnico:
  - Detalhamento de itens
  - Refinamento por cidade/UF
- ✅ Orientação de estilo “colega sênior mentorando profissional júnior”
- ✅ Envio de respostas longas em partes (evita erro de limite do Telegram)

---

## 🧠 Base Técnica e Legal

### Patologias

- NBR 9575
- NBR 15575
- NBR 13752

### Regularização e aprovação

- Lei 13.465/2017 (Reurb)
- Lei 6.766/79 (Parcelamento do Solo)
- Art. 1.245 do Código Civil
- Código de Obras municipal (conforme cidade)

---

## 🛠️ Tecnologias

- Python 3.8+
- python-telegram-bot
- Google Generative AI (Gemini)
- Pillow
- python-dotenv

---

## 📦 Instalação

### Pré-requisitos

- Python 3.8+
- Token de bot do Telegram
- API key do Google AI Studio

### 1) Clonar o projeto

```bash
git clone <url-do-repositorio>
cd patologias_bot
```

### 2) Criar e ativar ambiente virtual

```bash
python -m venv .venv

# Linux/Mac
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3) Instalar dependências

```bash
pip install -r requirements.txt
```

### 4) Configurar variáveis de ambiente

```bash
cp .env.example .env
```

No `.env`:

```env
TELEGRAM_TOKEN=seu_token
GOOGLE_API_KEY=sua_chave
```

### 5) Executar

```bash
python main.py
```

---

## 💬 Uso no Telegram

1. Envie `/start`
2. Escolha:
   - `📸 Analisar Patologia`
   - `📋 Checklist Regularização`
3. Siga o fluxo guiado
4. Use os botões de follow-up para aprofundar

### Comandos

- `/start` – inicia o bot
- `/ajuda` – dicas para fotos de vistoria
- `/regularizar` – atalho para o fluxo regulatório

---

## 📁 Estrutura do Projeto

```text
patologias_bot/
├── main.py
├── requirements.txt
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── list_models.py
├── src/
│   ├── __init__.py
│   ├── ai_service.py
│   ├── handlers.py
│   └── utils.py
└── README.md
```

---

## ⚠️ Limitações

- A qualidade da foto influencia fortemente o diagnóstico
- Pode haver falso positivo/negativo em análise preliminar por IA
- Não substitui vistoria in loco, ensaios e responsabilidade técnica
- Deve ser usado como ferramenta de apoio profissional

---

## 🔭 Próximos Passos

- Aprimorar prompts com legislação municipal por base de conhecimento
- Geração de relatórios técnicos (PDF) para apoio ao laudo
- Métricas de qualidade de resposta por tipo de caso
- Ampliação de fluxos para acompanhamento de protocolo em prefeitura

---

## 🤝 Contribuições

Projeto acadêmico em evolução. Sugestões e melhorias são bem-vindas.
