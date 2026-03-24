from app.core.llm import call_llm


def build_prompt(state, question_type, user_message=None):

    return f"""
You are having a natural conversation with a developer.

Current step: {state.step}

Context:

topic: {state.topic}
challenge: {state.challenge}
lesson: {state.lesson}
angle: {state.angle}

Question type: {question_type}


Rules:

Be natural
One short message
No markdown
No lists
No explanations


----------------------

If confirm_topic:

Confirm this topic:

{state.topic}


----------------------

If refine_topic:

Ask for more detail about the topic.


----------------------

If suggest_topic:

Suggest 2–3 possible directions for the topic.


----------------------

If refine_challenge:

Ask for more detail about the challenge.


----------------------

If suggest_challenge:

Suggest possible challenges based on topic.


----------------------

If ask_lesson:

Ask what insight or lesson the user learned
from solving the challenge.


----------------------

If refine_lesson:

User gave a vague lesson.
Ask them to explain the lesson more clearly.


----------------------

If suggest_lesson:

User is unsure about the lesson.
Suggest possible lessons based on the challenge.


----------------------

If ask_angle:

Ask what angle the post should take.

Examples:
engineering lesson
mistake story
technical deep dive
tip for others
funny story


----------------------

If summary:

Say we will generate the post preview.


----------------------

Return only the message.
"""


def generate_question(
    state,
    question_type,
    user_message=None,
):

    prompt = build_prompt(
        state,
        question_type,
        user_message,
    )

    return call_llm(prompt)