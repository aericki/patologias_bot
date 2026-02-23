import os
import google.generativeai as genai
from PIL import Image

def configure_genai():
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError("GOOGLE_API_KEY não configurada.")
    genai.configure(api_key=api_key)

async def analyze_image(image_path):
    """
    Envia a imagem para o Google Gemini e retorna a análise da patologia.
    """
    try:
        configure_genai()
        model = genai.GenerativeModel('gemini-flash-latest')
        
        img = Image.open(image_path)
        
        prompt = (
            "Você é um Engenheiro Civil sênior com 20+ anos de experiência em "
            "patologias construtivas, atuando como MENTOR de um engenheiro/arquiteto "
            "recém-formado que está aprendendo a diagnosticar patologias em campo.\n\n"
            "CONTEXTO: O profissional que enviou esta foto está fazendo uma vistoria "
            "e precisa de orientação técnica para seu laudo/relatório.\n\n"
            "Analise a imagem e classifique: FISSURA (<0.5mm), TRINCA (0.5-1.5mm), "
            "RACHADURA (>1.5mm) ou INFILTRAÇÃO (umidade/mofo).\n"
            "Considere NBR 9575, 15575, 13752.\n\n"
            "Responda como um colega mais experiente orientando:\n"
            "**Diagnóstico:** [Classificação]\n"
            "**Causa Provável:** [2-3 causas técnicas]\n"
            "**Investigação Complementar:** [O que o profissional deve verificar "
            "in loco para confirmar — ex: mapeamento de fissuras, ensaio de "
            "percussão, teste de carbonatação, etc.]\n"
            "**Reparo Recomendado:** [Técnica de reparo e materiais]\n"
            "**NBR Aplicável:** [Normas de referência para o laudo]\n"
            "**Dica de Prática:** [Algo que só se aprende com experiência — "
            "ex: 'Sempre fotografe com escala métrica para o laudo']\n\n"
            "Use linguagem técnica entre profissionais — sem simplificar "
            "demais. O objetivo é ensinar e desenvolver o olhar clínico do colega."
        )
        
        response = await model.generate_content_async([prompt, img])
        return response.text
        
    except Exception as e:
        return f"Erro na análise da IA: {str(e)}"


# ── Regularização de imóveis ────────────────────────────────

async def gerar_checklist_regularizacao(descricao_usuario):
    """Gera checklist de regularização com base legal."""
    try:
        configure_genai()
        model = genai.GenerativeModel('gemini-flash-latest')

        prompt = (
            "Você é um Engenheiro Civil sênior com 20+ anos de experiência em "
            "regularização imobiliária e aprovação de projetos, atuando como "
            "MENTOR de um(a) engenheiro(a)/arquiteto(a) recém-formado(a).\n\n"
            "CONTEXTO: Seu colega júnior acabou de pegar um caso de cliente e "
            "precisa de orientação prática sobre como conduzir a regularização. "
            "Fale como um colega mais experiente ensinando — use linguagem "
            "técnica entre profissionais, sem simplificar como se fosse para leigo.\n\n"
            "BASE LEGAL (referencie quando aplicável):\n"
            "- Lei 13.465/2017 (Reurb): Regularização Fundiária Urbana\n"
            "  • Reurb-S (Interesse Social): população de baixa renda, gratuita\n"
            "  • Reurb-E (Interesse Específico): demais casos, onerosa\n"
            "  • CRF (Certidão de Regularização Fundiária): documento final\n"
            "  • Legitimação de posse e legitimação fundiária\n"
            "- Lei 6.766/79: Parcelamento do solo urbano\n"
            "- Art. 1.245 do Código Civil: transferência de propriedade via registro\n"
            "- Código de Obras municipal (varia por cidade)\n\n"
            f"CASO DO CLIENTE: '{descricao_usuario}'\n\n"
            "Gere um CHECKLIST DE REGULARIZAÇÃO orientando o profissional:\n"
            "1. **📊 Diagnóstico do Caso** — classifique a situação "
            "(irregular, clandestino, etc.) e explique por quê\n"
            "2. **📋 Documentação que Você Vai Precisar** — liste com ☐, "
            "explicando onde obter cada documento\n"
            "3. **🔢 Roteiro de Execução** — passo a passo de como conduzir "
            "o processo (o que protocolar, onde ir, com quem falar)\n"
            "4. **⏱ Prazos e Honorários** — tempo estimado e referência de "
            "valores para cobrar do cliente\n"
            "5. **⚖️ Base Legal** — leis aplicáveis para fundamentar seu trabalho\n"
            "6. **💡 Dica de Veterano** — algo que só se aprende com experiência "
            "(ex: armadilhas do processo, como antecipar exigências da prefeitura, "
            "como negociar com cartórios, etc.)\n\n"
            "IMPORTANTE: O usuário do bot É o engenheiro/arquiteto, não o "
            "cliente final. Nunca sugira 'contrate um engenheiro' — ele É "
            "o profissional. Oriente-o sobre como executar o serviço.\n\n"
            "Se faltar informação crítica do caso, faça UMA pergunta objetiva."
        )

        response = await model.generate_content_async(prompt)
        return response.text

    except Exception as e:
        return f"Erro na consulta de regularização: {str(e)}"


async def gerar_checklist_aprovacao_projeto(dados):
    """Gera checklist de aprovação de projeto novo na prefeitura."""
    try:
        configure_genai()
        model = genai.GenerativeModel('gemini-flash-latest')

        tipo = dados.get('tipo_imovel', 'Residência')
        escritura = dados.get('escritura', 'Não informado')
        cidade = dados.get('cidade', 'Não informada')

        prompt = (
            "Você é um Engenheiro Civil sênior com 20+ anos de experiência em "
            "aprovação de projetos em prefeituras, atuando como MENTOR de um(a) "
            "engenheiro(a)/arquiteto(a) recém-formado(a) que está conduzindo "
            "seu primeiro (ou dos primeiros) processos de aprovação.\n\n"
            "CONTEXTO: Seu colega júnior precisa aprovar um projeto na "
            "prefeitura e quer orientação prática de quem já fez isso muitas "
            "vezes. Fale como colega experiente — linguagem técnica entre "
            "profissionais, sem simplificar para leigo.\n\n"
            f"DADOS DO CASO DO CLIENTE:\n- Tipo: {tipo}\n- Escritura/matrícula: "
            f"{escritura}\n- Cidade/UF: {cidade}\n\n"
            "DOCUMENTAÇÃO BASE (maioria dos municípios exige):\n"
            "☐ Requerimento ao setor de aprovação de obras\n"
            "☐ Projeto arquitetônico completo (planta baixa, cortes, "
            "fachada, situação, locação) — mín. 2 vias\n"
            "☐ Memorial descritivo da obra\n"
            "☐ ART (CREA) ou RRT (CAU) — você emite a sua\n"
            "☐ Matrícula atualizada do terreno (máx. 30 dias)\n"
            "☐ Certidão negativa de débitos municipais (IPTU)\n"
            "☐ Cópia do documento do proprietário (RG/CPF)\n"
            "☐ Comprovante de endereço / croqui de localização\n"
            "☐ Taxa de análise de projeto (DAM/boleto)\n"
            "☐ Consulta prévia de viabilidade (quando exigida)\n\n"
            "Gere um CHECKLIST orientando o profissional:\n"
            "1. **📋 Documentos que Você Vai Precisar** — adapte a lista com ☐, "
            "indicando o que é responsabilidade sua vs. do cliente\n"
            "2. **🔢 Roteiro na Prefeitura** — passo a passo (onde ir, com "
            "quem falar, o que protocolar)\n"
            "3. **⏱ Prazos Estimados** — tempo médio e como acelerar\n"
            "4. **💰 Referência de Honorários e Taxas** — quanto cobrar do "
            "cliente (honorários técnicos) + taxas municipais\n"
            "5. **⚠️ Armadilhas do Processo** — erros comuns de iniciante e "
            "como evitar (ex: memorial incompleto, recuo errado, etc.)\n"
            "6. **⚖️ Base Legal** — Código de Obras, Lei de Uso e Ocupação, "
            "NBR 13.532\n"
            "7. **💡 Dica de Veterano** — insight prático de quem já aprovou "
            "muitos projetos (ex: 'sempre vá presencialmente na primeira vez', "
            "'peça o nome do analista', etc.)\n\n"
            "IMPORTANTE: O usuário do bot É o engenheiro/arquiteto responsável "
            "técnico, não o cliente final. Nunca sugira 'contrate um engenheiro' "
            "— ele É o profissional. Oriente-o a executar o serviço.\n\n"
            f"Se conhecer particularidades de {cidade}, cite-as. "
            "Caso contrário, alerte sobre consultar o Código de Obras local."
        )

        response = await model.generate_content_async(prompt)
        return response.text

    except Exception as e:
        return f"Erro na consulta de aprovação de projeto: {str(e)}"


async def gerar_followup_regularizacao(checklist_anterior, pergunta_usuario):
    """Responde follow-up com contexto do checklist anterior."""
    try:
        configure_genai()
        model = genai.GenerativeModel('gemini-flash-latest')

        prompt = (
            "Você é um Engenheiro Civil sênior mentorando um(a) colega "
            "recém-formado(a) sobre regularização imobiliária.\n\n"
            "CONTEXTO: Você já gerou o checklist abaixo para orientar o "
            "profissional, e agora ele tem uma dúvida de acompanhamento.\n\n"
            "Checklist gerado anteriormente:\n---\n"
            f"{checklist_anterior}\n---\n\n"
            f"Dúvida do profissional: '{pergunta_usuario}'\n\n"
            "Responda como colega experiente — linguagem técnica, prática "
            "e direta. Referencie legislação quando aplicável. Use ☐ se "
            "listar documentos/etapas. Lembre-se: quem pergunta É o "
            "engenheiro/arquiteto, não um cliente leigo."
        )

        response = await model.generate_content_async(prompt)
        return response.text

    except Exception as e:
        return f"Erro na consulta de follow-up: {str(e)}"


# ── Avaliação Pós-Ocupação (APO) ────────────────────────────

async def gerar_apo_usuario(relato_morador):
    """
    Processa o relato do morador (linguagem leiga) e estrutura em um
    relatório técnico de percepção do usuário (APO).
    """
    try:
        configure_genai()
        model = genai.GenerativeModel('gemini-flash-latest')

        prompt = (
            "Você é um pesquisador especialista em Avaliação Pós-Ocupação (APO) "
            "e Desempenho de Edificações.\n\n"
            "CONTEXTO: Estamos realizando uma APO em uma residência. O morador "
            "forneceu um relato sobre sua experiência morando no local, abordando "
            "suas percepções de conforto, funcionalidade e problemas do dia a dia. "
            "Sua tarefa é traduzir esse relato leigo para categorias técnicas de desempenho.\n\n"
            f"RELATO DO MORADOR: '{relato_morador}'\n\n"
            "Gere um RELATÓRIO DE PERCEPÇÃO DO USUÁRIO estruturado da seguinte forma:\n"
            "1. **🌡️ Conforto Ambiental** — Classifique os relatos em: Térmico, Acústico ou Lumínico.\n"
            "2. **🛋️ Funcionalidade e Uso** — Como o espaço atende às necessidades (layout, tomadas, circulação).\n"
            "3. **⚠️ Alertas de Manutenção** — Problemas relatados que indicam falhas construtivas.\n"
            "4. **📊 Índice de Satisfação Sugerido** — Avalie o tom do relato (Positivo, Neutro ou Negativo).\n"
            "5. **🔍 Foco para a Inspeção** — O que o engenheiro deve procurar durante a vistoria física "
            "(Walkthrough) com base nestas reclamações.\n\n"
            "Responda de forma técnica, objetiva e estruturada, utilizando marcadores."
        )

        response = await model.generate_content_async(prompt)
        return response.text

    except Exception as e:
        return f"Erro na análise de APO (Usuário): {str(e)}"


async def gerar_apo_especialista(dados_inspecao):
    """
    Gera o checklist e avaliação de desempenho (NBR 15575) com base
    na observação técnica do engenheiro durante o walkthrough.
    """
    try:
        configure_genai()
        model = genai.GenerativeModel('gemini-flash-latest')

        prompt = (
            "Você é um Engenheiro Civil Sênior, especialista em Desempenho de "
            "Edificações (NBR 15575) e Avaliação Pós-Ocupação (APO).\n\n"
            "CONTEXTO: Um engenheiro júnior está em campo realizando o 'Walkthrough' "
            "(vistoria especialista) de uma APO. Ele encontrou uma situação específica "
            "e precisa da sua orientação sobre como avaliar o desempenho desse sistema.\n\n"
            f"OBSERVAÇÃO DE CAMPO: '{dados_inspecao}'\n\n"
            "Gere um CHECKLIST TÉCNICO DE APO para orientar o profissional:\n"
            "1. **📋 Requisito de Desempenho** — Qual sistema está falhando e qual o "
            "critério da NBR 15575 que rege isso (ex: Estanqueidade, Durabilidade, etc.).\n"
            "2. **⏳ Vida Útil de Projeto (VUP) e Garantia** — Indique se, pelo tempo "
            "de uso relatado, a falha configura perda prematura de vida útil ou falta "
            "de manutenção do usuário.\n"
            "3. **📏 Ensaios e Medições Recomendadas** — Quais ferramentas ou testes o "
            "engenheiro deve aplicar in loco para validar a falha (ex: termografia, "
            "teste de percussão, medição de umidade).\n"
            "4. **⚖️ Cruzamento de Dados** — Como cruzar essa falha técnica com a possível "
            "reclamação do morador.\n"
            "5. **💡 Dica de Especialista** — Algo prático sobre a elaboração do laudo final.\n\n"
            "Fale de engenheiro para engenheiro. Linguagem técnica e normativa."
        )

        response = await model.generate_content_async(prompt)
        return response.text

    except Exception as e:
        return f"Erro na análise de APO (Especialista): {str(e)}"
