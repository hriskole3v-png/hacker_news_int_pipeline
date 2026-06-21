import argparse
from notify import send_digest_email
from digest import build_digest, render_markdown, synthesise_themes, render_html

def main():
    parser = argparse.ArgumentParser(description="Hacker News tech digest agent")
    parser.add_argument("--limit", type=int, default=15, help="number of top stories")
    parser.add_argument("--out", type=str, default="digest.md", help="output file")
    args = parser.parse_args()

    print(f"Fetching and summarising top {args.limit} Hacker News stories...")
    tech, other = build_digest(args.limit)
    themes = synthesise_themes(tech)
    md = render_markdown(tech, other, themes)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Digest saved to {args.out} ({len(tech)} tech, {len(other)} other)")

    html = render_html(tech, other, themes)
    with open("digest.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("HTML digest saved to digest.html")

    send_digest_email(md)

if __name__ == "__main__":
    main()