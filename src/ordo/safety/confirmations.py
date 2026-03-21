def confirm_action(message: str) -> bool:
    """
    Ask user confirmation before dangerous actions.
    """
    while True:
        ans = input(f"{message} (y/n): ").strip().lower()
        if ans == "y":
            return True
        elif ans == "n":
            return False
        else:
            print("Please enter 'y' or 'n'")
