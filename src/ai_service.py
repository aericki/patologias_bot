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
            "Atue como Engenheiro Civil especialista em patologias.\n"
            "Analise a imagem e classifique: FISSURA (<0.5mm), TRINCA (0.5-1.5mm), RACHADURA (>1.5mm) ou INFILTRAÇÃO (umidade/mofo).\n"
            "Considere NBR 9575, 15575, 13752.\n\n"
            "Responda concisamente:\n"
            "**Diagnóstico:** [Classificação]\n"
            "**Causa Provável:** [2-3 causas]\n"
            "**Reparo:** [Ação corretiva resumida]\n"
            "**NBR:** [Norma aplicável]\n\n"
            "Nota: Análise preliminar via IA."
        )
        
        response = await model.generate_content_async([prompt, img])
        return response.text
        
    except Exception as e:
        return f"Erro na análise da IA: {str(e)}"
