from typing import Optional

import typer

from ordo.agent.agent_loop import run_agent
from ordo.indexer import content_pipeline
from ordo.indexer import vector_index

# This creates your main CLI app
app = typer.Typer(help="🤖 Ordo: AI-Driven File Manager", add_completion=False)

@app.command()
def scan(path: Optional[str] = typer.Argument(".", help="Specific Folder to Scan"), 
         deep: bool = typer.Option(False, "--deep", help="Enable deep metadata scanning")):
    """
    Scan a directory to map out your files.
    """
    print(f"🔍 Ordo is booting up... scanning '{path}'")
    if path:
        print(f"🔍 Ordo is targeting specific path: '{path}'")
        content_pipeline.scan_with_path(path)
    # else:
    #     print("🌍 No path provided. Scanning all ALLOWED_ROOTS...")
    #     content_pipeline.run()
    if deep:
        vector_index.run_deep_scan()
    
@app.command()
def organize(folder: str = typer.Argument(..., help="The target folder to clean up")):
    """
    Use AI to sort files into categorized folders.
    """
    print(f"📂 Preparing to organize files in '{folder}'...")


@app.command()
def run():
    """
    Start the interactive AI File Manager terminal.
    """
    print("🤖 Booting up Ordo Agent Environment...")
    
    # This triggers your 'while True' loop from core.py!
    run_agent()

def main():
    # This is what Poetry triggers when you type 'ordo'
    app()

if __name__ == "__main__":
    main()