import requests

BASE = "https://hacker-news.firebaseio.com/v0"

def get_top_story_ids(limit=30):
    r = requests.get(f"{BASE}/topstories.json", timeout=10)
    r.raise_for_status()
    return r.json()[:limit]

def get_story(story_id):
    r = requests.get(f"{BASE}/item/{story_id}.json", timeout=10)
    r.raise_for_status()
    return r.json()

def fetch_top_stories(limit=30):
    stories = []
    for sid in get_top_story_ids(limit):
        try:
            story = get_story(sid)
            if story and story.get("type") == "story" and story.get("title"):
                stories.append({
                    "id": story["id"],
                    "title": story["title"],
                    "url": story.get("url", ""),
                    "score": story.get("score", 0),
                    "by": story.get("by", ""),
                    "descendants": story.get("descendants", 0),  # comment count
                })
        except requests.RequestException:
            continue  # skip a failed story rather than crash the run
    return stories

if __name__ == "__main__":
    s = fetch_top_stories(5)
    for story in s:
        print(story["score"], story["title"])