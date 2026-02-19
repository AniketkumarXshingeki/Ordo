from agent.intent_parser import parse_intent
from tools.hybrid_search import hybrid_search
from tools.file_tools import move_file, rename_file, delete_file, create_folder
from tools.organize_tools import organize_by_type


def handle_action(intent):
    action = intent.get("action")

    if action == "search":
        query = intent.get("query", "")
        results = hybrid_search(query)

        print("\nTop matches:\n")
        for score, name, path in results:
            print(f"{name} | {score:.3f}")
            print(path)
            print("-" * 40)

    elif action == "organize":
        target = "E:/Projects/Ordo/Workspace"
        organize_by_type(target)

    elif action == "move":
        move_file(intent.get("source"), intent.get("destination"))

    elif action == "rename":
        rename_file(intent.get("source"), intent.get("new_name"))

    elif action == "delete":
        delete_file(intent.get("source"))

    elif action == "create_folder":
        create_folder(intent.get("destination"))

    else:
        print("Could not understand command.")


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