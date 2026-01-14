from groq import Groq
from app.services.prompt_registry import get_latest_prompt_record
from app.services.brand_prompt_builder import build_brand_prompt_layer
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def generate_content(
    topic: str,
    brand_id: int,
    platform: str,
    content_type: str = "post"
) -> str:
    """
    Generates platform-aware, brand-aware, adaptive content using:
    - Brand-scoped platform prompt
    - Brand personality layer
    - Content instruction layer
    """

    # 1️⃣ Pull latest brand-scoped adaptive system prompt
    prompt_record = get_latest_prompt_record(brand_id, platform)

    if not prompt_record:
        raise ValueError(f"No prompt found for brand_id={brand_id}, platform={platform}")

    # 2️⃣ Build brand personality layer
    brand_prompt = build_brand_prompt_layer(brand_id)

    # 3️⃣ Final stacked system prompt
    system_prompt = f"""
{prompt_record.prompt_text}

{brand_prompt}

You are an expert social media strategist and brand voice writer.
Follow the brand tone strictly. Do not mention AI. Do not explain the process.
""".strip()

    user_prompt = f"""
CONTENT INSTRUCTION:

Create a {content_type} for {platform}.

Topic: {topic}

Write high-quality, original content tailored exactly for this platform and brand.
Be specific, insightful, and engaging. Avoid generic phrasing.
""".strip()

    print(f"🧠 Generating content for brand_id={brand_id}, topic='{topic}', platform={platform}")

    # 4️⃣ LLM call
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()
