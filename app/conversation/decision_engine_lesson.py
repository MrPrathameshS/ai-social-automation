from app.core.llm import call_llm


def decide_lesson_action(state, user_message):

    prompt = f"""
You are a classifier.

Your job is to return ONE word.

Possible outputs:

confirm
refine
suggest


User message:
{user_message}


Rules:

Return suggest if user is unsure.

Unsure examples:
not sure
idk
dont know
no idea
nothing
unsure


Return confirm if message is a clear lesson.

Examples:
state machines help
refresh tokens need storage
retry logic needs idempotency
jwt needs blacklist


Return refine if message is vague but not unsure.

Examples:
learned a lot
many things
it helped


Return ONLY one word.
Do not explain.
Do not write sentences.
Do not write anything else.
"""

    result = call_llm(prompt).strip().lower()

    print("LESSON DECISION:", result)

    if result == "confirm":
        return "confirm"

    if result == "suggest":
        return "suggest"

    if result == "refine":
        return "refine"

    # fallback
    return "refine"