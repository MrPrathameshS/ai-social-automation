from groq import Groq
from app.services.prompt_registry import get_latest_prompt_record
from app.services.brand_prompt_builder import build_brand_prompt_layer
from app.services.brand_rule_prompt_builder import build_rule_prompt_layer
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def generate_content(
    topic: str,
    brand_id: int,
    platform: str,
    content_type: str = "post"
) -> str:

    prompt_record = get_latest_prompt_record(brand_id, platform)

    if not prompt_record:
        raise ValueError(f"No prompt found for brand_id={brand_id}, platform={platform}")

    brand_prompt = build_brand_prompt_layer(brand_id)

    rule_prompt = build_rule_prompt_layer(
        brand_id=brand_id,
        platform=platform,
        category_id=None
    )

    system_prompt = f"""
{prompt_record.prompt_text}

{brand_prompt}

{rule_prompt}

You are an expert social media strategist and brand voice writer.
Follow the brand tone strictly.
Follow all rules strictly.
Do not mention AI. Do not explain the process.
""".strip()

    user_prompt = f"""
CONTENT INSTRUCTION:

Create a {content_type} for {platform}.

Topic: {topic}

Write high-quality, original content tailored exactly for this platform and brand.
Be specific, insightful, and engaging. Avoid generic phrasing.
""".strip()

    print(f"🧠 Generating content for brand_id={brand_id}, topic='{topic}', platform={platform}")

    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.7,
    )

    return response.choices[0].message.content.strip()
