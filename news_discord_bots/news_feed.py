import requests
import time

# Replace these with your actual API keys
FINNHUB_API_KEY = "Finnhub key"

DISCORD_WEBHOOK_URL = "webhook"

posted_links = set()  # track posted news URLs globally

def post_to_discord(message: str):
    data = {
        "content": message
    }
    response = requests.post(DISCORD_WEBHOOK_URL, json=data)
    if response.status_code == 204:
        print("Posted to Discord successfully.")
    else:
        print(f"Failed to post to Discord: {response.status_code} {response.text}")


def fetch_finnhub():
    url = "https://finnhub.io/api/v1/news"
    params = {
        "category": "general",  # can be 'general', 'forex', 'crypto', etc.
        "token": FINNHUB_API_KEY
    }
    try:
        res = requests.get(url, params=params)
        res.raise_for_status()
        data = res.json()
        results = []
        for article in data:
            results.append({
                "title": article.get("headline"),
                "link": article.get("url"),
                "source": "Finnhub"
            })
        return results
    except Exception as e:
        print(f"Finnhub error: {e}")
        return []

def main():
    SOURCES = [fetch_finnhub]

    all_news = []
    for source_func in SOURCES:
        news = source_func()
        all_news.extend(news)
        time.sleep(1)

    unique = {}
    for item in all_news:
        key = item['link']
        if key not in unique:
            unique[key] = item

    # Only post news that hasn't been posted before
    new_items = [item for link, item in unique.items() if link not in posted_links]

    # Post new items and add their links to the posted set
    for news_item in new_items:
        message = f"{news_item['title']} ({news_item['link']})"
        post_to_discord(message)
        posted_links.add(news_item['link'])
        time.sleep(1)  # be kind to Discord

if __name__ == "__main__":
    while True:
        main()
        print("Waiting 5 seconds before next update...")
        time.sleep(5)  # sleep for 5 minutes
