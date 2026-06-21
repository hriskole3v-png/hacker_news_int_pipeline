import os
import json
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-2.5-flash"

ALLOWED_TOPICS = {"AI", "Security", "Software", "Hardware", "Business", "Science", "Other"}

PROMPT = """You are a tech analyst writing for a busy product and engineering team.
Given a Hacker News story title, write a concise digest entry.

Return ONLY valid JSON, no markdown, with this exact shape:
{{
  "summary": "2-3 sentence summary of what the story is about",
  "why_it_matters": "1 sentence on the trend or why the team should care",
  "topic": "one of: AI, Security, Software, Hardware, Business, Science, Other"
}}

Story title: {title}
"""

def summarise_story(title):
    try:
        resp = client.models.generate_content(
            model=MODEL,
            contents=PROMPT.format(title=title),
        )
        text = resp.text.strip()
        if text.startswith("```"):
            text = text.split("```")[1].replace("json", "", 1).strip()
        data = json.loads(text)
        if not all(k in data for k in ("summary", "why_it_matters", "topic")):
            raise ValueError("missing keys")
        # snap any unexpected topic to a safe default
        if data["topic"] not in ALLOWED_TOPICS:
            data["topic"] = "Other"
        return data
    except Exception:
        return {
            "summary": title,
            "why_it_matters": "Could not generate summary.",
            "topic": "Other",
        }

if __name__ == "__main__":
    print(json.dumps(summarise_story("AI agent runs amok in Fedora and elsewhere"), indent=2))