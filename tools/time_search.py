import sqlite3
from datetime import datetime

DB_PATH = "data/index.db"

def _run_query(start_ts, end_ts):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
    SELECT name, path, created_time
    FROM files
    WHERE created_time BETWEEN ? AND ?
    ORDER BY created_time DESC
    """, (start_ts, end_ts))

    rows = cur.fetchall()
    conn.close()

    results = []
    for name, path, ts in rows:
        readable = datetime.fromtimestamp(ts)
        results.append((name, path, readable))

    return results


# ------------------------------------------------
# Filter by specific DAY
# Example: day=15, month=3, year=2025
# ------------------------------------------------
def filter_by_day(day, month, year):
    start = datetime(year, month, day, 0, 0, 0).timestamp()
    end   = datetime(year, month, day, 23, 59, 59).timestamp()
    return _run_query(start, end)


# ------------------------------------------------
# Filter by MONTH
# Example: March 2025 → month=3, year=2025
# ------------------------------------------------
def filter_by_month(month, year):
    start = datetime(year, month, 1, 0, 0, 0).timestamp()

    if month == 12:
        end = datetime(year + 1, 1, 1, 0, 0, 0).timestamp()
    else:
        end = datetime(year, month + 1, 1, 0, 0, 0).timestamp()

    return _run_query(start, end)


# ------------------------------------------------
# Filter by YEAR
# Example: year=2024
# ------------------------------------------------
def filter_by_year(year):
    start = datetime(year, 1, 1, 0, 0, 0).timestamp()
    end   = datetime(year + 1, 1, 1, 0, 0, 0).timestamp()
    return _run_query(start, end)


# ------------------------------------------------
# Filter by DATE RANGE
# Example: 2024-01-01 → 2024-06-30
# ------------------------------------------------
def filter_by_range(start_date, end_date):
    """
    start_date, end_date format: 'YYYY-MM-DD'
    """
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt   = datetime.strptime(end_date, "%Y-%m-%d")

    start_ts = start_dt.timestamp()
    end_ts   = end_dt.timestamp()

    return _run_query(start_ts, end_ts)