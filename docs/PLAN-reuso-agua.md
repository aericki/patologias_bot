# Plano de Implementação: Módulo de Reuso de Água Pluvial (PI I)

## 1. Visão Geral
Adicionar um novo módulo ao bot para calcular a viabilidade de sistemas de aproveitamento de água pluvial, baseado na ABNT NBR 15527. Este módulo representará o Projeto Integrador I (Sustentabilidade/Hidráulica).

## 2. Arquitetura (Clean Architecture)

A inserção da nova feature seguirá a mesma separação de responsabilidades dos módulos existentes (Patologia, APO e Regularização):

### Camada de Domínio (`src/domain/`)
- `models.py`: Criar a dataclass `ReusoState` para armazenar de forma tipada os dados fornecidos pelo usuário durante a interação (ex: área de telhado, número de moradores, cidade para índice pluviométrico).
- `prompts/reuso.py`: Criar a constante `PROMPT_REUSO_AGUA` com as diretrizes do Engenheiro Sanitarista, incluindo a regra de ser **extremamente conciso** para o Telegram.

### Camada de Serviço (`src/services/`)
- `ai_service.py`: Adicionar o método `gerar_relatorio_reuso_agua(dados_projeto: str) -> str` na classe `GeminiService`.

### Camada de Infraestrutura (`src/infrastructure/telegram/`)
- `keyboards.py`: Atualizar `main_menu_markup()` para incluir o botão `🌱 Edifício Sustentável (Reuso)`. Pode-se criar também um menu de follow-up específico do reuso.
- `conversations/reuso.py`: Criar um novo `ConversationHandler` (`create_handler()`) com estados para:
  - Entrada no menu de sustentabilidade.
  - Coleta dos dados (área e moradores).
  - Chamada à IA e resposta.
- `bot.py`: Registrar o novo handler do reuso na `create_application()`. Atualizar as mensagens `_start` e `_about` para incluir menção ao PI I.

### Camada de Testes (`tests/`)
- Adicionar validações em `test_prompts.py` para garantir que a NBR 15527 e as restrições de formatação do Telegram estão no prompt.

## 3. Fluxo da Conversa no Telegram
1. Usuário clica em `🌱 Edifício Sustentável (Reuso)`
2. Bot solicita: "Por favor, digite a Área de Cobertura (telhado) e o Número de Moradores. Ex: 80m², 3 pessoas."
3. (Opcional) Bot pode perguntar a cidade para estimar a pluviometria.
4. Usuário envia os dados.
5. Bot envia a resposta gerada pelo Gemini formatada em tópicos curtos.
6. Bot oferece botão para "Calcular Outro" ou "Menu Principal".

## 4. Ordem de Execução (Fases)
- **Fase 1**: Atualização do Domínio (Prompts e Models) + Testes.
- **Fase 2**: Atualização do Serviço (GeminiService).
- **Fase 3**: Criação do handler na Infraestrutura e injeção no bot.py.
