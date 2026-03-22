from typing import Optional

import typer

from ordo.indexer import content_pipeline

# This creates your main CLI app
app = typer.Typer(help="🤖 Ordo: AI-Driven File Manager", add_completion=False)

@app.command()
def scan(path: Optional[str] = typer.Argument(".", help="Specific Folder to Scan"), 
         deep: bool = typer.Option(False, "--deep", help="Enable deep metadata scanning")):
    """
    Scan a directory to map out your files.
    """
    print(f"🔍 Ordo is booting up... scanning '{path}'")
    if deep:
        print("   -> 🕵️‍♂️ Deep scan activated!")
    
    # Next step: we will call your indexer here!
    # indexer.run_scan(path)
    content_pipeline.scan_with_path(path)

@app.command()
def organize(folder: str = typer.Argument(..., help="The target folder to clean up")):
    """
    Use AI to sort files into categorized folders.
    """
    print(f"📂 Preparing to organize files in '{folder}'...")

def main():
    # This is what Poetry triggers when you type 'ordo'
    app()

if __name__ == "__main__":
    main()