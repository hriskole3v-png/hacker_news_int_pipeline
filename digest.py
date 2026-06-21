from datetime import datetime
from fetch import fetch_top_stories
from summarise import summarise_story

from concurrent.futures import ThreadPoolExecutor

TECH_TOPICS = {"AI", "Security", "Software", "Hardware"}

def build_digest(limit=10):
    stories = fetch_top_stories(limit)

    def enrich(s):
        return {**s, **summarise_story(s["title"])}

    with ThreadPoolExecutor(max_workers=5) as ex:
        entries = list(ex.map(enrich, stories))

    tech = [e for e in entries if e["topic"] in TECH_TOPICS]
    other = [e for e in entries if e["topic"] not in TECH_TOPICS]
    return tech, other

def synthesise_themes(entries):
    """One LLM call over all summaries to surface cross-story trends."""
    if not entries:
        return ""
    from summarise import client, MODEL
    titles = "\n".join(f"- {e['title']} ({e['topic']})" for e in entries)
    prompt = f"""You are a tech analyst. Below are today's top tech stories.
In 2-3 sentences, identify the dominant themes or trends across them.
Be specific and insightful, not generic. Write for a busy product and engineering team.

Stories:
{titles}
"""
    try:
        resp = client.models.generate_content(model=MODEL, contents=prompt)
        return resp.text.strip()
    except Exception:
        return ""

def render_markdown(tech, other, themes=""):
    date = datetime.now().strftime("%d %B %Y")
    lines = [f"# Hacker News Tech Digest — {date}\n",
             f"_{len(tech)} tech stories, plus {len(other)} also trending._\n"]

    if themes:
        lines.append(f"\n## Today's Themes\n\n{themes}\n")

    # group tech stories by topic
    by_topic = {}
    for e in tech:
        by_topic.setdefault(e["topic"], []).append(e)

    for topic, items in sorted(by_topic.items()):
        lines.append(f"\n## {topic} ({len(items)})\n")
        for e in items:
            lines.append(f"### {e['title']}")
            lines.append(f"- {e['summary']}")
            lines.append(f"- **Why it matters:** {e['why_it_matters']}")
            lines.append(f"- Score: {e['score']} | [Discussion](https://news.ycombinator.com/item?id={e['id']})\n")

    if other:
        lines.append("\n## Also trending (non-tech)\n")
        for e in other:
            lines.append(f"- **{e['title']}** — {e['summary']} _(Score: {e['score']})_\n")

    return "\n".join(lines)

def render_html(tech, other, themes=""):
    date = datetime.now().strftime("%d %B %Y")
    css = """<style>
    body{font-family:'Segoe UI',Arial,sans-serif;max-width:760px;margin:40px auto;padding:0 20px;color:#1a2b5e;line-height:1.5}
    h1{border-bottom:3px solid #2e6be6;padding-bottom:8px}
    h2{color:#2e6be6;margin-top:32px}
    h3{margin-bottom:4px}
    .themes{background:#f2f6ff;border-left:4px solid #2e6be6;padding:14px 18px;border-radius:6px}
    .why{color:#333}.meta{color:#888;font-size:13px}
    .other{color:#444;font-size:14px}
    a{color:#2e6be6;text-decoration:none}
    </style>"""
    html = [f"<!DOCTYPE html><html><head><meta charset='utf-8'>{css}</head><body>"]
    html.append(f"<h1>Hacker News Tech Digest</h1><p class='meta'>{date} &middot; {len(tech)} tech stories</p>")

    if themes:
        html.append(f"<div class='themes'><strong>Today's Themes</strong><br>{themes}</div>")

    by_topic = {}
    for e in tech:
        by_topic.setdefault(e["topic"], []).append(e)

    for topic, items in sorted(by_topic.items()):
        html.append(f"<h2>{topic} ({len(items)})</h2>")
        for e in items:
            html.append(f"<h3>{e['title']}</h3>")
            html.append(f"<p>{e['summary']}</p>")
            html.append(f"<p class='why'><strong>Why it matters:</strong> {e['why_it_matters']}</p>")
            html.append(f"<p class='meta'>Score: {e['score']} &middot; <a href='https://news.ycombinator.com/item?id={e['id']}'>Discussion</a></p>")

    if other:
        html.append("<h2>Also trending (non-tech)</h2>")
        for e in other:
            html.append(f"<p class='other'><strong>{e['title']}</strong> — {e['summary']} <em>(Score: {e['score']})</em></p>")

    html.append("</body></html>")
    return "\n".join(html)


if __name__ == "__main__":
    tech, other = build_digest(10)
    themes = synthesise_themes(tech)
    md = render_markdown(tech, other, themes)
    with open("digest.md", "w", encoding="utf-8") as f:
        f.write(md)
    print(md)
    print("\n--- saved to digest.md ---")