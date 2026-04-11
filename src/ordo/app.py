from pathlib import Path
from typing import Optional

import typer

from ordo.agent.agent_loop import run_agent
from ordo.indexer import content_pipeline
from ordo.indexer import vector_index
from ordo.tools.time_search import *
from ordo.tools.organize_tools import organize_by_type
from ordo.tools.pinboard import init_pinboard_db
from ordo.tools import pinFile

LAST_SCAN_PATH_FILE = Path("data") / "last_scan_path.txt"


def save_last_scan_path(path: str) -> None:
    Path("data").mkdir(exist_ok=True)
    try:
        LAST_SCAN_PATH_FILE.write_text(str(Path(path).resolve()), encoding="utf-8")
    except Exception as e:
        print(f"⚠️ Could not save scan path: {e}")


def get_last_scan_path() -> Optional[str]:
    if not LAST_SCAN_PATH_FILE.exists():
        return None
    try:
        path = LAST_SCAN_PATH_FILE.read_text(encoding="utf-8").strip()
        return path if path else None
    except Exception as e:
        print(f"⚠️ Could not read saved scan path: {e}")
        return None
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
        save_last_scan_path(path)
    # else:
    #     print("🌍 No path provided. Scanning all ALLOWED_ROOTS...")
    #     content_pipeline.run()
    if deep:
        vector_index.run_deep_scan()
    
@app.command()
def organize(folder: Optional[str] = typer.Argument(None, help="The target folder to clean up. If omitted, uses the last scanned path.")):
    """
    Use AI to sort files into categorized folders.
    If no path is provided, organizes the most recently scanned directory.
    """
    if folder is None:
        folder = get_last_scan_path()
        if not folder:
            typer.echo("❌ No scanned path available. Run `ordo scan <path>` first or provide a folder.")
            raise typer.Exit(code=1)
        typer.echo(f"📂 No folder provided; using last scanned path: {folder}")

    if not Path(folder).exists():
        typer.echo(f"❌ Target folder does not exist: {folder}")
        raise typer.Exit(code=1)

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


# ============================================================
# PINBOARD (Quick Access) COMMANDS
# ============================================================

@app.command()
def pin(file_path: str = typer.Argument(..., help="Path or filename of the file to pin"),
        category: str = typer.Option("General", "--category", "-c", help="Category for the pinned file")):
    """
    Pin a file for quick access. Pinned files appear in the pinboard for faster access.
    """
    # Initialize pinboard database on first use
    init_pinboard_db()
    
    from ordo.tools.pinboard import pin_file
    pin_file(file_path, category)


@app.command()
def unpin(file_path: str = typer.Argument(..., help="Path or filename of the file to unpin")):
    """
    Unpin a file from quick access.
    """
    from ordo.tools.pinboard import unpin_file
    unpin_file(file_path)

# @app.command()
# def pinboard_stats():
#     """
#     Display pinboard statistics: total files pinned, by category, most accessed, etc.
#     """
#     init_pinboard_db()
#     pinFile.view_pinned_stats()


@app.command()
def pinboard_suggest():
    """
    Get AI-powered suggestions for files that should be pinned based on access frequency.
    """
    init_pinboard_db()
    pinFile.view_suggestions()


@app.command()
def pinboard_categories():
    """
    View all available pin categories.
    """
    init_pinboard_db()
    pinFile.view_categories()


@app.command()
def add_category(name: str = typer.Argument(..., help="Category name"),
                color: str = typer.Option("#3498db", "--color", help="Hex color code for the category")):
    """
    Create a new category for organizing pinned files.
    
    Examples:
      ordo add-category "Projects"
      ordo add-category "Work" --color "#ff0000"
    """
    init_pinboard_db()
    from ordo.tools.pinboard import add_category as add_cat
    add_cat(name, color)


@app.command()
def move_to_category(file_path: str = typer.Argument(..., help="Path to the pinned file"),
                    category: str = typer.Argument(..., help="Target category")):
    """
    Move a pinned file to a different category.
    
    Example:
      ordo move-to-category "/path/file.txt" "Work"
    """
    init_pinboard_db()
    from ordo.tools.pinboard import update_pin_category
    update_pin_category(file_path, category)


@app.command()
def pin_natural(query: str = typer.Argument(..., help="Natural language query")):
    """
    Pin a file using natural language instead of exact path.
    
    Examples:
      ordo pin-natural "my project file"
      ordo pin-natural "project"
      ordo pin-natural "budget spreadsheet"
    """
    init_pinboard_db()
    from ordo.tools.pinboard import natural_language_pin
    natural_language_pin(query)


@app.command()
def open_pinboard():
    """
    Open interactive pinboard menu.
    Browse and select pinned files to open with one click.
    
    Just enter the number of the file you want to open!
    """
    init_pinboard_db()
    pinFile.open_interactive_pinboard()


@app.command()
def open_category(category: str = typer.Argument(..., help="Category name")):
    """
    Open interactive pinboard for a specific category.
    See all files in that category and select one to open.
    
    Example:
      ordo open-category "Work"
      ordo open-category "Study"
    """
    init_pinboard_db()
    pinFile.open_interactive_category(category)


def main():
    # This is what Poetry triggers when you type 'ordo'
    app()

if __name__ == "__main__":
    main()