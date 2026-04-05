import google.generativeai as genai
import toml

secrets = toml.load(r"C:\Users\shank\expense_tracker\.streamlit\secrets.toml")
api_key = secrets.get("default", {}).get("GOOGLE_API_KEY", secrets.get("GOOGLE_API_KEY"))
genai.configure(api_key=api_key)

print("Available models:")
for m in genai.list_models():
    if 'generateContent' in m.supported_generation_methods:
        print(m.name)
