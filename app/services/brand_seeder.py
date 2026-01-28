from app.services.brand_registry import seed_brand_profile


def seed_brands():
    seed_brand_profile(
        brand_name="AI for Business",
        tone="Authoritative, visionary, data-driven",
        audience="CXOs, founders, enterprise leaders",
        style="Clear structure, insight-driven, confident statements",
        constraints="No emojis, no slang, no hype language"
    )

    seed_brand_profile(
        brand_name="Leadership Quotes",
        tone="Inspirational, bold, emotionally resonant",
        audience="Aspiring leaders, managers, entrepreneurs",
        style="Short impactful lines, rhetorical questions, punchy flow",
        constraints="No corporate jargon, no technical terms"
    )
