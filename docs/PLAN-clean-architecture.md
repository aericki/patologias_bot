# PLAN — Refatoração Arquitetural (Clean Architecture)

> **Objetivo:** Refatorar o bot de ~530 linhas em 2 arquivos para uma arquitetura limpa,
> testável e preparada para expansão multi-plataforma (web/mobile).
> **Restrição:** Apenas refatoração estrutural. Nenhuma funcionalidade nova.

---

## Diagnóstico Atual (Code Smells)

| Problema | Arquivo | Impacto |
|---|---|---|
| God Object — `handlers.py` faz roteamento, estado, formatação e envio | `handlers.py` (500+ linhas) | Manutenção impossível |
| Prompts hardcoded misturados com lógica de IA | `ai_service.py` | Não reutilizável |
| `configure_genai()` chamado em TODA função | `ai_service.py` | Redundância, sem DI |
| Estado via `user_data` dict sem tipagem nem validação | `handlers.py` | Bugs silenciosos |
| Sem `ConversationHandler` — máquina de estados manual | `handlers.py` | Reinventa a roda da lib |
| Zero testes | projeto | Sem rede de segurança |
| Zero logging estruturado nos handlers | `handlers.py` | Debugging cego |
| Sem camada de domínio — lógica acoplada ao Telegram | tudo | Impossibilita multi-plataforma |

---

## Arquitetura Alvo (Clean Architecture)

```
patologias_bot/
├── main.py                          # Entry point (bootstrap)
├── requirements.txt
├── Dockerfile
├── .env.example
├── tests/                           # NOVO — Testes
│   ├── __init__.py
│   ├── test_prompts.py
│   ├── test_conversation_states.py
│   └── test_message_formatter.py
│
└── src/
    ├── __init__.py
    │
    ├── config.py                    # NOVO — Settings centralizados (env vars)
    │
    ├── domain/                      # NOVO — Camada de Domínio (pura, sem deps)
    │   ├── __init__.py
    │   ├── prompts/                 # Prompts como dados estruturados
    │   │   ├── __init__.py
    │   │   ├── patologia.py         # PROMPT_PATOLOGIA
    │   │   ├── regularizacao.py     # PROMPT_REGULARIZACAO, PROMPT_APROVACAO, PROMPT_FOLLOWUP
    │   │   └── apo.py              # PROMPT_APO_USUARIO, PROMPT_APO_ESPECIALISTA
    │   └── models.py               # NOVO — Dataclasses de estado tipadas
    │
    ├── services/                    # NOVO — Camada de Serviço (use cases)
    │   ├── __init__.py
    │   └── ai_service.py           # Gemini client (inicializa UMA vez)
    │
    ├── infrastructure/              # NOVO — Camada de Infraestrutura
    │   ├── __init__.py
    │   └── telegram/               # Adaptador Telegram
    │       ├── __init__.py
    │       ├── bot.py              # Bootstrap do bot (handlers registration)
    │       ├── keyboards.py        # TODOS os teclados (menus, submenus)
    │       ├── formatters.py       # _split_long_message, _enviar_resposta_ia
    │       ├── conversations/      # ConversationHandlers separados por domínio
    │       │   ├── __init__.py
    │       │   ├── patologia.py    # ConversationHandler: análise de foto
    │       │   ├── regularizacao.py # ConversationHandler: fluxo regularização
    │       │   └── apo.py          # ConversationHandler: fluxo APO
    │       └── error_handler.py    # Error handler com notificação
    │
    └── utils.py                    # Utilitários puros (se necessário)
```

### Princípios Aplicados

| Princípio | Antes | Depois |
|---|---|---|
| **SRP** (Single Responsibility) | `handlers.py` faz tudo | Cada arquivo = 1 responsabilidade |
| **DIP** (Dependency Inversion) | `ai_service` acoplado ao Gemini | Interface de serviço desacoplada |
| **OCP** (Open-Closed) | Adicionar módulo = mexer em 2 files | Adicionar módulo = criar 1 conversation + 1 prompt |
| **Separação de Camadas** | Telegram + IA misturados | Domain → Service → Infrastructure |
| **ConversationHandler** | Máquina de estados manual via `user_data` | `ConversationHandler` nativo da lib |

---

## Fases de Implementação

### Fase 1 — Fundação (config + models + prompts)

> **Risco:** Nenhum. Arquivos novos, nada quebra.

| # | Tarefa | Arquivo | Descrição |
|---|---|---|---|
| 1.1 | Criar `src/config.py` | `src/config.py` | Centralizar `TELEGRAM_TOKEN`, `GOOGLE_API_KEY`, `LOG_LEVEL` com validação |
| 1.2 | Criar `src/domain/models.py` | `src/domain/models.py` | Dataclasses tipadas: `RegularizacaoState`, `ApoState` (substituem dicts) |
| 1.3 | Extrair prompts | `src/domain/prompts/*.py` | Mover strings de prompt para constantes nomeadas |
| 1.4 | Criar `tests/__init__.py` | `tests/` | Estrutura de testes com pytest |

**Critério de Aceite:** Arquivos criados, imports funcionam, `python -c "from src.domain.models import RegularizacaoState"` OK.

---

### Fase 2 — Serviço de IA (refatorar ai_service)

> **Risco:** Médio. Muda a interface da camada de IA.

| # | Tarefa | Arquivo | Descrição |
|---|---|---|---|
| 2.1 | Refatorar `ai_service.py` | `src/services/ai_service.py` | Classe `GeminiService` com `__init__` que faz `configure_genai()` UMA vez |
| 2.2 | Usar prompts da camada domain | `src/services/ai_service.py` | Importar prompts de `src.domain.prompts.*` |
| 2.3 | Testes unitários de prompts | `tests/test_prompts.py` | Verificar que prompts contêm keywords obrigatórias |

**Critério de Aceite:** `GeminiService` instanciável, métodos `analyze_image()`, `gerar_checklist_regularizacao()`, `gerar_apo_usuario()`, etc., todos delegam para `_call_gemini(prompt)` interno.

---

### Fase 3 — Infraestrutura Telegram (refatorar handlers)

> **Risco:** Alto. Reescreve o coração do bot. Testar cada fluxo.

| # | Tarefa | Arquivo | Descrição |
|---|---|---|---|
| 3.1 | Extrair teclados | `src/infrastructure/telegram/keyboards.py` | Mover `main_menu_markup()`, `apo_submenu()`, etc. |
| 3.2 | Extrair formatadores | `src/infrastructure/telegram/formatters.py` | Mover `_split_long_message()`, `_enviar_resposta_ia()` |
| 3.3 | Criar ConversationHandler: Patologia | `src/infrastructure/telegram/conversations/patologia.py` | Entry: foto recebida → análise → fim |
| 3.4 | Criar ConversationHandler: Regularização | `src/infrastructure/telegram/conversations/regularizacao.py` | Entry: botão → tipo → escritura → cidade → checklist → followup |
| 3.5 | Criar ConversationHandler: APO | `src/infrastructure/telegram/conversations/apo.py` | Entry: botão → tipo (usuario/especialista) → texto → resultado |
| 3.6 | Criar `bot.py` | `src/infrastructure/telegram/bot.py` | Registrar todos os ConversationHandlers + commands |
| 3.7 | Error handler melhorado | `src/infrastructure/telegram/error_handler.py` | Log estruturado + notificação ao dev (padrão da lib) |

**Critério de Aceite:** Todos os 3 fluxos (Patologia, Regularização, APO) funcionando no Telegram com ConversationHandler. Comando `/start` e menu principal intactos.

---

### Fase 4 — Bootstrap e Integração

> **Risco:** Baixo. Apenas liga as peças.

| # | Tarefa | Arquivo | Descrição |
|---|---|---|---|
| 4.1 | Refatorar `main.py` | `main.py` | Importar de `src.config` e `src.infrastructure.telegram.bot` |
| 4.2 | Atualizar `requirements.txt` | `requirements.txt` | Adicionar `pytest` |
| 4.3 | Atualizar `about_command` | conversation ou handler global | Mencionar a nova arquitetura/módulos |
| 4.4 | Deletar arquivos antigos | `src/handlers.py`, `src/ai_service.py` (antigos) | Remover após migração completa |

**Critério de Aceite:** `python main.py` sobe o bot. Todos os fluxos testados manualmente.

---

### Fase 5 — Testes e Qualidade

> **Risco:** Nenhum. Adiciona segurança.

| # | Tarefa | Arquivo | Descrição |
|---|---|---|---|
| 5.1 | Testes de prompts | `tests/test_prompts.py` | Verificar keywords, tamanho, estrutura |
| 5.2 | Testes de modelos | `tests/test_models.py` | Validação de estados, defaults, tipos |
| 5.3 | Testes de formatação | `tests/test_message_formatter.py` | `_split_long_message` com edge cases |
| 5.4 | Testes de conversação | `tests/test_conversation_states.py` | Transições de estado válidas |

**Critério de Aceite:** `pytest` passa com ≥80% coverage nos módulos `domain` e `formatters`.

---

## Ordem de Execução

```
Fase 1 (Fundação)  →  Fase 2 (Serviço IA)  →  Fase 3 (Telegram)  →  Fase 4 (Bootstrap)  →  Fase 5 (Testes)
     [Safe]              [Médio]                  [Alto]                [Baixo]                [Safe]
```

> ⚠️ **Regra Ágil:** Após cada Fase, o bot DEVE estar funcional.
> Se a Fase 3 quebrar algo, rollback para o estado pós-Fase 2.

---

## Benefícios Pós-Refatoração

| Cenário | Antes | Depois |
|---|---|---|
| Adicionar módulo novo | Mexer em `handlers.py` (500+ linhas) + `ai_service.py` | Criar 1 prompt + 1 ConversationHandler |
| Expandir para Web/Mobile | Reescrever tudo | Reusar `domain/` e `services/`, criar novo adaptador em `infrastructure/web/` |
| Testar lógica de IA | Impossível sem o bot rodando | Testar `GeminiService` isoladamente |
| Debug de estado | `print(user_data)` e rezar | `ConversationHandler` com logging nativo |
| Onboarding de dev | "Lê o handlers.py" | Cada arquivo autoexplicativo |

---

## Checklist de Verificação Final

- [ ] `python main.py` → bot sobe sem erros
- [ ] `/start` → menu com 3 botões (Patologia, Regularização, APO)
- [ ] 📸 Enviar foto → análise de patologia funciona
- [ ] 📋 Regularização → fluxo completo (tipo → escritura → cidade → checklist → followup)
- [ ] 🏢 APO Usuário → relato → relatório 5 tópicos
- [ ] 🏢 APO Especialista → observação → checklist NBR 15575
- [ ] `pytest` → todos os testes passam
- [ ] Nenhum `import` circular
- [ ] `handlers.py` e `ai_service.py` antigos deletados
