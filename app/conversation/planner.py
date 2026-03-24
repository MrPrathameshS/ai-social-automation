# app/conversation/planner.py

import json

from app.db.models.conversation_state import ConversationState
from app.core.llm import call_llm

from app.conversation.topic_summarizer import summarize_topic
from app.conversation.decision_engine import decide_action

from app.rag.retriever import (
    get_challenges,
    get_lessons,
    get_angles,
)
from app.conversation.decision_engine_lesson import decide_lesson_action

STEPS = [
    "ASK_TOPIC",
    "REFINE_TOPIC",
    "CONFIRM_TOPIC",
    "ASK_CHALLENGE",
    "ASK_LESSON",
    "ASK_ANGLE",
    "SUMMARY",
    "DONE",
]


# -------------------------
# fallback prompt (keep)
# -------------------------


def build_prompt(
    state: ConversationState,
    user_message: str,
) -> str:

    challenges = get_challenges(state.topic)
    lessons = get_lessons(state.topic)
    angles = get_angles(state.topic)

    return f"""
We are building a LinkedIn post.

topic: {state.topic}
challenge: {state.challenge}
lesson: {state.lesson}
angle: {state.angle}
step: {state.step}

User message:
{user_message}

Known challenges:
{challenges}

Known lessons:
{lessons}

Known angles:
{angles}

Return JSON.
"""


def build_system_prompt():

    return """
Return ONLY JSON.
"""


def call_planner_llm(prompt: str) -> dict:

    text = call_llm(
        prompt=prompt,
        system_prompt=build_system_prompt(),
    )

    try:
        return json.loads(text)

    except Exception:

        start = text.find("{")
        end = text.rfind("}") + 1

        return json.loads(text[start:end])


# -------------------------
# MAIN
# -------------------------


def plan(state: ConversationState, user_message: str) -> dict:

    msg = user_message.lower().strip()

    # -------------------------
    # SUMMARY
    # -------------------------

    if state.step == "SUMMARY":

        if msg in ["yes", "y", "generate", "ok", "go ahead"]:

            return {
                "field": "none",
                "value": None,
                "next_step": "DONE",
                "reply": "Generating preview...",
                "done": True,
            }

        else:

            return {
                "field": "none",
                "value": None,
                "next_step": "ASK_CHALLENGE",
                "question_type": "challenge",
                "done": False,
            }

    # -------------------------
    # ASK_TOPIC
    # -------------------------

    if state.step == "ASK_TOPIC":

        return {
            "field": "topic",
            "value": user_message,
            "next_step": "REFINE_TOPIC",
            "question_type": "refine_topic",
            "done": False,
        }

    # -------------------------
    # REFINE_TOPIC (decision engine)
    # -------------------------

    if state.step == "REFINE_TOPIC":

        action = decide_action(
            state,
            state.step,
            user_message,
        )

        # refine more
        if action == "refine":

            return {
                "field": "topic",
                "value": user_message,
                "next_step": "REFINE_TOPIC",
                "question_type": "refine_topic",
                "done": False,
            }

        # confirm
        if action == "confirm":

            new_topic = summarize_topic(
                state.topic,
                user_message,
            )

            return {
                "field": "topic",
                "value": new_topic,
                "next_step": "CONFIRM_TOPIC",
                "question_type": "confirm_topic",
                "done": False,
            }

        # suggest
        if action == "suggest":

            return {
                "field": "none",
                "value": None,
                "next_step": "REFINE_TOPIC",
                "question_type": "refine_topic",
                "done": False,
            }

        # next

        new_topic = summarize_topic(
            state.topic,
            user_message,
        )

        return {
            "field": "topic",
            "value": new_topic,
            "next_step": "CONFIRM_TOPIC",
            "question_type": "confirm_topic",
            "done": False,
        }

    # -------------------------
    # CONFIRM_TOPIC
    # -------------------------

    if state.step == "CONFIRM_TOPIC":

        action = decide_action(
            state,
            state.step,
            user_message,
        )

        if action == "confirm":

            return {
                "field": "none",
                "value": None,
                "next_step": "ASK_CHALLENGE",
                "question_type": "ask_challenge",
                "done": False,
            }

        if action == "refine":

            return {
                "field": "none",
                "value": None,
                "next_step": "REFINE_TOPIC",
                "question_type": "refine_topic",
                "done": False,
            }

        if action == "suggest":

            return {
                "field": "none",
                "value": None,
                "next_step": "REFINE_TOPIC",
                "question_type": "refine_topic",
                "done": False,
            }

    
    # -------------------------
    # ASK_CHALLENGE
    # -------------------------

    if state.step == "ASK_CHALLENGE":

        action = decide_action(
            state,
            state.step,
            user_message,
        )

        # ---------- refine ----------
        if action == "refine":

            return {
                "field": "challenge",
                "value": user_message,
                "next_step": "ASK_CHALLENGE",
                "question_type": "refine_challenge",
                "done": False,
            }

        # ---------- confirm ----------
        if action == "confirm":

            return {
                "field": "challenge",
                "value": user_message,
                "next_step": "ASK_LESSON",
                "question_type": "ask_lesson",
                "done": False,
            }

        # ---------- suggest ----------
        if action == "suggest":

            return {
                "field": "none",
                "value": None,
                "next_step": "ASK_CHALLENGE",
                "question_type": "suggest_challenge",
                "done": False,
            }

        # ---------- fallback ----------
        return {
            "field": "challenge",
            "value": user_message,
            "next_step": "ASK_LESSON",
            "question_type": "ask_lesson",
            "done": False,
        }

    # -------------------------
    # ASK_LESSON (dynamic)
    # -------------------------

    if state.step == "ASK_LESSON":

        action = decide_lesson_action(
            state,
            user_message,
        )

        # ---------- refine ----------
        if action == "refine":

            return {
                "field": "lesson",
                "value": user_message,
                "next_step": "ASK_LESSON",
                "question_type": "refine_lesson",
                "done": False,
            }

        # ---------- confirm ----------
        if action == "confirm":

            return {
                "field": "lesson",
                "value": user_message,
                "next_step": "ASK_ANGLE",
                "question_type": "ask_angle",
                "done": False,
            }

        # ---------- suggest ----------
        if action == "suggest":

            return {
                "field": "none",
                "value": None,
                "next_step": "ASK_LESSON",
                "question_type": "suggest_lesson",
                "done": False,
            }

        # ---------- fallback ----------
        return {
            "field": "lesson",
            "value": user_message,
            "next_step": "ASK_ANGLE",
            "question_type": "ask_angle",
            "done": False,
        }

    # -------------------------
    # ASK_ANGLE
    # -------------------------

    if state.step == "ASK_ANGLE":

        return {
            "field": "angle",
            "value": user_message,
            "next_step": "SUMMARY",
            "question_type": "summary",
            "done": False,
        }

    # -------------------------
    # fallback
    # -------------------------

    prompt = build_prompt(state, user_message)

    return call_planner_llm(prompt)