from typing import Dict


def build_summary(state: Dict) -> str:

    return f"""
Here is your post plan:

Topic: {state.get("topic")}
Project: {state.get("project")}
Context: {state.get("context")}

Story: {state.get("story")}

Lesson: {state.get("lesson")}

Angle: {state.get("angle")}

Intent: {state.get("intent")}
Tone: {state.get("tone")}
Audience: {state.get("audience")}


You can edit any field inline. Examples:

Topic: new topic
Story: updated story
Lesson: new lesson
Tone: casual
Audience: founders

Type "generate" to create the post.
"""