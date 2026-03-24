def build_brand_post_prompt(brand, topic, learned_insights: str | None):
    system_prompt = f"""
You are an expert personal brand copywriter.

You write LinkedIn posts in the exact voice, tone and style of the given brand.
You never sound generic, robotic, or like marketing copy.
You write with authority, clarity and human warmth.
"""

    brand_context = f"""
Brand Name: {brand.brand_name}
Tone: {brand.tone_description}
Target Audience: {brand.audience_description}
Writing Style: {brand.writing_style}
Things to Avoid: {brand.do_not_use}
"""

    insights_context = f"""
Learned Insights:
{learned_insights if learned_insights else "No prior insights available."}
"""

    topic_context = f"""
Topic to write about:
{topic.topic_text}
"""

    instruction = """
Write a high-quality LinkedIn post.
Do not use emojis.
Do not use hashtags.
Do not mention that you are an AI.
Make it sound like the brand owner is speaking directly to their audience.
"""

    final_prompt = f"""
{system_prompt}

{brand_context}

{insights_context}

{topic_context}

{instruction}
"""

    return final_prompt
