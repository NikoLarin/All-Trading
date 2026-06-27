import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

DISCORD_WEBHOOK_URL = "discord webhook"
RSS_FEED_URL = "https://www.myfxbook.com/rss/forex-economic-calendar-events"

sent_titles = set()

def is_us_event(entry):
    return "united-states" in entry.link.lower() or "usd" in entry.title.lower()

def is_high_impact(description_html):
    soup = BeautifulSoup(description_html, "html.parser")
    span = soup.find("span", class_="sprite-high-impact")
    return span is not None


from email.utils import parsedate_to_datetime

def convert_to_eastern(entry):
    try:
        # Use built-in parser that respects timezones
        utc_time = parsedate_to_datetime(entry.published)
        if utc_time.tzinfo is None:
            utc_time = utc_time.replace(tzinfo=pytz.utc)

        eastern = pytz.timezone("US/Eastern")
        local_time = utc_time.astimezone(eastern)
        return local_time.strftime("%Y-%m-%d %I:%M %p %Z")
    except Exception as e:
        print(f"Time conversion failed: {e}")
        return entry.published

def fetch_and_post():
    feed = feedparser.parse(RSS_FEED_URL)
    mentioned_everyone = False  # Only mention @everyone once per run

    for entry in feed.entries:
        if entry.title in sent_titles:
            continue
        if not is_us_event(entry):
            continue
        if not is_high_impact(entry.description):
            continue

        sent_titles.add(entry.title)
        local_time = convert_to_eastern(entry)

        # Mention @everyone only for the first high-impact message
        if not mentioned_everyone:
            message_prefix = "@everyone\n"
            mentioned_everyone = True
        else:
            message_prefix = ""
        
        
        event_title = entry.title
        event_url = entry.link

        message = f"""{message_prefix}🇺🇸 High-Impact News Alert
        **Event:** **{event_title}**
        **Time:** 🕒 {local_time}
        🔗 View Details: <{event_url}>

        """

        payload = {"content": message}
        response = requests.post(DISCORD_WEBHOOK_URL, json=payload)

        if response.status_code != 204:
            print(f"Failed to post: {response.status_code} - {response.text}")

if __name__ == "__main__":
    fetch_and_post()
