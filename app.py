
def show_help():
    print("""
Available Commands:
-------------------------------------------------
help                     → Show all commands
ls                       → List files in current directory
ls a                    → List all files including hidden ones
ls l                    → List files with details (size, date)          
create <filename>        → Create a new file
rename <old> <new>       → Rename a file
delete <filename>        → Delete a file
move <file> <new_path>   → Move file to new location
search <filename>        → Search file in current directory
exit                     → Exit the program
-------------------------------------------------
""")

print("\033[1;32m")
print("""
 ██████  ██████  ██████   ██████ 
██    ██ ██   ██ ██   ██ ██    ██
██    ██ ██████  ██   ██ ██    ██
██    ██ ██   ██ ██   ██ ██    ██
 ██████  ██   ██ ██████   ██████ 
""")
print("\033[0m")
print("Welcome to ORDO CLI - Your Advance AI based File Management Tool!\n")
print("Type 'help' to see available commands.\n")

while True:
    command = input("ORDO> ").strip().split()

    if not command:
        continue

    if command[0] == "help":
        show_help()
    elif command[0] == "ls":
        print("Listing files in current directory...")

    elif command[0] == "ls" and len(command) == 2 and command[1] == "a":
        print("Listing all files including hidden ones...")
    elif command[0] == "ls" and len(command) == 2 and command[1] == "l":
        print("Listing files with details (size, date)...")

    elif command[0] == "create" and len(command) == 2:
        print("file is created successfully."+command[1])

    elif command[0] == "rename" and len(command) == 3:
       print("file is renamed successfully.")

    elif command[0] == "delete" and len(command) == 2:
        print("file is deleted successfully.")

    elif command[0] == "move" and len(command) == 3:
        print("file is moved successfully.")

    elif command[0] == "search" and len(command) == 2:
        print("file is found successfully.")

    elif command[0] == "exit":
        print("👋 Exiting ORDO CLI. Goodbye!")
        break

    else:
        print("⚠️ Invalid command. Type 'help' for available commands.")