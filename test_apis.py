import os
import sys
from dotenv import load_dotenv
from google import genai
from tavily import TavilyClient

# Ensure UTF-8 output on Windows consoles to prevent charmap encoding errors
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

print("=" * 60)
print("ResearchMate - API Connection Test")
print("=" * 60)

if not gemini_key or not tavily_key:
    print("[ERROR] API keys missing in .env file.")
    print("Please check GEMINI_API_KEY and TAVILY_API_KEY in .env.")
    sys.exit(1)

print("[INFO] API keys loaded successfully from .env!")

# Test Gemini
print("\n[1/2] Testing Gemini API...")
gemini_success = False

# We prioritize gemini-3.5-flash-lite for immediate and responsive execution
models_to_test = [
    "gemini-3.5-flash-lite",
    "gemini-2.5-flash-lite"
]

try:
    gemini_client = genai.Client(api_key=gemini_key)
    for model in models_to_test:
        try:
            print(f"Connecting with {model}...")
            response = gemini_client.interactions.create(
                model=model,
                input="Reply with: ResearchMate Gemini connection successful."
            )
            print(f"[SUCCESS] Gemini connected successfully using {model}!")
            output_text = getattr(response, "output_text", str(response))
            print(f"Response: {output_text.strip()}")
            gemini_success = True
            break
        except Exception as e:
            print(f"[WARNING] Model {model} failed: {e}")

    if not gemini_success:
        print("[ERROR] Gemini connection failed for tested models.")
except Exception as e:
    print(f"[ERROR] Gemini client initialization failed: {e}")

# Test Tavily
print("\n[2/2] Testing Tavily Search API...")
try:
    tavily_client = TavilyClient(api_key=tavily_key)
    results = tavily_client.search(
        query="Artificial Intelligence breakthroughs",
        max_results=2
    )

    items = results.get("results", [])
    if items:
        for idx, item in enumerate(items, start=1):
            print(f"\nResult #{idx}:")
            print(f"  Title: {item.get('title', 'N/A')}")
            print(f"  URL:   {item.get('url', 'N/A')}")
        print("\n[SUCCESS] Tavily connected successfully!")
    else:
        print("[WARNING] Tavily returned 0 results.")

except Exception as e:
    print(f"[ERROR] Tavily error: {e}")

print("\n" + "=" * 60)
print("API Testing Completed!")
print("=" * 60)
