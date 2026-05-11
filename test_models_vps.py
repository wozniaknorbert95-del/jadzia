import google.generativeai as genai
import os

genai.configure(api_key="AIzaSyAmwwPucLKx8jS6JG3PacT8rIMsJNB3zlQ")

models_to_test = [
    "models/gemini-1.5-flash",
    "models/gemini-flash-latest",
    "models/gemini-1.5-pro",
    "models/gemini-pro-latest",
    "models/gemini-2.0-flash"
]

print("Testing models for generateContent...")
for model_name in models_to_test:
    print(f"Testing {model_name}...", end=" ", flush=True)
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Hi, reply with 'OK'")
        print(f"SUCCESS: {response.text.strip()}")
        # If we found one, we can stop or list all
    except Exception as e:
        print(f"FAILED: {e}")
