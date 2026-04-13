import requests
from bs4 import BeautifulSoup
import json, os

KEYWORDS = ["콜업", "승격"]
URL = "https://m.fmkorea.com/index.php?mid=baseball&category=3319438871"
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
    headers = {
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15"
    }
    res = requests.get(URL, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    posts = []
    # 에펨코리아 모바일 게시물 목록
    for item in soup.select("ul.list_ul li"):
        a = item.select_one("a")
        title_el = item.select_one(".li_title, .title, strong")
        if not a or not title_el:
            continue
        title = title_el.get_text(strip=True)
        href = a.get("href", "")
        if not href or not title:
            continue
        posts.append({
            "id": href,
            "title": title,
            "link": "https://m.fmkorea.com" + href if href.startswith("/") else href
        })
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
    print(f"총 {len(posts)}개 게시물 발견")
    for p in posts:
        print(p["title"])

    new_seen = set(seen)
    for post in posts:
        if post["id"] and post["id"] not in seen:
            new_seen.add(post["id"])
            if any(kw in post["title"] for kw in KEYWORDS):
                send_notification(post)
                print(f"알림 전송: {post['title']}")

    save_seen(new_seen)

if __name__ == "__main__":
    main()
