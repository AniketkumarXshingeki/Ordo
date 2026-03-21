from tools.hybrid_search import hybrid_search
from tools.time_search import filter_by_month, filter_by_year
from datetime import datetime


# ---------------------------
# Check intent validity
# ---------------------------
def validate_intent(intent):
    action = intent.get("action")

    if action == "search" and not intent.get("query"):
        return False, "Missing search query"

    if action == "move" and not (intent.get("source") and intent.get("destination")):
        return False, "Move requires source and destination"

    if action == "rename" and not (intent.get("source") and intent.get("new_name")):
        return False, "Rename requires source and new_name"

    if action == "delete" and not intent.get("source"):
        return False, "Delete requires source"

    return True, None


# ---------------------------
# Choose best file safely
# ---------------------------
def choose_best_result(results):
    if not results:
        return None

    score, name, path = results[0]

    # confidence threshold
    if score < 0.35:
        return None

    return path


# ---------------------------
# Multi-step reasoning for move
# ---------------------------
def resolve_move_intent(intent):
    """
    Handles vague commands like:
    'move my recent pdf'
    """
    query = intent.get("query")

    if not query:
        return None, None

    results = hybrid_search(query, top_k=5)

    best_file = choose_best_result(results)

    if not best_file:
        return None, None

    destination = intent.get("destination")
    return best_file, destination