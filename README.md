# 🏗️ Bot de Identificação de Patologias Estruturais

> **Projeto de TCC - Engenharia Civil - UNISA**  
> USO DE I.A NA IDENTIFICAÇÃO DE FISSURAS E INFILTRAÇÕES EM EDIFICAÇÕES
> [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
> [![Telegram Bot](https://img.shields.io/badge/Telegram-Bot-blue.svg)](https://core.telegram.org/bots)
> [![Google Gemini](https://img.shields.io/badge/Google-Gemini%201.5-orange.svg)](https://ai.google.dev/)

## 📋 Sobre o Projeto

Este projeto foi desenvolvido como parte do Trabalho de Conclusão de Curso (TCC) em Engenharia Civil, com o objetivo de **avaliar o potencial de algoritmos de Inteligência Artificial e Visão Computacional na detecção automática de patologias estruturais** em edificações residenciais.

O sistema consiste em um **chatbot no Telegram** que utiliza modelos de linguagem multimodais (LLM com visão) para analisar imagens de estruturas e identificar:

- 🔍 **Fissuras** (térmicas, por recalque, retração)
- 💧 **Infiltrações** (ascendente, por chuva, vazamentos)
- 🧱 **Trincas e rachaduras**
- 🌊 **Problemas de umidade**

### 🎯 Objetivos

**Geral:**

- Avaliar o potencial de algoritmos de IA na detecção automática de fissuras e infiltrações em estruturas residenciais.

**Específicos:**

- Desenvolver uma ferramenta acessível para análise preliminar de patologias
- Testar a precisão de modelos de IA generativa em diagnósticos estruturais
- Comparar diagnósticos automatizados com análises técnicas tradicionais
- Fornecer laudos estruturados com base em normas técnicas brasileiras (NBR)

---

## 🚀 Funcionalidades

- ✅ Análise de imagens via Telegram
- ✅ Identificação automática de patologias estruturais
- ✅ Diagnóstico com base em IA (Google Gemini 1.5 Flash)
- ✅ **Guia de Regularização de Imóveis** com submenu interativo:
  - 🏠 Regularizar imóvel existente (coleta guiada de dados)
  - 📐 Aprovar projeto novo na prefeitura (checklist de documentos)
  - 📄 Consulta livre (texto aberto)
- ✅ Base legal embutida: Lei 13.465/2017 (Reurb), Lei 6.766/79, Código de Obras
- ✅ Conversa multi-turno: detalhar itens e refinar por cidade
- ✅ Laudo estruturado contendo:
  - **Diagnóstico:** Tipo de patologia identificada
  - **Causa Provável:** Origem do problema
  - **Reparo Sugerido:** Recomendações técnicas
  - **Normas Técnicas:** NBR 9575, NBR 15575, NBR 13752
- ✅ Interface simples e intuitiva via Telegram

---

## 🛠️ Tecnologias Utilizadas

- **Python 3.8+** - Linguagem de programação
- **python-telegram-bot** - Framework para bots do Telegram
- **Google Generative AI (Gemini 1.5 Flash)** - Modelo de IA multimodal
- **Pillow** - Processamento de imagens
- **python-dotenv** - Gerenciamento de variáveis de ambiente

---

## 📦 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- Conta no Telegram
- Chave de API do Google Gemini
- Token de Bot do Telegram

### Passo a Passo

1. **Clone o repositório:**

```bash
git clone <url-do-repositorio>
cd botEng
```

2. **Crie um ambiente virtual (recomendado):**

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

3. **Instale as dependências:**

```bash
pip install -r requirements.txt
```

4. **Configure as variáveis de ambiente:**

Copie o arquivo `.env.example` para `.env`:

```bash
cp .env.example .env
```

Edite o arquivo `.env` e adicione suas credenciais:

```env
TELEGRAM_TOKEN=seu_token_do_telegram_aqui
GOOGLE_API_KEY=sua_chave_api_google_aqui
```

**Como obter as credenciais:**

- **Telegram Token:** Fale com [@BotFather](https://t.me/botfather) no Telegram
- **Google API Key:** Acesse [Google AI Studio](https://aistudio.google.com/app/apikey)

5. **Execute o bot:**

```bash
python main.py
```

---

## 💬 Como Usar

1. **Inicie uma conversa** com o bot no Telegram
2. **Envie o comando** `/start` para ver as instruções
3. Escolha no menu entre **📸 Analisar Patologia** e **📋 Checklist Regularização**
4. Para patologia, **envie uma foto** da manifestação (fissura, infiltração, etc.)
5. Para regularização, selecione o cenário (imóvel existente, projeto novo ou consulta livre)
6. Responda as perguntas guiadas (tipo de imóvel, escritura, cidade)
7. Receba o checklist personalizado e use os botões de follow-up

### Comandos Disponíveis

- `/start` - Inicia o bot e exibe mensagem de boas-vindas
- `/ajuda` - Mostra instruções de uso
- `/regularizar` - Acesso direto ao Guia de Regularização

---

## 📁 Estrutura do Projeto

```
botEng/
├── main.py                 # Arquivo principal do bot
├── requirements.txt        # Dependências do projeto
├── .env.example           # Exemplo de variáveis de ambiente
├── .gitignore             # Arquivos ignorados pelo Git
├── src/
│   ├── __init__.py        # Inicialização do módulo
│   ├── handlers.py        # Handlers de comandos e mensagens
│   ├── ai_service.py      # Integração com Google Gemini
│   └── utils.py           # Funções utilitárias
└── README.md              # Este arquivo
```

---

## 🔬 Metodologia (TCC)

### Tipo de Pesquisa

- **Classificação:** Pesquisa Aplicada, Exploratória
- **Abordagem:** Estudo de Caso com Validação Tecnológica

### Ferramenta Utilizada

- **Modelo:** Google Gemini 1.5 Flash (LLM Multimodal)
- **Justificativa:** Acessibilidade, rapidez de processamento e capacidade de interpretar contexto além da simples detecção de pixels

### Coleta de Dados

- **Local:** Residências unifamiliares e edificações diversas
- **Procedimento:** Captura de imagens com smartphone focando em patologias visíveis

---

## 📊 Resultados Esperados

O sistema fornece laudos preliminares que podem auxiliar engenheiros e técnicos em:

- ✅ **Triagem inicial** de patologias
- ✅ **Padronização** de diagnósticos preliminares
- ✅ **Agilidade** na análise (segundos vs. horas)
- ✅ **Acesso rápido** a normas técnicas aplicáveis

### ⚠️ Limitações

- Dependência da qualidade da foto (iluminação, foco, ângulo)
- Possibilidade de falsos positivos (confundir sujeira ou sombra com fissura)
- **A IA não substitui a visita in loco** e testes físicos (percussão, medição de umidade)
- Ferramenta deve ser usada como **auxiliar ao engenheiro**, não como substituta

---

## 📚 Normas Técnicas Referenciadas

- **NBR 9575** - Impermeabilização - Seleção e projeto
- **NBR 15575** - Edificações habitacionais - Desempenho
- **NBR 13752** - Perícias de engenharia na construção civil

---

## 🚀 Deploy

Para instruções detalhadas sobre como fazer deploy do bot em produção, consulte o arquivo `DEPLOY.md`.

---

## 🤝 Contribuições

Este é um projeto acadêmico desenvolvido para TCC. Sugestões e melhorias são bem-vindas!

---

## 📝 Licença

Este projeto foi desenvolvido para fins acadêmicos como parte do TCC em Engenharia Civil.

---

## 👨‍💻 Autor

Desenvolvido como Trabalho de Conclusão de Curso (TCC) em Engenharia Civil.

---

## 🔮 Trabalhos Futuros

- Treinar uma rede neural específica com dataset brasileiro de patologias
- Implementar detecção de múltiplas patologias em uma única imagem
- Adicionar suporte para análise de vídeos
- Integração com drones para inspeção de fachadas
- Sistema de geração automática de relatórios técnicos em PDF

---

**⚡ Construção 4.0 - Modernizando a Engenharia Civil com Inteligência Artificial**
