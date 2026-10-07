"""
Standalone test — run this directly to check if your API key/setup works,
with no Flask involved. This isolates the problem.
 
Run:  python test_api.py
"""
import os
from dotenv import load_dotenv
 
load_dotenv()
 
key = os.environ.get("GEMINI_API_KEY", "")
print(f"Key loaded from .env: {'YES' if key else 'NO'}")
print(f"Key starts with: {key[:8]}..." if key else "No key found at all.")
 
from google import genai
 
client = genai.Client()
 
try:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="Say hello in one short sentence.",
    )
    print("\nSUCCESS. Model replied:")
    print(response.text)
except Exception as e:
    print(f"\nFAILED — {type(e).__name__}")
    print(str(e))