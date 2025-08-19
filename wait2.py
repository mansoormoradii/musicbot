#@RubikaBots
import time
from datetime import datetime
from pyrubi import Client
from pyrubi.types import Message

bot = Client("bot")

# تنظیمات
MESSAGE_LIMIT = 5  # حد مجاز پیام‌ها در یک دقیقه
BLOCK_TIME = 300   # زمان مسدود شدن کاربر (به ثانیه)

# دیکشنری‌ها برای مدیریت کاربران مسدود شده و پیام‌های اخیر
blocked_users = {}
last_messages = {}

@bot.on_message()
def handle_message(message: Message):
    m = message  

    # بررسی اینکه آیا کاربر مسدود شده است
    if m.author_guid in blocked_users:
        if time.time() < blocked_users[m.author_guid]:
            return  # اگر کاربر هنوز مسدود است، هیچ کاری انجام نده
        else:
            del blocked_users[m.author_guid]  # اگر زمان بلاک تمام شده، کاربر را آزاد کن

    # ثبت زمان پیام جدید
    if m.author_guid in last_messages:
        last_messages[m.author_guid].append(time.time())
    else:
        last_messages[m.author_guid] = [time.time()]

    # حذف پیام‌های قدیمی‌تر از یک دقیقه
    last_messages[m.author_guid] = [t for t in last_messages[m.author_guid] if t > time.time() - 60]

    # بررسی تعداد پیام‌ها و مسدود کردن کاربر در صورت نیاز
    if len(last_messages[m.author_guid]) > MESSAGE_LIMIT:
        blocked_users[m.author_guid] = time.time() + BLOCK_TIME
        m.reply("**کاربر عزیز، برای ارسال پیام مکرر از ربات محروم می‌شوید.**")
        return

    # دریافت تاریخ و زمان فعلی
    current_time = datetime.now().strftime("%H:%M")
    current_date = datetime.now().strftime("%Y-%m-%d")

    # پاسخ به پیام با تاریخ و زمان
    response = f"**کاربر عزیز، پیام شما \n ⏰ Time :  {current_time}\n 📆 Date :  {current_date}\nارسال شد ، بزودی جواب شما را میدهیم.✅**\n @@📣channel click@@(https://rubika.ir/@mutherapysic)"
    time.sleep(5)
    

    # ارسال پاسخ نهایی
    message.reply(response)

# شروع
bot.run()