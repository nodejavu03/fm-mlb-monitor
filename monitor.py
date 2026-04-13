

import requests
from bs4 import BeautifulSoup
import json, os

KEYWORDS = ["콜업", "승격"]
URL = "https://www.fmkorea.com/baseball"   # MLB 게시판 URL로 변경 필요
NTFY_TOPIC = os.environ["NTFY_TOPIC"]
STATE_FILE = "seen_posts.json"

def load_seen():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(STATE_FILE, "w") as f:
        json.dump(list(seen), f)

def fetch_posts():
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(URL, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    posts = []
    for a in soup.select("ul.bd_lst li .title a"):
        title = a.get_text(strip=True)
        href = a.get("href", "")
        posts.append({"id": href, "title": title, "link": "https://www.fmkorea.com" + href})
    return posts

def send_notification(post):
    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        headers={
            "Title": "⚾ 에펨 MLB 알림",
            "Content-Type": "text/plain; charset=utf-8",
            "Click": post["link"]
        },
        data=post["title"].encode("utf-8")
    )

def main():
    seen = load_seen()
    posts = fetch_posts()
    new_seen = set(seen)

    for post in posts:
        if post["id"] and post["id"] not in seen:
            new_seen.add(post["id"])
            if any(kw in post["title"] for kw in KEYWORDS):
                send_notification(post)

    save_seen(new_seen)

if __name__ == "__main__":
    main()
