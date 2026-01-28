from app.services.engagement_collector import collect_engagement_metrics
from app.services.ai_performance_analyzer import analyze_performance_and_learn
from app.services.strategy_evolution_engine import run_strategy_evolution
from app.services.ai_scheduler import run_ai_scheduler


def run_auto_evolution_cycle():
    print("\n🚀 AUTO EVOLUTION CYCLE STARTED\n")

    print("1️⃣ Collecting engagement...")
    collect_engagement_metrics()

    print("2️⃣ Analyzing performance...")
    analyze_performance_and_learn()

    print("3️⃣ Detecting drift & mutating strategy if needed...")
    run_strategy_evolution()

    print("4️⃣ Re-running AI scheduler with latest strategy...")
    run_ai_scheduler()

    print("\n✅ AUTO EVOLUTION CYCLE COMPLETE\n")
