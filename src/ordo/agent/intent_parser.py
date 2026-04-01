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

For "search" actions, extract these filters if the user mentions them:
-- category: The type of file requested must be one of ("document", "image", "audio", "video", "presentation", "code", "archive"). It strictly must be one of these values or Leave null if not mentioned or mentioned any other value.
- days_ago: An integer representing how far back to look (e.g., "yesterday" = 1, "last week" = 7, "last month" = 30). Leave null if not mentioned.

JSON format:
{
  "action": "...",
  "query": "...",
  "category": "...",
  "days_ago": "...",
  "source": "...",
  "destination": "...",
  "new_name": "..."
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