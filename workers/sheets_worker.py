import sys
import os

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(ROOT_DIR)

from app.services.sheets_service import get_sheet_rows, ingest_topics_from_sheet

print("🔥 LOADED NEW sheets_worker.py")


def main():
    print("🚀 Sheets worker started...")
    rows = get_sheet_rows()
    print(f"📥 Fetched {len(rows)} rows from Google Sheet")
    ingest_topics_from_sheet(rows)
    print("✅ Sheets ingestion complete")


if __name__ == "__main__":
    main()
