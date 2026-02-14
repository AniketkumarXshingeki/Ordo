from models.llm import ask_llm
import json


SYSTEM_PROMPT = """
You are a file management AI.
you will receive commands from the user and must respond with a JSON object that describes the user's intent.
Return ONLY valid JSON.
No explanations.

Supported actions:
- search
- organize
- move
- rename
- delete
- create_folder

JSON format:
{
  "action": "...",
  "query": "...",
  "source": "...",
  "destination": "...",
  "new_name": "..."
}
"""


def parse_intent(user_input: str):
    prompt = SYSTEM_PROMPT + "\nUser: " + user_input

    response = ask_llm(prompt)

    print("\nRAW LLM RESPONSE:\n", response)   # ← ADD THIS

    try:
        data = json.loads(response)
        return data
    except Exception:
        return {"action": "unknown"}