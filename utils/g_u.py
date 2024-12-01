import google.generativeai as genai

def configure_genai(api_key):
    genai.configure(api_key=api_key)

def generate_supportive_response(user_entry):
    prompt = f"""
    You are an empathetic AI assistant. Read the following journal entry and provide a kind comment:
    "{user_entry}"
    """
    response = genai.generate_content(prompt)
    return response.text.strip() if response else "Keep up the great work!"
