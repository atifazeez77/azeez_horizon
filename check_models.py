import google.generativeai as genai
import os
from dotenv import load_dotenv

# Load your hidden API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("Error: API Key not found. Check your .env file.")
else:
    genai.configure(api_key=api_key)
    print("Fetching available models...\n")
    
    # List all models that support generating content (chat)
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"- {m.name}")