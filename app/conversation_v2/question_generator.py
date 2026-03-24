from typing import Dict, Any

from app.core.llm import call_llm

def get_stage_instruction(stage: str) -> str:

    if stage == "ASK_TOPIC":
        return "Ask what topic the post should be about."

    if stage == "REFINE_TOPIC":
        return "Ask the user to clarify the topic."

    if stage == "CONFIRM_TOPIC":
        return (
            "Restate the topic clearly.\n"
            "Then ask the user to confirm it.\n\n"
            "Tell the user:\n"
            "- type YES to continue\n"
            "- type anything else to refine the topic\n\n"
            "Do not ask an open-ended question.\n"
            "Do not assume the answer.\n"
            "Keep it short."
        )

    if stage == "ASK_PROJECT":
        return "Ask what project they are working on."
    if stage == "ASK_PROJECT_DESC":
        return "Ask the user to describe what the project does."

    

    if stage == "ASK_CONTEXT":
        return (
            "Ask what context this post belongs to.\n"
            "User must choose one of these:\n"
            "- learning\n"
            "- milestone\n"
            "- update\n"
            "- problem\n"
            "- experiment\n"
            "- announcement\n"
            "- reflection\n"
            "- build log\n"
            "- job search\n"
            "- launch\n"
            "Do not ask open ended question."
        )

    if stage == "ASK_STORY":
        return "Ask what happened. Ask for the story."

    if stage == "ASK_LESSON":
        return "Ask what they learned."

    if stage == "ASK_ANGLE":
        return "Ask what angle the post should focus on."

    

    if stage == "ASK_INTENT":
        return (
            "Ask what the user wants this post to achieve.\n"
            "Show these options:\n"
            "1. Teach something\n"
            "2. Build authority\n"
            "3. Attract recruiters\n"
            "4. Promote a project\n"
            "5. Share progress\n"
            "6. Tell a story\n"
            "User must choose one option.\n"
            "Do not ask an open-ended question."
        )

    if stage == "ASK_TONE":
        return (
            "Ask what tone the post should have.\n"
            "Show options:\n"
            "1. Professional\n"
            "2. Casual\n"
            "3. Inspirational\n"
            "4. Educational\n"
            "5. Storytelling\n"
            "6. Bold\n"
            "User must choose one."
        )

    if stage == "ASK_AUDIENCE":
        return (
            "Ask who the post is for.\n"
            "Show options:\n"
            "1. AI engineers\n"
            "2. Recruiters\n"
            "3. Founders\n"
            "4. Developers\n"
            "5. Students\n"
            "6. General audience\n"
            "User must choose one."
        )

    if stage == "ASK_CTA":
        return "Ask what call-to-action to include."

    return "Ask the next question."

def build_prompt(
    stage: str,
    state: Dict[str, Any],
    user_input: str,
) -> str:

    instruction = get_stage_instruction(stage)

    last_user = state.get("last_user_message")
    last_assistant = state.get("last_assistant_message")

    return f"""
You are an AI writing assistant helping create a LinkedIn post.

Current stage: {stage}

Stage instruction:
{instruction}

IMPORTANT RULES:
- Follow the stage instruction strictly
- Do not skip stages
- If this is a CONFIRM stage, ask only a confirmation question
- Do not ask about other fields
- Do not assume the user's answer

Collected info:

topic: {state.get("topic")}
project: {state.get("project")}
project_desc: {state.get("project_desc")}
context: {state.get("context")}
story: {state.get("story")}
lesson: {state.get("lesson")}
angle: {state.get("angle")}
intent: {state.get("intent")}
tone: {state.get("tone")}
audience: {state.get("audience")}

Last assistant:
{last_assistant}

Last user:
{last_user}

User message:
{user_input}

Ask the next question.
Keep it short.
Be natural.
"""


def generate_question(
    stage: str,
    state: Dict[str, Any],
    user_input: str,
) -> str:

    prompt = build_prompt(
        stage=stage,
        state=state,
        user_input=user_input,
    )

    reply = call_llm(prompt)

    return reply.strip()