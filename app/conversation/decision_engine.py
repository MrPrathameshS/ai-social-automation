from app.core.llm import call_llm


def build_prompt(state, step, user_message):

    return f"""
You decide what the assistant should do next.

Current step:
{step}

IMPORTANT:
You must follow ONLY the rules for the current step.
Ignore rules for other steps.

User message:
{user_message}

Current context:

topic: {state.topic}
challenge: {state.challenge}
lesson: {state.lesson}
angle: {state.angle}


Possible actions:

refine = user added more detail
confirm = enough information collected
suggest = user unsure / vague / short / confused



RULES FOR TOPIC

Return confirm if the user message clearly describes
a technical project, feature, or system.

Confirm even if short.

Examples of confirm:
- built jwt auth api
- made authentication system
- built retry logic
- created caching layer
- built websocket server
- implemented refresh token rotation
- built backend service
- built api
- built ml model

Return suggest if:
- user unsure
- message very vague
- user says idk / not sure
- message like "something", "stuff", "project"

Return refine if user is adding more detail but topic unclear.



RULES FOR CHALLENGE

Return confirm if the message looks like a specific technical problem,
even if short.

Examples of confirm:
jwt
token refresh
blacklisting
auth bug
async issue
db lock
permission error
race condition
cache invalidation
login problem
oauth issue

Return suggest if:
- user unsure
- message like "not sure"
- message like "idk"
- message very vague like "problem", "issue", "stuff"

Return refine if user is adding more detail.



RULES FOR LESSON

Apply these rules ONLY if Current step = ASK_LESSON

Return confirm if the message looks like a clear insight,
learning, or takeaway.

Examples of confirm:
state machines make scheduling easier
retry logic needs idempotency
jwt needs blacklist
caching needs invalidation
async code needs locks
always validate tokens
logging is important
race conditions are tricky


Return suggest if:
- user unsure
- user says not sure
- user says idk
- user says dont know
- message is "not sure"
- message is "idk"
- message is "no idea"
- message is "nothing"


Return refine if:
- message vague but not unsure
- message like "learned a lot"
- message like "many things"
- message like "it helped"



Return ONLY one word:

refine
confirm
suggest
"""


def decide_action(state, step, user_message):

    prompt = build_prompt(
        state,
        step,
        user_message,
    )

    result = call_llm(prompt).strip().lower()

    print("DECISION:", result)

    if "confirm" in result:
        return "confirm"

    elif "suggest" in result:
        return "suggest"

    elif "refine" in result:
        return "refine"

    # fallback
    return "refine"