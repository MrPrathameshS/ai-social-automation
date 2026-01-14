print("🔥 LOADED bulk_approval_worker.py")

import sys
import os
import time

# ----------------- PATH FIX -----------------
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.append(ROOT_DIR)

# ----------------- IMPORTS -----------------
from app.services.bulk_approval_processor import run_bulk_approval_engine

# ----------------- BOOT -----------------
print("🚀 Bulk Approval Worker started...")

def main():
    while True:
        try:
            print("\n🚀 BULK APPROVAL ENGINE TICK")
            run_bulk_approval_engine()
        except Exception as e:
            print(f"❌ Bulk approval loop error: {e}")

        time.sleep(60)  # run every 60 seconds


if __name__ == "__main__":
    main()
