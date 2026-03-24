# app/rag/knowledge_data.py


KNOWLEDGE = {

    "scheduler": {
        "challenges": [
            "retry logic",
            "job deduplication",
            "timeout handling",
            "state tracking",
            "distributed scheduling",
            "race conditions",
            "cron parsing",
        ],
        "lessons": [
            "state machines simplify scheduling",
            "idempotency is important",
            "queues help manage retries",
            "locking prevents duplicates",
            "observability is critical",
        ],
        "angles": [
            "engineering lesson",
            "system design insight",
            "debugging story",
            "performance optimization",
        ],
    },

    "machine learning": {
        "challenges": [
            "data imbalance",
            "overfitting",
            "slow training",
            "bad labels",
            "feature leakage",
        ],
        "lessons": [
            "data quality matters more than model",
            "simpler models generalize better",
            "validation is critical",
            "hyperparameters matter",
        ],
        "angles": [
            "research insight",
            "experiment failure",
            "model improvement",
        ],
    },

    "backend": {
        "challenges": [
            "race conditions",
            "database locks",
            "scaling issues",
            "timeout errors",
            "cache invalidation",
        ],
        "lessons": [
            "logs are essential",
            "monitoring saves time",
            "stateless services scale better",
            "small changes break systems",
        ],
        "angles": [
            "engineering lesson",
            "production bug",
            "architecture insight",
        ],
    },

}