import gspread
from google.oauth2.service_account import Credentials
from app.db.session import SessionLocal
from app.db.models import GeneratedContent, Topic

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

SERVICE_ACCOUNT_FILE = "credentials.json"
SHEET_NAME = "AI Social Automation Control"


def sync_db_status_to_sheet():
    print("🔄 Syncing DB status to Google Sheet...")

    creds = Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    client = gspread.authorize(creds)
    sheet = client.open(SHEET_NAME).sheet1

    rows = sheet.get_all_records()
    headers = sheet.row_values(1)
    print("📋 Sheet Headers:", headers)

    # --- SAFE COLUMN RESOLVER ---
    def col_idx(name):
        name = name.strip().lower()
        for i, h in enumerate(headers):
            if h.strip().lower() == name:
                return i + 1
        return None

    status_col = col_idx("status")
    scheduled_col = col_idx("scheduled_at")
    posted_col = col_idx("posted_at")

    print(f"🔎 Resolved columns → status:{status_col}, scheduled:{scheduled_col}, posted:{posted_col}")

    db = SessionLocal()

    try:
        contents = db.query(GeneratedContent).all()
        topics = db.query(Topic).all()

        # Build topic_id → topic_text map ONCE
        topic_map = {t.id: t.topic_text for t in topics}

        for i, row in enumerate(rows, start=2):  # start=2 because header is row 1
            topic_text = row.get("topic")
            platforms_raw = row.get("platforms", "")

            if not topic_text or not platforms_raw:
                continue

            platform_list = [p.strip().lower() for p in platforms_raw.split(",")]

            matched_contents = [
                c for c in contents
                if topic_map.get(c.topic_id) == topic_text and c.platform.lower() in platform_list
            ]

            if not matched_contents:
                continue

            # ---- MERGE LOGIC ----
            final_status = "pending"
            final_scheduled = None
            final_posted = None

            for c in matched_contents:
                if c.status == "posted":
                    final_status = "posted"
                elif c.status == "approved" and final_status != "posted":
                    final_status = "approved"

                if c.scheduled_at:
                    final_scheduled = c.scheduled_at
                if c.posted_at:
                    final_posted = c.posted_at

            # ---- WRITE TO SHEET ----
            if status_col:
                sheet.update_cell(i, status_col, final_status)

            if scheduled_col:
                sheet.update_cell(
                    i,
                    scheduled_col,
                    final_scheduled.isoformat() if final_scheduled else ""
                )

            if posted_col:
                sheet.update_cell(
                    i,
                    posted_col,
                    final_posted.isoformat() if final_posted else ""
                )

            print(f"🔄 Synced row {i} | {topic_text} | {platform_list} → {final_status}")

        print("✅ Sheet status sync complete")

    except Exception as e:
        print(f"❌ Sheet status sync error: {e}")
    finally:
        db.close()
