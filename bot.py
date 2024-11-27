
import subprocess
import sys

# تابع برای نصب کتابخانه‌ها
def install(package, display_name):
    try:
        print(f"در حال نصب کتابخانه {display_name}...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", package],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True
        )
        print(f"{display_name} با موفقیت نصب شد.")
    except subprocess.CalledProcessError as e:
        print(f"خطا در نصب {display_name}: {e.stderr}")
        sys.exit(1)

# لیست کتابخانه‌ها با نام‌های نصب صحیح و نام‌های نمایشی
required_packages = [
    ("beautifulsoup4", "BeautifulSoup"),
    ("googlesearch-python", "Google Search"),
    ("scrapy", "Scrapy"),
    ("twisted", "Twisted")
]

# بررسی و نصب خودکار کتابخانه‌ها
for package, display_name in required_packages:
    try:
        __import__(package.split('-')[0])  # تلاش برای ایمپورت کتابخانه
        print(f"کتابخانه {display_name} از قبل نصب شده است.")
    except ImportError:
        install(package, display_name)

import os
import random
import rubpy
from rubpy import Client, filters, utils
from rubpy.types import Updates
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import scrapy
from scrapy.crawler import CrawlerRunner
from twisted.internet import defer, reactor
from scrapy.utils.log import configure_logging

# پیکربندی ربات
bot = Client(name='Ai_bot')
guid =[" گوید گپ شما "]
guid_music = "گوید گپ شما"
active_voice_chats = {}
url = 'https://kashoob.com/playlist/9GOj9/%D9%85%D8%AF%D8%A7%D8%AD%DB%8C-%D9%87%D8%A7%DB%8C-%D8%AD%D9%85%D8%A7%D8%B3%DB%8C-%D9%85%D8%A8%D8%A7%D8%B1%D8%B2%D9%87-%D8%A8%D8%A7-%D8%A7%D8%B3%D8%B1%D8%A7%D8%A6%DB%8C%D9%84'

# ارسال درخواست برای دریافت محتوای صفحه
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# پیدا کردن تمامی تگ‌های <div> که ویژگی data-url دارند
audio_links = [div['data-url'] for div in soup.find_all('div', {'data-url': True})]
# جستجو در گوگل و استخراج لینک‌ها
def search_songs(query):
    query = query + " آهنگ"  # اضافه کردن "آهنگ" برای جستجوی بهتر آهنگ‌های ایرانی
    search_results = search(query, num_results=15)
    
    song_links = []
    
    for link in search_results:
        if 'music' in link or 'song' in link:  # فیلتر کردن لینک‌های مرتبط با موسیقی
            song_links.append(link)
    
    return song_links

# کرول کردن صفحه‌ای برای استخراج لینک‌های دانلود
class SongCrawler(scrapy.Spider):
    name = "song_crawler"
    
    def __init__(self, start_urls, *args, **kwargs):
        super(SongCrawler, self).__init__(*args, **kwargs)
        self.start_urls = start_urls
    
    def parse(self, response):
        download_links = []
        # بررسی لینک‌ها برای پیدا کردن لینک‌های دانلود آهنگ
        for link in response.css('a::attr(href)').getall():
            if 'download' in link or '.mp3' in link:
                download_links.append(link)
        
        # ارسال لینک دانلود پیدا شده
        for dl_link in download_links:
            yield {'download_link': dl_link}

# اجرای کرولر با استفاده از CrawlerRunner
def crawl_song_page(urls):
    runner = CrawlerRunner()
    runner.crawl(SongCrawler, start_urls=urls)
    d = runner.join()
    d.addCallback(lambda _: reactor.stop())
# تابع برای دریافت آهنگ بر اساس جستجوی کاربر
def get_response_from_api(user_input):
    url = "https://api.api-code.ir/gpt-4/"
    payload = {"text": user_input}

    try:
        response = requests.get(url, params=payload)
        response.raise_for_status()  # بررسی وضعیت پاسخ
        
        data = response.json()
        return data['result']  # فقط نتیجه را برمی‌گرداند

    except requests.exceptions.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except requests.exceptions.RequestException as req_err:
        return f"Request error occurred: {req_err}"
    except Exception as e:
        return f"An error occurred: {e}"
def get_song(search_text: str):
    try:
        url = f"https://api-free.ir/api/sr-music/?text={search_text}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok") and "result" in data:
                return data["result"]
            else:
                return None
    except Exception as e:
        print(f"Error fetching song: {e}")
        return None

# تابع برای دریافت صدای تبدیل شده از متن
def fetch_audio(text, voice_type):
    try:
        url = f"https://api.api-code.ir/text-to-voice/?text={text}&type={voice_type}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "success":
                audio_url = data["audio"]
                audio_response = requests.get(audio_url)
                if audio_response.status_code == 200:
                    audio_path = f"{voice_type}_{text}.ogg"
                    with open(audio_path, "wb") as audio_file:
                        audio_file.write(audio_response.content)
                    return audio_path
    except Exception as e:
        print(f"Error fetching audio: {e}")
    return None

# تابع برای دریافت لینک آهنگ تصادفی
def get_random_music_link():
    try:
        api_url = "https://api-free.ir/api/music/"
        response = requests.get(api_url)
        if response.status_code == 200:
            data = response.json()
            if data.get("ok") and data.get("result") and data["result"].get("song"):
                return data["result"]["song"]
    except Exception as e:
        print(f"Error fetching random song: {e}")
    return None
global_status = True  # وضعیت کلی ربات
owners="u0Guh3f0531236db71d8fd20e938bc5a"
# تابع مدیریت پیام‌ها
def check_status():
    if not global_status:
        return False
    return True
async def manage_voice_chat(action: str, group_guid: str, user_guid: str, update: Updates):
    """
    مدیریت ویس چت (ایجاد یا خروج).
    
    Args:
        action (str): "start" برای ایجاد یا "leave" برای خروج.
        group_guid (str): آیدی گروه.
        user_guid (str): آیدی کاربر ارسال‌کننده دستور.
        update (Updates): آبجکت آپدیت برای ارسال پیام پاسخ.
    """
    try:
        # اطمینان از اینکه کاربر مدیر است
        if not await update.is_admin(user_guid=user_guid):
            await update.reply("❗ شما دسترسی لازم برای این عملیات را ندارید.")
            return
        
        if action == "start":
            # ایجاد ویس چت
            result = await bot.create_group_voice_chat(group_guid=group_guid)
            voice_chat_id = result["group_voice_chat_update"]["voice_chat_id"]
            
            # ذخیره آیدی ویس چت
            active_voice_chats[group_guid] = voice_chat_id
            await update.reply("🎙 ویس چت با موفقیت ایجاد شد.")
        
        elif action == "leave":
            # بررسی وجود ویس چت فعال
            voice_chat_id = active_voice_chats.get(group_guid)
            if not voice_chat_id:
                await update.reply("❗ ویس چت فعالی برای خروج یافت نشد.")
                # await bot.discard_channel_voice_chat(group_guid,voice_chat_id)
                return
            
            # خروج از ویس چت
            await bot.leave_group_voice_chat(group_guid=group_guid, voice_chat_id=voice_chat_id)
            await update.reply("🔇 ویس چت با موفقیت قطع شد.")
        
            
            # حذف آیدی ویس چت از دیکشنری
            del active_voice_chats[group_guid]
        
        else:
            await update.reply("❗ دستور نامعتبر. لطفاً از دستورات صحیح استفاده کنید.")
    
    except Exception as e:
        await update.reply(f"❗ خطایی رخ داده است: {e}")

# دستور برای ایجاد ویس چت
@bot.on_message_updates(filters.text ,filters.is_group, filters.Commands(['CALL', 'call', 'کال']))
async def start_voice_chat(update: Updates):
    group = update.object_guid
    if group:
        await manage_voice_chat(action="start", group_guid=group, user_guid=update.author_guid, update=update)

# دستور برای خروج از ویس چت
@bot.on_message_updates(filters.text ,filters.is_group, filters.Commands(['leave']))
async def leave_voice_chat(update: Updates):
    group = update.object_guid
    if group:
        await manage_voice_chat(action="leave", group_guid=group, user_guid=update.author_guid, update=update)

@bot.on_message_updates(filters.is_group)
async def toggle_status(update: Updates):
    global global_status
    if update.author_guid and update.author_guid in owners:
        # ادامه کد شما

        
    # بررسی دستورات "فعال" و "خاموش"
        if update.text == "فعال":
            global_status = True
            await update.reply("ربات اکنون فعال است.")
        elif update.text == "خاموش":
            global_status = False
            await update.reply("ربات خاموش شد و دیگر به دستورات پاسخ نمی‌دهد.")
# پردازش دستورات و رویدادهای مختلف
@bot.on_message_updates(filters.Commands(["start"]),filters.is_group)
async def start_bot(update: Updates):
    if not check_status():
        return
    
    await update.reply("سلام! ربات موزیکال با موفقیت فعال شد. لطفاً برای مشاهده دستورات، به کانال زیر مراجعه فرمایید:\n@Music_call_mirbot")

    
    
@bot.on_message_updates(filters.Commands(["play"]),filters.is_group)
async def play_random_song(update: Updates):
    if not check_status():
        return
    await update.reply("درحال پردازش درخواست شما هستم لطفا صبرکنید...")
    song_url = get_random_music_link()
    if song_url:
        await bot.voice_chat_player(guid_music, song_url)
        await update.reply("آهنگ تصادفی به ویسکال ارسال شد!")
    else:
        await update.reply("مشکلی در دریافت آهنگ تصادفی پیش آمده است.")

@bot.on_message_updates(filters.Commands(["music"]),filters.is_group)
async def play_searched_song(update: Updates):
    if not check_status():
        return
    await update.reply("درحال پردازش درخواست شما هستم لطفا صبرکنید...")
    search_text = " ".join(update.text.split()[1:])  # دریافت متن جستجو
    song_url = get_song(search_text)
    if song_url:
        await bot.voice_chat_player(guid_music, song_url)
        await update.reply(f"آهنگ «{search_text}» به ویسکال ارسال شد!")
    else:
        await update.reply("آهنگی با این مشخصات یافت نشد.")

@bot.on_message_updates(filters.Commands(["reply_music"]),filters.is_group)
async def reply_random_song(update: Updates):
    if not check_status():
        return
    await update.reply("درحال پردازش درخواست شما هستم لطفا صبرکنید...")
    song_url = get_random_music_link()
    if song_url:
        await update.reply(f"🎶 اینم یک آهنگ تصادفی:\n{song_url}")
        await update.reply_music(song_url,caption=f"🎶 اینم یک آهنگ تصادفی:\n{song_url}")
    else:
        await update.reply("متاسفانه آهنگ تصادفی پیدا نشد.")

@bot.on_message_updates(filters.Commands(["mard"]),filters.is_group)
async def reply_male_voice(update: Updates):
    if not check_status():
        return
    await update.reply("درحال پردازش درخواست شما هستم لطفا صبرکنید...")
    text = " ".join(update.text.split()[1:])  # دریافت متن
    audio_path = fetch_audio(text, "male")
    if audio_path:
        await update.reply_voice(audio_path,caption="ویس شما اماده شد")
        os.remove(audio_path)  # حذف فایل بعد از ارسال
    else:
        await update.reply("مشکلی در تبدیل متن به صدا پیش آمده است.")

@bot.on_message_updates(filters.Commands(["zan"]),filters.is_group)
async def reply_female_voice(update: Updates):
    
    if not check_status():
        return
    await update.reply("درحال پردازش درخواست شما هستم لطفا صبرکنید...")
    text = " ".join(update.text.split()[1:])  # دریافت متن
    audio_path = fetch_audio(text, "female")
    if audio_path:
        await update.reply_voice(audio_path,caption="ویس شما اماده شد")
        os.remove(audio_path)  # حذف فایل بعد از ارسال
    else:
        await update.reply("مشکلی در تبدیل متن به صدا پیش آمده است.")

# لغو پخش موسیقی
@bot.on_message_updates(filters.Commands(["cancel"]),filters.is_group)
async def cancel_playback(update: Updates):
    if not check_status():
        return
    try:
        file_bisda="bisda.mp3"
        
        await bot.voice_chat_player(guid_music,file_bisda)
        await update.reply("اهنگ متوقف شد")
    except Exception as er:
        await update.reply(er)
   
       
        

   


@bot.on_message_updates(filters.music,filters.is_group)
async def handle_music_(update: Updates):
    
    
    if not check_status():
        return
    await update.reply("دریافت شد")
    # دانلود و ذخیره موزیک
    file_path = await update.download(save_as="downloaded_music.mp3")
    await update.reply("موزیک شما دانلود و به ویسکال ارسال شد")
    
    # ارسال موزیک به چت
    with open("downloaded_music.mp3","rb") as m :
        # await bot.send_music(guid,'downloaded_music.mp3')
        await bot.voice_chat_player(guid,'downloaded_music.mp3')
@bot.on_message_updates(filters.Commands(["help"]),filters.is_group)
async def help_bot(update: Updates):
    if not check_status():
        return
    
    
    await update.reply("سلام! ربات موزیکال با موفقیت فعال شد. لطفاً برای مشاهده دستورات، به کانال زیر مراجعه فرمایید:\n@Music_call_mirbot")



    
   
        


    
@bot.on_message_updates(filters.is_group)
async def send_crawl_song_page(update: Updates):
    if not check_status():
        return
    
    query = update.text.replace("/موسیقی", "").strip()
    if update.text.startswith("/موسیقی"):
        await update.reply("درحال پردازش و جستجو هستم، لطفاً صبر کنید...")
    
        # جستجوی لینک‌های آهنگ
        song_links = search_songs(query)
        
        if song_links:
            # انتخاب تصادفی یک لینک
            random_link = random.choice(song_links)
            
            # کرول کردن لینک انتخابی برای دریافت لینک دانلود
            download_links = await get_download_links(random_link)
            
            if download_links:
                # انتخاب تصادفی از بین لینک‌های دانلود پیدا شده
                random_download_link = random.choice(download_links)
                
                # ارسال آهنگ تصادفی به ویس چت
                await bot.voice_chat_player(guid_music, random_download_link)
                await update.reply(f"🎶 آهنگ پیدا شد و به ویس چت ارسال شد:\n{random_download_link}")
            else:
                await update.reply(f"❗ برای آهنگ '{query}' هیچ لینک دانلودی پیدا نشد.")
        else:
            await update.reply(f"❗ هیچ آهنگی برای '{query}' پیدا نشد.")

# دریافت لینک‌های دانلود مستقیم آهنگ (مثلاً لینک mp3)
async def get_download_links(link):
    # کرول کردن صفحه برای پیدا کردن لینک‌های دانلود
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        download_links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if '.mp3' in href:  # بررسی اینکه آیا لینک دانلود mp3 است
                if not href.startswith('http'):
                    href = link + href  # اگر لینک نسبی است، آن را کامل کنیم
                download_links.append(href)
        
        return download_links
    except Exception as e:
        print(f"Error during crawling: {e}")
        return []


@bot.on_message_updates(filters.is_group)
async def send_crawl_song_page(update: Updates):
    if not check_status():
        return
    
    query = update.text.replace("/ارسال", "").strip()
    if update.text.startswith("/ارسال"):
        await update.reply("درحال پردازش و جستجو هستم، لطفاً صبر کنید...")
    
        # جستجوی لینک‌های آهنگ
        song_links = search_songs(query)
        
        if song_links:
            # انتخاب تصادفی یک لینک
            random_link = random.choice(song_links)
            
            # کرول کردن لینک انتخابی برای دریافت لینک دانلود
            download_links = await get_download_links(random_link)
            
            if download_links:
                # انتخاب تصادفی از بین لینک‌های دانلود پیدا شده
                random_download_link = random.choice(download_links)
                
                # ارسال آهنگ تصادفی به ویس چت
                await update.reply_music(random_download_link,caption="اهنگ شما حاضرشد")
                await update.reply(f"🎶 آهنگ پیدا شد و به ویس چت ارسال شد:\n{random_download_link}")
            else:
                await update.reply(f"❗ برای آهنگ '{query}' هیچ لینک دانلودی پیدا نشد.")
        else:
            await update.reply(f"❗ هیچ آهنگی برای '{query}' پیدا نشد.")

# دریافت لینک‌های دانلود مستقیم آهنگ (مثلاً لینک mp3)
async def get_download_links(link):
    # کرول کردن صفحه برای پیدا کردن لینک‌های دانلود
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        download_links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            if '.mp3' in href:  # بررسی اینکه آیا لینک دانلود mp3 است
                if not href.startswith('http'):
                    href = link + href  # اگر لینک نسبی است، آن را کامل کنیم
                download_links.append(href)
        
        return download_links
    except Exception as e:
        print(f"Error during crawling: {e}")
        return []

@bot.on_message_updates(filters.is_group,filters.Commands(['مداحی']))
async def send_random_audio(update: Updates):
    if not check_status():
        return
    await update.reply("درحال پردازش هستم به زودی درویسکال اجرا میشه ..")
    # اگر لینک‌ها موجود باشند
    if audio_links:
        # انتخاب یک لینک رندم از لیست
        audio_url = random.choice(audio_links)

        # ارسال لینک صوتی به چت
        await bot.voice_chat_player(guid_music,audio_url)
    else:
        await update.reply('هیچ فایل صوتی پیدا نشد.')
# اجرای ربات
bot.run()

