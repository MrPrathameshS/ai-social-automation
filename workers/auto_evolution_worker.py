import time
from app.services.auto_evolution_runner import run_auto_evolution_cycle


if __name__ == "__main__":
    print("🧬 Autonomous Strategy Evolution Worker started...")

    while True:
        run_auto_evolution_cycle()

        # Sleep 6 hours between cycles (adjustable)
        time.sleep(6 * 60 * 60)
