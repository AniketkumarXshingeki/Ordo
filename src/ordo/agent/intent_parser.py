from ordo.models.llm import ask_llm
import json

# Upgraded Prompt to handle Hybrid Search arguments
SYSTEM_PROMPT = """
You are an intelligent file management AI.
You will receive commands from the user and must respond with a JSON object that describes the user's intent.
Return ONLY valid JSON. No explanations. No extra text. Just the JSON.

Supported actions:
- search
- organize
- move
- rename
- delete
- create_folder

For "search" actions, use the following format:

JSON format:
{
  "action": "search",
  "query": "...",
  "category": "...", The type of file requested must be one of ("document", "image", "audio", "video", "presentation"). It strictly must be one of these values or Leave null if not mentioned or mentioned any other value.
}

For "move" actions, use the following format:

JSON format:
{
  "action": "move",
  "source": "...", (given source path)
  "destination": "...", (given destination path)
}

For "rename" actions, use the following format:

JSON format:
{
  "action": "rename",
  "source": "...", (given source path)
  "new_name": "...", (given new name)
}

For "delete" actions, use the following format:

JSON format:
{
  "action": "delete",
  "source": "..." (given source path)
}

For "create_folder" actions, use the following format:

JSON format:
{
  "action": "create_folder",
  "destination": "...", (given destination path)
}
For "organize" actions, use the following format:

JSON format:
{
  "action": "organize",
  "source": "...". (given source path)
  "destination": "...", (given destination path)
}
"""

def parse_intent(user_input: str):
    prompt = SYSTEM_PROMPT + "\nUser: " + user_input

    response = ask_llm(prompt)
    print("\n[DEBUG] RAW LLM RESPONSE:\n", response)

    try:
        data = json.loads(response)
        return data
    except Exception:
        return {"action": "unknown"}