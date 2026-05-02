
### Basic Commands

```bash
# Initialize and scan your files
ordo scan /path/to/your/files

# Search for files by time
ordo search --year 2024
ordo search --month 3 --year 2024
ordo search --day 15 --month 3 --year 2024
ordo search --start-date 2024-01-01 --end-date 2024-12-31

# Organize files automatically
ordo organize /path/to/messy/folder

# Start interactive AI assistant
ordo run
```

### Pinboard Quick Access

```bash
# Pin important files
ordo pin "/path/to/important/file.txt" --category "Work"
ordo pin "/path/to/project.xlsx" -c "Projects"

# View your pinboard
ordo pinboard
ordo pinboard --view grid
ordo pinboard --view category

# Get AI suggestions
ordo pinboard-suggest

# Pin using natural language
ordo pin-natural "my budget spreadsheet"
```

### File Operations

```bash
# Create folders
ordo create "new/project/folder"

# Move files
ordo move "source.txt" "destination.txt"

# Rename files
ordo rename "oldname.txt" "newname.txt"

# Delete files (with confirmation)
ordo delete "unwanted.txt"
```

## 🏗️ Architecture

```
ordo/
├── agent/           # AI agent and natural language processing
│   ├── agent_loop.py    # Main agent interaction loop
│   ├── intent_parser.py # Command understanding
│   └── planner.py       # Task planning and execution
├── indexer/         # File indexing and search
│   ├── content_pipeline.py  # File scanning pipeline
│   └── vector_index.py      # FAISS vector indexing
├── memory/          # Context and conversation memory
├── models/          # Data models and schemas
├── safety/          # Security and validation
├── tools/           # Core functionality modules
│   ├── pinboard.py      # Pinboard implementation
│   ├── file_tools.py    # File operations
│   ├── organize_tools.py # AI organization
│   └── time_search.py   # Time-based search
└── utils/           # Utility functions
```

### Database Schema

**Main Files Index:**
- File metadata, content embeddings, timestamps
- Optimized for fast search and filtering

**Pinboard Tables:**
- `pinboard` - Pinned files with categories and access stats
- `pin_categories` - Custom categories with colors

## 📋 Command Reference

### Core Commands
- `scan [path]` - Index files in directory
- `search [options]` - Time-based file search
- `organize [folder]` - AI-powered file organization
- `run` - Start interactive AI assistant

### Pinboard Commands
- `pin <file> [--category NAME]` - Pin a file
- `unpin <file>` - Remove from pinboard
- `pinboard [--view TYPE]` - View pinned files
- `pinboard-suggest` - Get pinning suggestions
- `pinboard-categories` - List categories
- `add-category <name> [--color]` - Create category
- `pin-natural <query>` - Natural language pinning
- `open-pinboard` - Open GUI pinboard
- `open-category <name>` - Open category GUI

### File Operations
- `create <folder>` - Create new folder
- `move <source> <dest>` - Move file
- `rename <file> <newname>` - Rename file
- `delete <file>` - Delete file

## 🤖 AI Features

### Intelligent Organization
Ordo uses AI to automatically categorize and organize your files:
- Documents, Images, Videos, Audio, Archives
- Custom organization rules
- Learning from your preferences

### Smart Search
- Semantic search understands intent
- Fuzzy matching for typos
- Content-based ranking

### Natural Language Interface
```bash
# Interactive mode examples
"find my tax documents from last year"
"organize my downloads folder"
"show me files I accessed this week"
"pin all my project files"
```

## 🛡️ Safety & Security

- **Offline-first** - No data sent to external servers
- **Local AI models** - Uses Ollama for local inference
- **Safe file operations** - Confirmation prompts for destructive actions
- **Permission-aware** - Respects file system permissions

## 📈 Performance

- **Fast indexing** - Optimized scanning pipeline
- **Instant search** - Pre-computed vector embeddings
- **Efficient storage** - Compressed indexes and metadata
- **Low memory footprint** - Streaming processing for large directories




