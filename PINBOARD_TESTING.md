# Pinboard Feature - Testing & Validation Guide

## Quick Start Test (5 minutes)

### Step 1: Verify Installation
```bash
# Check if ORDO recognizes new commands
ordo --help
# Should show pinboard-related commands

# Test basic pinboard initialization
ordo pinboard-categories
# Output: List of default categories (General, Work, Study, Personal)
```

### Step 2: Pin Some Files
```bash
# Create test files first (if needed)
mkdir ~/test_files
echo "Project notes" > ~/test_files/project.txt
echo "Budget data" > ~/test_files/budget.xlsx
echo "Study material" > ~/test_files/study.pdf

# Scan the directory so files are indexed
ordo scan ~/test_files

# Pin the files
ordo pin ~/test_files/project.txt --category "Work"
ordo pin ~/test_files/budget.xlsx --category "Personal"
ordo pin ~/test_files/study.pdf --category "Study"
```

### Step 3: View Pinboard
```bash
# View in different formats
ordo pinboard                    # List view
ordo pinboard --view grid       # Grid view
ordo pinboard --view category   # Category view
ordo pinboard --stats           # With statistics
```

### Step 4: Test Categories
```bash
# Create custom category
ordo add-category "Projects" --color "#2ecc71"

# Move file to new category
ordo move-to-category ~/test_files/project.txt "Projects"

# View result
ordo pinboard --view category
```

---

## Comprehensive Test Plan

### A. Core Functionality Tests

#### Test 1: Pin/Unpin Operations
```bash
# Test 1.1: Pin a file
ordo pin /path/to/file.txt
# Expected: ✅ File pinned message

# Test 1.2: Pin with category
ordo pin /path/to/file.txt --category "Work"
# Expected: ✅ File pinned to Work category

# Test 1.3: Unpin a file
ordo unpin /path/to/file.txt
# Expected: ✅ File unpinned message

# Test 1.4: Unpin non-existent pin
ordo unpin /nonexistent/path.txt
# Expected: ❌ File not found in pinboard
```

#### Test 2: View Operations
```bash
# Test 2.1: List view
ordo pinboard
# Expected: Detailed list with paths and categories

# Test 2.2: Grid view
ordo pinboard --view grid
# Expected: Icon grid layout

# Test 2.3: Category view
ordo pinboard --view category
# Expected: Files grouped by category

# Test 2.4: List with stats
ordo pinboard --stats
# Expected: Access count included
```

#### Test 3: Category Management
```bash
# Test 3.1: View default categories
ordo pinboard-categories
# Expected: General, Work, Study, Personal

# Test 3.2: Create new category
ordo add-category "Projects"
# Expected: ✅ Category created message

# Test 3.3: Create with color
ordo add-category "Important" --color "#ff0000"
# Expected: Category with hex color

# Test 3.4: Move file to category
ordo move-to-category /path/to/file.txt "Projects"
# Expected: ✅ File moved to category message

# Test 3.5: Verify move
ordo pinboard --view category
# Expected: File appears in Projects category
```

### B. Advanced Feature Tests

#### Test 4: Statistics
```bash
# Test 4.1: View statistics
ordo pinboard-stats
# Expected: Total count, by-category breakdown, most accessed

# Test 4.2: Multiple pinned files
# Pin 10+ files to different categories, then:
ordo pinboard-stats
# Expected: Accurate counts for each category
```

#### Test 5: Suggestions
```bash
# Test 5.1: Get suggestions
ordo pinboard-suggest
# Expected: List of suggested files to pin (if enough usage)

# Test 5.2: Pin suggested file
ordo pin /path/to/suggested/file.txt
# Expected: ✅ File pinned message
```

#### Test 6: Natural Language
```bash
# Test 6.1: Simple name matching
ordo pin-natural "project file"
# Expected: Finds and pins file matching "project file"

# Test 6.2: Partial matching
ordo pin-natural "budget"
# Expected: Finds file containing "budget"

# Test 6.3: Non-existent file
ordo pin-natural "nonexistent file xyz"
# Expected: ❌ No file found message
```

### C. Error Handling Tests

#### Test 7: Edge Cases
```bash
# Test 7.1: Pin already pinned file
ordo pin /path/to/file.txt
ordo pin /path/to/file.txt
# Expected: Second call succeeds, no duplicates

# Test 7.2: Unsafe paths
ordo pin "/System/Library/file.txt"  # System directory
# Expected: ❌ Blocked: Unsafe path

# Test 7.3: Non-existent file
ordo pin /nonexistent/file.txt
# Expected: ❌ File not found message

# Test 7.4: Non-indexed file
# Create a file but don't scan directory
echo "test" > /tmp/new_file.txt
ordo pin /tmp/new_file.txt
# Expected: ❌ File not indexed message
# Solution:
ordo scan /tmp
ordo pin /tmp/new_file.txt
# Expected: ✅ File pinned message
```

### D. Performance Tests

#### Test 8: Scalability
```bash
# Test 8.1: Pin many files
for i in {1..100}; do
  echo "content $i" > ~/test_files/file_$i.txt
  ordo pin ~/test_files/file_$i.txt
done

# Measure:
time ordo pinboard
# Expected: < 100ms for 100 files

time ordo pinboard --view category
# Expected: < 100ms for 100 files

time ordo pinboard-stats
# Expected: < 200ms

# Test 8.2: Large dataset
# Pin 1000+ files
for i in {1..1000}; do
  echo "content $i" > ~/large_test/file_$i.txt
done
ordo scan ~/large_test
# Pin half of them
# Verify performance still acceptable

# Test 8.3: Memory usage
# Monitor memory before/after
ps aux | grep python
ordo pinboard --view grid
ps aux | grep python
# Expected: No excessive memory growth
```

### E. Integration Tests

#### Test 9: Integration with Other Features
```bash
# Test 9.1: Scan and pin
ordo scan ~/documents
ordo pin ~/documents/important.pdf
ordo pinboard

# Test 9.2: Search and pin
ordo search --year 2024
# Pin some results:
ordo pin /path/to/search/result.txt

# Test 9.3: Organize and pin
ordo pin ~/files/document.docx --category "Work"
ordo organize ~/files

# Test 9.4: Verify pinboard after changes
ordo pinboard
# Expected: Pinned file still listed, maybe in new location
```

---

## Database Validation Tests

### Test 10: Database Integrity
```bash
# Test 10.1: Database exists
ls -la data/index.db
# Expected: File exists and is readable

# Test 10.2: Check schema
sqlite3 data/index.db ".tables"
# Expected: Shows pinboard, pin_categories tables

# Test 10.3: Check data
sqlite3 data/index.db "SELECT COUNT(*) FROM pinboard WHERE is_pinned = 1;"
# Expected: Correct count of pinned files

# Test 10.4: Check indexes
sqlite3 data/index.db ".indices"
# Expected: Shows idx_pinboard_status, idx_pinboard_category
```

---

## Scenario-Based Tests

### Test 11: Real-World Workflows

#### Scenario A: Developer Workflow
```bash
# Setup
ordo add-category "Development"
ordo add-category "Documentation"
ordo add-category "Testing"

# Pin project files
ordo pin ~/projects/main_app/src/main.py -c "Development"
ordo pin ~/projects/main_app/tests/ -c "Testing"
ordo pin ~/projects/main_app/README.md -c "Documentation"
ordo pin ~/projects/main_app/requirements.txt -c "Development"

# Verify setup
ordo pinboard --view category
# Expected: Files organized by development category

# Get stats
ordo pinboard-stats
# Expected: 4 total, distributed across categories
```

#### Scenario B: Student Workflow
```bash
# Setup
ordo add-category "Math" --color "#3498db"
ordo add-category "Physics" --color "#e74c3c"
ordo add-category "Literature" --color "#2ecc71"

# Pin study materials
ordo pin ~/studies/math/calculus_notes.pdf -c "Math"
ordo pin ~/studies/math/exercises.xlsx -c "Math"
ordo pin ~/studies/physics/formulas.md -c "Physics"
ordo pin ~/studies/literature/summary.txt -c "Literature"

# Quick access
ordo pinboard
# Natural language access
ordo pin-natural "math notes"
```

#### Scenario C: Project Manager Workflow
```bash
# Setup
ordo add-category "Project-Alpha"
ordo add-category "Project-Beta"
ordo add-category "Admin"

# Pin essentials
ordo pin ~/projects/alpha/roadmap.md -c "Project-Alpha"
ordo pin ~/projects/alpha/budget.xlsx -c "Project-Alpha"
ordo pin ~/projects/beta/timeline.pdf -c "Project-Beta"
ordo pin ~/company/admin/policies.docx -c "Admin"

# Monitor usage
ordo pinboard-stats
# Expected: Clear breakdown of project focus
```

---

## Verification Checklist

### Functional Requirements
- [ ] Pin functionality works
- [ ] Unpin functionality works
- [ ] Multiple view modes (list, grid, category)
- [ ] Category creation and management
- [ ] Category reassignment
- [ ] Statistics display
- [ ] Suggestion system
- [ ] Natural language support

### Non-Functional Requirements
- [ ] Database creates successfully
- [ ] Queries complete in < 100ms
- [ ] Handles 1000+ files
- [ ] Safe path validation
- [ ] Error messages are clear
- [ ] Memory usage acceptable
- [ ] Works across multiple sessions

### User Experience
- [ ] Help text is clear
- [ ] Output formatting is readable
- [ ] Icons display correctly
- [ ] Timestamps are human-readable
- [ ] Command structure is intuitive
- [ ] Error recovery is smooth

### Documentation
- [ ] README is complete
- [ ] Examples work as documented
- [ ] Commands match documentation
- [ ] Help text matches docs

---

## Troubleshooting Tests

### Test 12: Common Issues

#### Issue 1: "File not indexed"
```bash
# Root cause: File exists but not in database
# Solution:
ordo scan /path/to/file/directory
ordo pin /path/to/file.txt

# Verify:
ordo pinboard
# Expected: File appears
```

#### Issue 2: Empty pinboard
```bash
# Root cause: No files pinned yet
# Solution:
ordo scan ~/documents
ordo pin ~/documents/file.txt
ordo pinboard

# Verify:
# Expected: File appears in pinboard
```

#### Issue 3: Old categories missing
```bash
# Root cause: Database reset or corruption
# Solution:
# Backup database
cp data/index.db data/index.db.backup

# Recreate database
rm data/index.db
ordo pinboard-categories

# Restore from backup if needed
mv data/index.db.backup data/index.db
```

#### Issue 4: Slow pinboard views
```bash
# Root cause: Too many files
# Solution: Use filtered views
ordo pinboard --view category  # Faster than full list

# Or check database
sqlite3 data/index.db "EXPLAIN QUERY PLAN SELECT * FROM pinboard WHERE is_pinned = 1 ORDER BY pin_order;"

# Verify indexes exist:
sqlite3 data/index.db ".indices"
```

---

## Performance Benchmarks

### Expected Results
| Operation | Expected Time | Test Command |
|-----------|---------------|--------------|
| Pin file | < 10ms | `time ordo pin <file>` |
| Unpin file | < 5ms | `time ordo unpin <file>` |
| View 100 files | < 50ms | `time ordo pinboard` |
| View grid | < 100ms | `time ordo pinboard --view grid` |
| View by category | < 80ms | `time ordo pinboard --view category` |
| Get stats | < 100ms | `time ordo pinboard-stats` |
| Get suggestions | < 200ms | `time ordo pinboard-suggest` |

### Benchmark Test Script
```bash
#!/bin/bash
# Save as benchmark.sh

echo "=== PINBOARD PERFORMANCE BENCHMARKS ==="

# Setup
ordo scan ~/test_benchmark

# Pin test
echo "Pinning 10 files..."
for i in {1..10}; do
  time ordo pin ~/test_benchmark/file_$i.txt
done

# View tests
echo "View operations..."
time ordo pinboard
time ordo pinboard --view grid
time ordo pinboard --view category

# Stats test
echo "Statistics..."
time ordo pinboard-stats

# Suggestions
echo "Suggestions..."
time ordo pinboard-suggest
```

---

## Sign-Off Checklist

After completing all tests, verify:

- [ ] All commands execute without errors
- [ ] Database contains correct data
- [ ] Performance meets expectations
- [ ] Error handling is robust
- [ ] Documentation is accurate
- [ ] Integration with ORDO works
- [ ] No security vulnerabilities
- [ ] Clean error messages
- [ ] Intuitive user experience
- [ ] Ready for production

---

## Notes for Testers

1. **File Paths**: Always use files that exist and are properly indexed
2. **Categories**: Test both default and custom categories
3. **Database**: Check `data/index.db` with SQLite to verify data
4. **Performance**: Test with various dataset sizes (10, 100, 1000 files)
5. **Error Cases**: Try invalid inputs to ensure graceful handling
6. **Integration**: Verify pinboard works with other ORDO features

---

## Final Validation Command

```bash
# Run this comprehensive test:
echo "1. Checking if commands exist..."
ordo --help | grep -E "pin|pinboard"

echo "2. Testing basic pinboard..."
ordo pinboard

echo "3. Testing categories..."
ordo pinboard-categories

echo "4. Checking database..."
sqlite3 data/index.db "SELECT COUNT(*) FROM pinboard;"

echo "5. All systems operational!"
```

---

*Created: April 10, 2026*
*Status: Ready for Testing*
