import google.generativeai as genai
from django.conf import settings

# Configure the Gemini API
genai.configure(api_key=settings.GEMINI_API_KEY)

def get_ai_response(prompt):
    """
    Send a text prompt to Google Gemini and return the model's response.
    """
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")  # Fast, free, text model
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Error: {e}"
