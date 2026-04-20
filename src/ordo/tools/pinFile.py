"""
Pin File Operations - Wrapper module for common pinboard operations
Provides simplified interface for pinning/unpinning files
"""

from pathlib import Path
from ordo.tools.pinboard import (
    pin_file, unpin_file, get_all_pinned_files,
    get_pinned_by_category, update_pin_category,
    record_pin_access, get_statistics, suggest_files_to_pin,
    natural_language_pin, init_pinboard_db, get_categories, add_category,
    interactive_pinboard, interactive_category_pinboard, open_file_default,
    gui_pinboard, gui_category_pinboard
)
from ordo.tools.pinboard_ui import (
    display_pinned_list, display_pinned_grid, display_by_category,
    display_statistics, display_suggestions, display_categories, display_detailed_view
)


def quick_pin(file_path: str) -> bool:
    """Quick pin a file."""
    return pin_file(file_path, category="General")


def quick_unpin(file_path: str) -> bool:
    """Quick unpin a file."""
    return unpin_file(file_path)


def view_all_pinned(view_type: str = "list", show_stats: bool = False) -> None:
    """
    View all pinned files.
    
    Args:
        view_type: 'list', 'grid', or 'category'
        show_stats: Include access statistics
    """
    pinned = get_all_pinned_files()
    
    if view_type == "list":
        print(display_pinned_list(pinned, show_stats=show_stats))
    elif view_type == "grid":
        print(display_pinned_grid(pinned))
    elif view_type == "category":
        files_by_cat = {}
        for file_info in pinned:
            cat = file_info.get('pin_category', 'General')
            if cat not in files_by_cat:
                files_by_cat[cat] = []
            files_by_cat[cat].append(file_info)
        
        categories = get_categories()
        print(display_by_category(files_by_cat, categories))
    else:
        print(display_pinned_list(pinned, show_stats=show_stats))


def view_pinned_stats() -> None:
    """View pinboard statistics."""
    stats = get_statistics()
    print(display_statistics(stats))


def view_suggestions() -> None:
    """View AI suggestions for files to pin."""
    suggestions = suggest_files_to_pin(limit=5)
    print(display_suggestions(suggestions))


def view_categories() -> None:
    """View all available categories."""
    categories = get_categories()
    print(display_categories(categories))


def open_interactive_pinboard() -> None:
    """Open GUI pinboard to select and open files."""
    gui_pinboard()


def open_interactive_category(category: str) -> None:
    """Open GUI pinboard for a specific category."""
    gui_category_pinboard(category)
