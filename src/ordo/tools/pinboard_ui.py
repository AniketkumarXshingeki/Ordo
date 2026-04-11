"""
Pinboard UI Module for ORDO
Displays pinned files in various formats (list, grid, detailed view).
"""

from typing import List, Dict
from datetime import datetime
from pathlib import Path


def format_size(size_bytes: int) -> str:
    """Convert bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f}{unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f}TB"


def format_time(timestamp: float) -> str:
    """Convert timestamp to readable date."""
    if not timestamp:
        return "Never"
    dt = datetime.fromtimestamp(timestamp)
    return dt.strftime("%Y-%m-%d %H:%M")


def get_file_icon(file_type: str) -> str:
    """Get emoji icon based on file type."""
    icons = {
        'Documents': '📄',
        'Images': '🖼️',
        'Videos': '🎬',
        'Audio': '🎵',
        'Archives': '📦',
        'Code': '💻',
        'Spreadsheets': '📊',
        'Presentations': '📽️',
        'PDFs': '📕',
        'Text': '📝',
        'Folders': '📁',
    }
    return icons.get(file_type, '📄')


def display_pinned_list(pinned_files: List[Dict], show_stats: bool = False) -> str:
    """
    Display pinned files as a formatted list.
    
    Args:
        pinned_files: List of pinned file dictionaries
        show_stats: Include access statistics
    
    Returns:
        Formatted string for terminal display
    """
    if not pinned_files:
        return "📌 No pinned files yet. Start pinning files with: ordo pin <file_path>"

    output = "\n" + "=" * 100 + "\n"
    output += "📌 PINNED FILES (Quick Access)\n"
    output += "=" * 100 + "\n\n"

    for idx, file_info in enumerate(pinned_files, 1):
        icon = get_file_icon(file_info.get('file_type', 'Documents'))
        name = file_info['file_name']
        category = file_info.get('pin_category', 'General')
        path = file_info['file_path']
        last_accessed = format_time(file_info.get('last_accessed'))
        access_count = file_info.get('access_count', 0)

        output += f"{idx:2}. {icon} {name}\n"
        output += f"    📍 Path: {path}\n"
        output += f"    🏷️  Category: {category}\n"
        output += f"    ⏰ Last Accessed: {last_accessed}\n"

        if show_stats:
            output += f"    📊 Access Count: {access_count}\n"

        output += "\n"

    output += "=" * 100 + "\n"
    output += f"Total Pinned: {len(pinned_files)} files\n"
    output += "=" * 100 + "\n"

    return output


def display_pinned_grid(pinned_files: List[Dict], cols: int = 4) -> str:
    """
    Display pinned files in a grid layout (like desktop icons).
    
    Args:
        pinned_files: List of pinned file dictionaries
        cols: Number of columns in grid
    
    Returns:
        Formatted string for terminal display
    """
    if not pinned_files:
        return "📌 No pinned files yet."

    output = "\n" + "=" * 100 + "\n"
    output += "📌 PINNED FILES - GRID VIEW\n"
    output += "=" * 100 + "\n\n"

    for i in range(0, len(pinned_files), cols):
        batch = pinned_files[i:i + cols]
        
        # Icon row
        icon_row = "  "
        for file_info in batch:
            icon = get_file_icon(file_info.get('file_type', 'Documents'))
            icon_row += f"{icon:^20}"
        output += icon_row + "\n"

        # Name row
        name_row = "  "
        for file_info in batch:
            name = file_info['file_name'][:18]
            name_row += f"{name:^20}"
        output += name_row + "\n"

        # Category row
        cat_row = "  "
        for file_info in batch:
            cat = file_info.get('pin_category', 'General')[:15]
            cat_row += f"[{cat}]"[0:20].center(20)
        output += cat_row + "\n\n"

    output += "=" * 100 + "\n"
    return output


def display_by_category(files_by_category: Dict[str, List[Dict]], categories: List[Dict]) -> str:
    """
    Display pinned files grouped by category.
    
    Args:
        files_by_category: Dictionary with category as key and file list as value
        categories: List of category metadata including colors
    
    Returns:
        Formatted string for terminal display
    """
    if not files_by_category or all(len(files) == 0 for files in files_by_category.values()):
        return "📌 No pinned files yet."

    output = "\n" + "=" * 100 + "\n"
    output += "📌 PINNED FILES - BY CATEGORY\n"
    output += "=" * 100 + "\n\n"

    for cat in categories:
        cat_name = cat['name']
        files = files_by_category.get(cat_name, [])

        if not files:
            continue

        output += f"🏷️  {cat_name} ({len(files)} files)\n"
        output += "-" * 50 + "\n"

        for idx, file_info in enumerate(files, 1):
            icon = get_file_icon(file_info.get('file_type', 'Documents'))
            name = file_info['file_name']
            output += f"  {idx}. {icon} {name}\n"

        output += "\n"

    output += "=" * 100 + "\n"
    return output


def display_statistics(stats: Dict) -> str:
    """
    Display pinboard statistics and usage patterns.
    
    Args:
        stats: Dictionary with statistics
    
    Returns:
        Formatted string for terminal display
    """
    output = "\n" + "=" * 100 + "\n"
    output += "📊 PINBOARD STATISTICS\n"
    output += "=" * 100 + "\n\n"

    output += f"Total Pinned Files: {stats['total_pinned']}\n\n"

    output += "🏷️  By Category:\n"
    for cat, count in stats['by_category'].items():
        output += f"  • {cat}: {count}\n"

    output += "\n📈 Most Accessed:\n"
    if stats['most_accessed']:
        for idx, file_info in enumerate(stats['most_accessed'], 1):
            name = file_info['file_name']
            count = file_info['access_count']
            output += f"  {idx}. {name} ({count} accesses)\n"
    else:
        output += "  None yet\n"

    output += "\n" + "=" * 100 + "\n"
    return output


def display_suggestions(suggestions: List[Dict]) -> str:
    """
    Display AI-powered suggestions for files to pin.
    
    Args:
        suggestions: List of suggested file dictionaries
    
    Returns:
        Formatted string for terminal display
    """
    if not suggestions:
        return "✨ No suggestions available. Your frequently accessed files will appear here."

    output = "\n" + "=" * 100 + "\n"
    output += "✨ SUGGESTED FILES TO PIN (Based on Access Frequency)\n"
    output += "=" * 100 + "\n\n"

    for idx, file_info in enumerate(suggestions, 1):
        icon = get_file_icon(file_info.get('file_type', 'Documents'))
        name = file_info['name']
        path = file_info['path']
        freq = file_info.get('freq', 0)

        output += f"{idx}. {icon} {name}\n"
        output += f"   Path: {path}\n"
        output += f"   Frequency Score: {freq}\n"
        output += f"   Command: ordo pin '{path}'\n\n"

    output += "=" * 100 + "\n"
    return output


def display_categories(categories: List[Dict]) -> str:
    """
    Display available categories.
    
    Args:
        categories: List of category dictionaries
    
    Returns:
        Formatted string for terminal display
    """
    output = "\n" + "=" * 100 + "\n"
    output += "🏷️  AVAILABLE CATEGORIES\n"
    output += "=" * 100 + "\n\n"

    for cat in categories:
        name = cat['name']
        color = cat.get('color', '#3498db')
        output += f"  • {name:15} (Color: {color})\n"

    output += "\n" + "=" * 100 + "\n"
    output += "Add custom category: ordo add-category <name> [--color #HEXCODE]\n"
    output += "=" * 100 + "\n"

    return output


def display_detailed_view(pinned_file: Dict) -> str:
    """
    Display detailed information about a single pinned file.
    
    Args:
        pinned_file: Single pinned file dictionary
    
    Returns:
        Formatted string for terminal display
    """
    output = "\n" + "=" * 100 + "\n"
    output += "📄 PINNED FILE DETAILS\n"
    output += "=" * 100 + "\n\n"

    output += f"Name:          {pinned_file['file_name']}\n"
    output += f"Type:          {pinned_file.get('file_type', 'Unknown')}\n"
    output += f"Path:          {pinned_file['file_path']}\n"
    output += f"Category:      {pinned_file.get('pin_category', 'General')}\n"
    output += f"Pinned:        {format_time(pinned_file.get('pinned_at'))}\n"
    output += f"Last Accessed: {format_time(pinned_file.get('last_accessed'))}\n"
    output += f"Access Count:  {pinned_file.get('access_count', 0)}\n"

    output += "\n" + "=" * 100 + "\n"

    return output
