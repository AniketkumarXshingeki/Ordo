import sys
from ordo.indexer.content_pipeline import scan_with_path

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python scripts/scan_path.py <path>')
    else:
        scan_with_path(sys.argv[1])

