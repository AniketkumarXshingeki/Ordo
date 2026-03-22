import ollama
import json

MODEL = "phi"

def ask_llm(prompt: str) -> str:
    """
    Send prompt to Ollama natively via its local API, with safety checks!
    """
    try:
        # Try to ping the local Ollama server
        response = ollama.generate(
            model=MODEL, 
            prompt=prompt,
            format="json", 
            stream=False
        )
        return response['response'].strip()
        
    except ollama.ResponseError as e:
        # This triggers if Ollama is running, but you haven't downloaded 'phi' yet
        print(f"\n Ollama Error: {e.error}")
        print(f"👉 Fix it by running this in a new terminal: ollama pull {MODEL}\n")
        return '{"action": "unknown"}'
        
    except Exception:
        # This triggers if the Ollama app is completely closed/turned off
        print("\n🛑 Connection Error: Could not reach the AI Engine.")
        print("👉 Please make sure the Ollama app is open and running in the background!\n")
        
        # Return a fake JSON string so your parse_intent function doesn't crash
        return '{"action": "unknown"}'