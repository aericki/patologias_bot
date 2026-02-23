from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_markup() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [KeyboardButton("📸 Analisar Patologia"), KeyboardButton("📋 Checklist Regularização")],
            [KeyboardButton("🏢 Avaliação Pós-Ocupação (APO)")],
            [KeyboardButton("ℹ️ Sobre o Projeto")],
        ],
        resize_keyboard=True,
    )


def regularizacao_submenu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🏠 Regularizar imóvel existente", callback_data="reg_existente")],
            [InlineKeyboardButton("📐 Aprovar projeto novo", callback_data="reg_projeto_novo")],
            [InlineKeyboardButton("📄 Consulta livre", callback_data="reg_consulta_livre")],
        ]
    )


def apo_submenu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🗣️ Relato do Morador (Usuário)", callback_data="apo_usuario")],
            [InlineKeyboardButton("👷 Observação Técnica (Especialista)", callback_data="apo_especialista")],
        ]
    )


def tipo_imovel_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🏠 Casa", callback_data="tipo_casa"),
                InlineKeyboardButton("🏢 Apto", callback_data="tipo_apartamento"),
            ],
            [
                InlineKeyboardButton("🏪 Comércio", callback_data="tipo_comercio"),
                InlineKeyboardButton("🔀 Misto", callback_data="tipo_misto"),
            ],
        ]
    )


def escritura_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✅ Sim", callback_data="esc_sim"),
                InlineKeyboardButton("❌ Não", callback_data="esc_nao"),
                InlineKeyboardButton("📝 Só contrato", callback_data="esc_contrato"),
            ],
        ]
    )


def followup_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🔄 Detalhar um item", callback_data="followup_detalhar")],
            [InlineKeyboardButton("📍 Informar minha cidade", callback_data="followup_cidade")],
            [InlineKeyboardButton("🏠 Menu principal", callback_data="followup_menu")],
        ]
    )


def apo_post_menu(callback_repeat: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🏠 Menu principal", callback_data="apo_menu")],
            [InlineKeyboardButton("🔁 Nova análise APO", callback_data=callback_repeat)],
        ]
    )
