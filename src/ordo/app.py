from typing import Optional

import typer

from ordo.agent.agent_loop import run_agent
from ordo.indexer import content_pipeline
from ordo.indexer import vector_index
from ordo.tools.time_search import *
from ordo.tools.organize_tools import organize_by_type
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
    organize_by_type(folder)

# Add this new command for time-based searching
@app.command()
def search(
    day: Optional[int] = typer.Option(None, help="Day of the month (1-31)"),
    month: Optional[int] = typer.Option(None, help="Month (1-12)"),
    year: Optional[int] = typer.Option(None, help="Year (e.g., 2024)"),  # Now optional
    start_date: Optional[str] = typer.Option(None, help="Start date for range search (YYYY-MM-DD)"),
    end_date: Optional[str] = typer.Option(None, help="End date for range search (YYYY-MM-DD)"),
):
    """
    Search for files by creation time: day, month, year, or date range.
    Provide either specific day/month/year or a start/end date range.
    """
    if start_date and end_date:
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            end_dt = datetime.strptime(end_date, "%Y-%m-%d")
            if start_dt > end_dt:
                typer.echo("❌ Start date must be before or equal to end date.")
                return
            results = filter_by_range(start_date, end_date)
        except ValueError:
            typer.echo("❌ Invalid date format. Use YYYY-MM-DD.")
            return
    elif day and month and year:
        # Day search
        results = filter_by_day(day, month, year)
    elif month and year:
        # Month search
        results = filter_by_month(month, year)
    elif year:
        # Year search
        results = filter_by_year(year)
    else:
        typer.echo("❌ Please provide valid search criteria: --year, --month --year, --day --month --year, or --start-date --end-date.")
        return

    if not results:
        typer.echo("🔍 No files found for the given criteria.")
        return

    typer.echo(f"🔍 Found {len(results)} file(s):")
    for name, path, dt in results:
        typer.echo(f"  - {name} | {path} | Created: {dt.strftime('%Y-%m-%d %H:%M:%S')}")
# Add this import at the top with other imports
from ordo.tools.file_tools import create_folder, move_file, rename_file, delete_file

# Add these new commands to your app

@app.command()
def create(folder: str = typer.Argument(..., help="Path for the new folder")):
    """
    Create a new folder with all parent directories.
    """
    if create_folder(folder):
        typer.echo(f"✅ Folder created: {folder}")
    else:
        typer.echo(f"❌ Failed to create folder")

@app.command()
def move(
    source: str = typer.Argument(..., help="Source file path"),
    destination: str = typer.Argument(..., help="Destination file path")
):
    """
    Move a file from source to destination.
    """
    if move_file(source, destination):
        typer.echo(f"✅ File moved successfully")
    else:
        typer.echo(f"❌ Failed to move file")

@app.command()
def rename(
    filepath: str = typer.Argument(..., help="File path to rename"),
    new_name: str = typer.Argument(..., help="New filename")
):
    """
    Rename a file.
    """
    if rename_file(filepath, new_name):
        typer.echo(f"✅ File renamed successfully")
    else:
        typer.echo(f"❌ Failed to rename file")

@app.command()
def delete(
    filepath: str = typer.Argument(..., help="File path to delete"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation")
):
    """
    Delete a file (requires confirmation).
    """
    if delete_file(filepath):
        typer.echo(f"✅ File deleted successfully")
    else:
        typer.echo(f"❌ Failed to delete file")
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