from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models import PromptTemplate, BrandProfile


BASE_PROMPTS = {
    "linkedin": """You are a professional LinkedIn thought leadership writer.
Write insightful, value-driven posts for senior leaders and decision makers.
Tone: authoritative, strategic, inspiring.
Avoid emojis. Focus on clarity and impact.""",

    "instagram": """You are a high-engagement Instagram content creator.
Write short, punchy, emotionally engaging captions.
Use light emojis, line breaks, and hashtags.
Focus on inspiration, relatability, and shareability.""",
}


def seed_base_prompts_for_brand(brand_id: int):
    db: Session = SessionLocal()
    try:
        brand = db.query(BrandProfile).filter(BrandProfile.id == brand_id).first()
        if not brand:
            print(f"⚠️ Brand not found for id: {brand_id}")
            return

        for platform, base_prompt in BASE_PROMPTS.items():
            exists = (
                db.query(PromptTemplate)
                .filter_by(brand_id=brand.id, platform=platform)
                .first()
            )

            if not exists:
                prompt = PromptTemplate(
                    brand_id=brand.id,
                    platform=platform,
                    version=1,
                    prompt_text=base_prompt,
                    mutation_reason="Base seed"
                )
                db.add(prompt)
                print(f"🌱 Seeded base prompt for {brand.brand_name} on {platform}")

        db.commit()
    finally:
        db.close()


def get_latest_prompt_record(brand_id: int, platform: str):
    db: Session = SessionLocal()
    try:
        return (
            db.query(PromptTemplate)
            .filter(
                PromptTemplate.brand_id == brand_id,
                PromptTemplate.platform == platform
            )
            .order_by(PromptTemplate.version.desc())
            .first()
        )
    finally:
        db.close()


def regenerate_prompts_for_brand(db: Session, brand_id: int):
    brand = db.query(BrandProfile).filter(BrandProfile.id == brand_id).first()
    if not brand:
        print(f"⚠️ Brand not found for id: {brand_id}")
        return

    print(f"🔁 Regenerating prompts for brand: {brand.brand_name}")

    platforms = ["instagram", "linkedin"]

    for platform in platforms:
        latest_prompt = (
            db.query(PromptTemplate)
            .filter(
                PromptTemplate.brand_id == brand.id,
                PromptTemplate.platform == platform
            )
            .order_by(PromptTemplate.version.desc())
            .first()
        )

        new_version = latest_prompt.version + 1 if latest_prompt else 1
        base_prompt = BASE_PROMPTS.get(platform, "")

        new_prompt = PromptTemplate(
            brand_id=brand.id,
            platform=platform,
            version=new_version,
            prompt_text=base_prompt,
            mutation_reason="Regenerated base prompt"
        )

        db.add(new_prompt)

    db.commit()
    print(f"✅ Prompts regenerated for brand: {brand.brand_name}")
