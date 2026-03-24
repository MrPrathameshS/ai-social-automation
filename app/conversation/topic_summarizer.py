from app.core.llm import call_llm


def build_prompt(old_topic, new_message):

    return f"""
We are building a topic for a LinkedIn post.

Current topic:
{old_topic}

New info from user:
{new_message}

Rewrite the topic as ONE short clean sentence.

Rules:
- keep it short
- keep meaning
- no extra text
- no quotes
"""


def summarize_topic(old_topic, new_message):

    prompt = build_prompt(old_topic, new_message)

    text = call_llm(prompt)

    return text.strip()