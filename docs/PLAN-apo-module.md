# Módulo de Avaliação Pós-Ocupação (APO)

Implementação de um novo módulo de APO no bot Telegram, separando os dois eixos da metodologia:
**Visão do Usuário** (morador, linguagem leiga → análise perceptual) e **Visão do Especialista**
(engenheiro, walkthrough técnico → checklist normativo NBR 15575).

O fluxo segue o mesmo padrão de máquina de estados (`user_data`) já estabelecido no módulo de
Regularização, garantindo consistência arquitetural.

---

## Proposed Changes

### Camada de IA

#### [MODIFY] [ai_service.py](file:///c:/Users/aeric/OneDrive/Documentos/Projetos/patologias_bot/src/ai_service.py)

Adicionar duas novas funções assíncronas ao final do arquivo:

- **`gerar_apo_usuario(relato_morador)`** — recebe texto livre do morador e retorna relatório
  estruturado de percepção (conforto térmico/acústico/lumínico, funcionalidade, alertas de
  manutenção, índice de satisfação, foco para o walkthrough).
- **`gerar_apo_especialista(dados_inspecao)`** — recebe observação técnica do engenheiro em
  campo e retorna checklist normativo (requisito NBR 15575, VUP/Garantia, ensaios recomendados,
  cruzamento de dados, dica de laudo).

Os prompts já foram validados pelo usuário e constam no pedido original.

---

### Camada de Interface (Telegram)

#### [MODIFY] [handlers.py](file:///c:/Users/aeric/OneDrive/Documentos/Projetos/patologias_bot/src/handlers.py)

**1. Imports** — adicionar `gerar_apo_usuario` e `gerar_apo_especialista` ao bloco de importação de
`src.ai_service`.

**2. `main_menu_markup()`** — inserir nova linha com o botão
`"🏢 Avaliação Pós-Ocupação (APO)"` entre os botões existentes.

**3. Nova função `apo_submenu()`** — retorna `InlineKeyboardMarkup` com duas opções:
- `"🗣️ Relato do Morador (Usuário)"` → `callback_data="apo_usuario"`
- `"👷 Observação Técnica (Especialista)"` → `callback_data="apo_especialista"`

**4. `handle_callback()`** — adicionar tratamento para:
| `callback_data` | Ação |
|---|---|
| `apo_usuario` | Salva `apo_state = {tipo: 'usuario', etapa: 'aguardando_relato'}` e pede o relato do morador |
| `apo_especialista` | Salva `apo_state = {tipo: 'especialista', etapa: 'aguardando_observacao'}` e pede a observação de campo |
| `apo_menu` | Limpa `apo_state`, volta ao menu principal |

**5. `handle_message()`** — adicionar bloco *antes* dos tratamentos existentes para capturar
os estados `apo_state`:
- `etapa == 'aguardando_relato'` → chama `gerar_apo_usuario(text)`, exibe resultado e oferece
  botão "🏠 Menu principal" (`callback_data="apo_menu"`).
- `etapa == 'aguardando_observacao'` → chama `gerar_apo_especialista(text)`, exibe resultado
  e oferece botão "🏠 Menu principal".

**6. Texto do `/start`** — atualizar a mensagem de boas-vindas para mencionar a nova funcionalidade APO.

---

## Verification Plan

> Não há testes automatizados no projeto. A verificação é feita manualmente.

### Manual — Fluxo do Morador (Usuário)
1. Inicie o bot localmente: `python main.py`
2. Abra o Telegram e envie `/start`.
3. Toque em **🏢 Avaliação Pós-Ocupação (APO)**.
4. Toque em **🗣️ Relato do Morador (Usuário)**.
5. Envie um texto leigo, exemplo:
   > *"O quarto é muito quente no verão, a janela pega sol o dia todo. O banheiro tem um barulho de cano toda vez que o vizinho usa a água. A tomada da cozinha ficou mal posicionada, atrás do fogão."*
6. **Resultado esperado:** relatório estruturado com os 5 tópicos (🌡️ Conforto, 🛋️ Funcionalidade, ⚠️ Alertas, 📊 Índice, 🔍 Foco) sem erros de parsing Markdown.

### Manual — Fluxo do Especialista
1. No menu principal, toque em **🏢 Avaliação Pós-Ocupação (APO)**.
2. Toque em **👷 Observação Técnica (Especialista)**.
3. Envie observação técnica, exemplo:
   > *"Constatei manchas de umidade ascendente na parede da sala, aproximadamente 40 cm de altura, em imóvel com 8 anos de uso. Piso cerâmico com som cavo em 3 pontos próximos à janela."*
4. **Resultado esperado:** checklist técnico com os 5 tópicos (📋 Requisito NBR, ⏳ VUP, 📏 Ensaios, ⚖️ Cruzamento, 💡 Dica) em linguagem normativa.

### Manual — Botão Voltar
1. Após obter qualquer resultado APO, toque em **🏠 Menu principal**.
2. **Resultado esperado:** estado `apo_state` limpo, menu principal exibido.

### Smoke test — Módulos existentes não afetados
1. Após a implementação, testar **📸 Analisar Patologia** e **📋 Checklist Regularização**
   para garantir que os fluxos existentes não foram quebrados.
