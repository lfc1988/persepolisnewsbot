import requests
from bs4 import BeautifulSoup
import schedule
import time
import os
from transformers import pipeline

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def send_to_telegram(photo_url, caption):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    data = {
        "chat_id": CHAT_ID,
        "photo": photo_url,
        "caption": caption
    }
    requests.post(url, data=data)

def rewrite_and_summarize(text, max_len=500):
    try:
        summary = summarizer(text, max_length=120, min_length=30, do_sample=False)
        result = summary[0]['summary_text']
        return result[:max_len]
    except Exception:
        return text[:max_len]

def crawl_varzesh3():
    url = "https://www.varzesh3.com"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    for item in soup.select(".news-item"):
        title = item.select_one("h2").text.strip()
        if "پرسپولیس" in title:
            photo = item.select_one("img")["src"]
            text = item.select_one(".summary").text.strip()
            caption = rewrite_and_summarize(f"{title} - {text}")
            send_to_telegram(photo, caption)

def crawl_football360():
    url = "https://football360.ir"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    for item in soup.select(".news-item"):
        title = item.select_one("h2").text.strip()
        if "پرسپولیس" in title:
            photo = item.select_one("img")["src"]
            text = item.select_one(".summary").text.strip()
            caption = rewrite_and_summarize(f"{title} - {text}")
            send_to_telegram(photo, caption)

def crawl_fotballi():
    url = "https://www.fotballi.net"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    for item in soup.select(".news-item"):
        title = item.select_one("h2").text.strip()
        if "پرسپولیس" in title:
            photo = item.select_one("img")["src"]
            text = item.select_one(".summary").text.strip()
            caption = rewrite_and_summarize(f"{title} - {text}")
            send_to_telegram(photo, caption)

def crawl_all():
    crawl_varzesh3()
    crawl_football360()
    crawl_fotballi()

schedule.every(15).minutes.do(crawl_all)

while True:
    schedule.run_pending()
    time.sleep(1)
