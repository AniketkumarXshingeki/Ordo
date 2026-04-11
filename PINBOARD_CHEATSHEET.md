# ORDO Pinboard - Command Cheat Sheet

## 🎯 Most Used Commands

```bash
# Pin a file
ordo pin /path/to/file.txt

# View pinboard
ordo pinboard

# Unpin a file
ordo unpin /path/to/file.txt
```

---

## 📌 Pin Operations

```bash
# Basic pin
ordo pin /path/to/file

# Pin to category
ordo pin /path/to/file --category "Work"
ordo pin /path/to/file -c "Work"

# Pin by name (natural language)
ordo pin-natural "my project file"

# Unpin
ordo unpin /path/to/file
```

---

## 🎨 View Pinboard

```bash
# List view (default)
ordo pinboard

# Grid view (like desktop)
ordo pinboard --view grid

# Category view
ordo pinboard --view category

# With statistics
ordo pinboard --stats
ordo pinboard --view list --stats
```

---

## 🏷️ Categories

```bash
# View all categories
ordo pinboard-categories

# Add category
ordo add-category "Projects"

# Add with color
ordo add-category "Important" --color "#ff0000"

# Move file to category
ordo move-to-category /path/to/file "Projects"
```

---

## 📊 Stats & Suggestions

```bash
# View statistics
ordo pinboard-stats

# Get AI suggestions
ordo pinboard-suggest
```

---

## 🎓 Common Workflows

### Daily Work
```bash
ordo pin ~/inbox.txt --category "Work"
ordo pin ~/tasks.md --category "Work"
ordo pinboard --view category
```

### Project Management
```bash
ordo add-category "Project-X"
ordo pin ~/project/file1.txt -c "Project-X"
ordo pin ~/project/file2.txt -c "Project-X"
ordo pinboard --view category
```

### Quick Access
```bash
# Just view pinboard
ordo pinboard

# Grid for visual scanning
ordo pinboard --view grid
```

---

## 🔍 Examples

```bash
# Create categories
ordo add-category "Work" --color "#e74c3c"
ordo add-category "Study" --color "#2ecc71"

# Pin files
ordo pin ~/document.pdf -c "Work"
ordo pin ~/notes.txt -c "Study"

# View results
ordo pinboard --view category

# Get insights
ordo pinboard-stats

# Smart suggestions
ordo pinboard-suggest
```

---

## ⚡ Quick Tips

| Task | Command |
|------|---------|
| Pin file | `ordo pin <path>` |
| Unpin file | `ordo unpin <path>` |
| View all | `ordo pinboard` |
| View grid | `ordo pinboard --view grid` |
| View by category | `ordo pinboard --view category` |
| Create category | `ordo add-category <name>` |
| List categories | `ordo pinboard-categories` |
| Show stats | `ordo pinboard-stats` |
| Get suggestions | `ordo pinboard-suggest` |
| Pin by name | `ordo pin-natural "<query>"` |

---

## 🚨 Troubleshooting

| Problem | Solution |
|---------|----------|
| File won't pin | Scan directory first: `ordo scan /path` |
| Category missing | Create it: `ordo add-category <name>` |
| Pinboard empty | Pin some files: `ordo pin <path>` |
| Slow view | Use filtered: `ordo pinboard --view category` |

---

## 🎯 Keyboard Shortcuts (Coming Soon)

Save this file for quick reference!

---

*Pinboard Feature Quick Reference*
*Last Updated: April 10, 2026*
