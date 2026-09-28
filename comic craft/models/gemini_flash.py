import json
import os
import re

import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

OUTLINE_PROMPT = """
You are a comic outline writer. Create a 5-panel comic outline based on:
Story: {story_prompt}
Character: {character_name}
Setting: {setting}
Tone: {tone}
Art Style: {art_style}

Return ONLY valid JSON array of 5 objects, each like:
{{"panel": 1, "title": "...", "scene_description": "...", "image_prompt": "detailed visual prompt for {art_style} style, comic panel, {setting}..."}}
No markdown, no explanation.
"""


def _fallback_outline(character_name, setting, story_prompt, tone, art_style):
    return [
        {
            "panel": i + 1,
            "title": f"Chapter {i + 1}: {character_name}'s Journey",
            "scene_description": f"{character_name} in {setting} - {story_prompt} - part {i + 1}",
            "image_prompt": f"{art_style} comic style, {character_name} in {setting}, {tone} mood, {story_prompt}, highly detailed, comic panel",
        }
        for i in range(5)
    ]


def generate_outline(story_prompt, character_name, setting, tone, art_style):
    try:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing")

        model = genai.GenerativeModel("models/gemini-1.5-flash")
        prompt = OUTLINE_PROMPT.format(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )
        response = model.generate_content(prompt)
        text = getattr(response, "text", "")
        if not text:
            raise ValueError("No text returned from Gemini API")

        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.IGNORECASE | re.DOTALL)
        outline = json.loads(cleaned)
        if isinstance(outline, dict):
            outline = outline.get("panels", [])
        if not isinstance(outline, list):
            raise ValueError("Outline response was not a list")
        return outline[:5]
    except Exception as e:
        print(f"Flash Error, using fallback: {e}")
        return _fallback_outline(character_name, setting, story_prompt, tone, art_style)
