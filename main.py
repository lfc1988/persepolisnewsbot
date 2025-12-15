import requests
from bs4 import BeautifulSoup
import os
import time

# تنظیمات عمومی
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
SENT_LINKS_FILE = "sent_links.txt"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}
# کلمات کلیدی
KEYWORDS = ["پرسپولیس", "لنگ"] # بهتر است کلمات کلیدی را اضافه کنید

def load_sent_links():
    """خواندن لینک‌های قبلا ارسال شده از فایل."""
    if not os.path.exists(SENT_LINKS_FILE):
        return set()
    with open(SENT_LINKS_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def save_link(link):
    """ذخیره لینک جدید در فایل."""
    with open(SENT_LINKS_FILE, "a", encoding="utf-8") as f:
        f.write(f"{link}\n")

def simple_summary(title, text, max_len=300):
    """خلاصه‌سازی ساده (برش متن) به جای مدل سنگین."""
    
    # ترکیب تیتر و متن و محدود کردن به حداکثر 300 کاراکتر
    combined_text = f"{title}\n\n{text}"
    if len(combined_text) > max_len:
        return combined_text[:max_len-3] + "..."
    return combined_text

def send_to_telegram(photo_url, caption):
    """ارسال عکس و متن به تلگرام."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    
    data = {
        "chat_id": CHAT_ID,
        "photo": photo_url,
        "caption": caption
    }
    try:
        resp = requests.post(url, data=data, timeout=10)
        resp.raise_for_status() # بررسی خطاهای HTTP
        print(f"Successfully sent post. Status: {resp.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Telegram: {e}")

# --- توابع اسکرپینگ ---

def crawl_site(url, item_selector, title_selector, summary_selector, site_name):
    print(f"Checking {site_name}...")
    try:
        page = requests.get(url, headers=HEADERS, timeout=15)
        page.raise_for_status()
        soup = BeautifulSoup(page.text, "html.parser")
        sent_links = load_sent_links()

        news_list = soup.select(item_selector) 
        
        for item in news_list:
            try:
                # 1. استخراج لینک و عنوان
                link_tag = item.select_one("a")
                if not link_tag or not link_tag.get('href'): continue
                
                href = link_tag['href']
                # ایجاد لینک کامل
                if not href.startswith("http"):
                    base_url = "/".join(url.split("/")[:3]) 
                    full_link = f"{base_url}{href}"
                else:
                    full_link = href
                    
                # بررسی تکراری نبودن
                if full_link in sent_links: continue

                title_tag = item.select_one(title_selector)
                title = title_tag.text.strip() if title_tag else "N/A"
                
                # 2. فیلتر کلمه کلیدی
                if not any(keyword in title for keyword in KEYWORDS): continue
                
                # 3. استخراج متن خلاصه
                summary_tag = item.select_one(summary_selector)
                text = summary_tag.text.strip() if summary_tag else ""
                
                # 4. استخراج عکس
                img_tag = item.select_one("img")
                photo = img_tag.get('src') if img_tag and img_tag.get('src') else None
                if not photo: continue # اگر عکس پیدا نشد، خبر را ارسال نکن

                # 5. خلاصه و بازنویسی ساده
                caption = simple_summary(title, text)
                caption_with_link = f"🔴 {title}\n\n{caption}\n\n🔗 منبع: {site_name}"
                
                # 6. ارسال
                send_to_telegram(photo, caption_with_link)
                save_link(full_link)
                
                time.sleep(1) # وقفه کوتاه بین ارسال‌ها

            except Exception as e:
                print(f"Error processing item in {site_name}: {e}")

    except requests.exceptions.RequestException as e:
        print(f"Connection Error for {site_name}: {e}")

def crawl_all():
    # استفاده از لینک مستقیم تگ برای دقت بیشتر
    
    # 1. ورزش 3
    crawl_site(
        url="https://www.varzesh3.com/news/tag/43/%D9%BE%D8%B1%D8%B3%D9%BE%D9%88%D9%84%DB%8C%D8%B3",
        item_selector=".news-main-list li",
        title_selector=".title",
        summary_selector=".summary",
        site_name="ورزش 3"
    )

    # 2. فوتبال 360
    crawl_site(
        url="https://football360.ir/tag/%D9%BE%D8%B1%D8%B3%D9%BE%D9%88%D9%84%DB%8C%D8%B3",
        item_selector=".item.news-list",
        title_selector="h2 a",
        summary_selector=".item-summary",
        site_name="فوتبال 360"
    )

    # 3. فوتبالی
    crawl_site(
        url="https://www.fotballi.net/tag/%D9%BE%D8%B1%D8%B3%D9%BE%D9%88%D9%84%DB%8C%D8%B3",
        item_selector=".list-item-content",
        title_selector=".item-title a",
        summary_selector=".item-description",
        site_name="فوتبالی"
    )

if __name__ == "__main__":
    crawl_all()
