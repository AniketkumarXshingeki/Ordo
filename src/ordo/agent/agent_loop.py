from ordo.agent.intent_parser import parse_intent
from ordo.tools.hybrid_search import hybrid_search
from ordo.tools.file_tools import move_file, rename_file, delete_file, create_folder
from ordo.tools.organize_tools import organize_by_type
from ordo.agent.planner import validate_intent, resolve_move_intent


def handle_action(intent):
    valid, error = validate_intent(intent)

    if not valid:
        print("Invalid command:", error)
        return

    action = intent.get("action")

    # ---------------- SEARCH ----------------
    if action == "search":
        query = intent.get("query")
        results = hybrid_search(query)

        if not results:
            print("No matching files found.")
            return

        print("\nTop matches:\n")
        for score, name, path in results:
            print(f"{name} | {score:.3f}")
            print(path)
            print("-" * 40)

    # ---------------- MOVE (SMART) ----------------
    elif action == "move":
        src = intent.get("source")
        dest = intent.get("destination")

        # If source missing → resolve using reasoning
        if not src:
            src, dest = resolve_move_intent(intent)

            if not src:
                print("Could not confidently identify file to move.")
                return

        move_file(src, dest)

    # ---------------- OTHER ACTIONS ----------------
    elif action == "organize":
        organize_by_type("E:/Projects/Ordo/Workspace")

    elif action == "rename":
        rename_file(intent.get("source"), intent.get("new_name"))

    elif action == "delete":
        delete_file(intent.get("source"))

    elif action == "create_folder":
        create_folder(intent.get("destination"))

    else:
        print("Unknown command.")
def run_agent():
    print("\nAI File Manager Ready (type 'exit' to quit)\n")

    while True:
        user_input = input(">> ")

        if user_input.lower() in ["exit", "quit"]:
            break

        intent = parse_intent(user_input)
        print("Intent:", intent)

        handle_action(intent)


if __name__ == "__main__":
    run_agent()