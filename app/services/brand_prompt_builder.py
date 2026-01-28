from app.services.brand_registry import get_brand_profile_by_id


def build_brand_prompt_layer(brand_id: int) -> str:
    profile = get_brand_profile_by_id(brand_id)

    if not profile:
        return ""

    layer = f"""
BRAND PERSONALITY:
Brand Name: {profile.brand_name}
Tone: {profile.tone_description}
Audience: {profile.audience_description}
Writing Style: {profile.writing_style}
Constraints: {profile.do_not_use}

LEARNED INSIGHTS:
{profile.learned_insights or "No learned insights yet."}
"""

    return layer.strip()
