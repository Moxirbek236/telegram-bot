import json
import os


def save_user(user):
    file_path = 'users.json'
    users = []
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read().strip()
                if content:
                    users = json.loads(content)
    except Exception as e:
        print(f"[XATO] users.json o‘qishda muammo: {e}")
        users = []

    if not any(u['id'] == user.id for u in users):
        users.append({
            'id': user.id,
            'username': user.username or '',
            'first_name': user.first_name or '',
            'language_code': user.language_code or ''
        })

        try:
            with open(file_path, 'w') as f:
                json.dump(users, f, indent=2)
            print(
                f"✅ Yangi foydalanuvchi qo‘shildi: {user.username or user.first_name}"
            )
        except Exception as e:
            print(f"[XATO] users.json yozishda muammo: {e}")


import datetime
import pytz
import schedule
import time
import requests
import sys
import random
import asyncio
from telegram import Bot, Update
from telegram.ext import (ApplicationBuilder, MessageHandler, CommandHandler,
                          CallbackContext, filters)
from keep_alive import keep_alive

keep_alive()

# === Sozlamalar ===
TOKEN = '7818484616:AAG6UZLNbKi4Cm5SDJloF-FOhOtmIBeRWtM'
CHAT_ID = '@Tongi_Salomlar_2025'
OWM_API_KEY = '57e2dc54a5dfd435e2bb7586af756faf'
WEATHER_URL = 'http://api.openweathermap.org/data/2.5/weather'
bot = Bot(token=TOKEN)

# === Tavsif tarjimalari ===
UZ_TRANSLATIONS = {
    "clear sky": "ochiq osmon",
    "few clouds": "ozgina bulutli",
    "scattered clouds": "tarqalgan bulutlar",
    "broken clouds": "yoriq bulutlar",
    "overcast clouds": "qorong'u bulutli",
    "shower rain": "kuchli yomg'ir",
    "rain": "yomg'ir",
    "moderate rain": "o‘rtacha yomg‘ir",
    "light rain": "yengil yomg'ir",
    "heavy intensity rain": "kuchli yomg‘ir",
    "thunderstorm": "chaqmoq",
    "snow": "qor",
    "mist": "tuman",
    "haze": "xira havo",
    "fog": "tuman",
    "smoke": "tutun",
}

kun_salomlari = {
    "Monday":
    "🌄 Hayrli tong, muborak Dushanba!\nBugun yangi hafta – yangi imkoniyatlar bilan boshlanmoqda. Har bir qadamda Allohning madadi siz bilan bo‘lsin. Niyatlaringiz yorug‘, yo‘llaringiz ochiq, kuningiz esa sermahsul va barakali o‘tsin!\n\n\n\nHurmat bilan https://t.me/Tongi_Salomlar_2025 !!!, biz sizni yahshi ko'ramiz!\nSog' salomat bo'ling!!!",
    "Tuesday":
    "🌅 Hayrli tong, qadrli Seshanba!\nQuyosh ufqdan chiqqani kabi, sizning ham qalbingizga nur yog‘ilsin! Yaratgan bugun sizga kuch, sabr, va ezgu ishlar yo‘lida qulaylik ato etsin. Har ishda fayz va baraka bo‘lsin!\n\n\n\nHurmat bilan https://t.me/Tongi_Salomlar_2025 !!!, biz sizni yahshi ko'ramiz!\nSog' salomat bo'ling!!!",
    "Wednesday":
    "🌞 Hayrli tong, barakali Chorshanba!\nBugun hayotingizda xotirjamlik, yuragingizda osoyishtalik, ishingizda esa omad hamroh bo‘lsin. Saharning tiniq havosi, tanangizga kuch, qalbingizga esa zavq bersin!\n\n\n\nHurmat bilan https://t.me/Tongi_Salomlar_2025 !!!, biz sizni yahshi ko'ramiz!\nSog' salomat bo'ling!!!",
    "Thursday":
    "🌸 Hayrli tong, aziz Payshanba!\nSokin tongda tilagan duolaringiz qabul bo‘lsin. Bugun sizga ezgulik, kuch-g‘ayrat, mehr-oqibat, va eng asosiysi – baxt olib kelsin. Orzular sari harakatli qadamlar bilan boshlang!\n\n\n\nHurmat bilan https://t.me/Tongi_Salomlar_2025 !!!, biz sizni yahshi ko'ramiz!\nSog' salomat bo'ling!!!",
    "Friday":
    "🕌 Juma muborak, hayrli tong!\nBu muborak tong sizga Allohning rahmatini, barakasini olib kelsin. Bugungi ibodatlaringiz, niyatlaringiz qabul, yuragingiz halovatda bo‘lsin. Har tongdan bugungisi ham go‘zal bo‘lsin!\n\n\n\nHurmat bilan https://t.me/Tongi_Salomlar_2025 !!!, biz sizni yahshi ko'ramiz!\nSog' salomat bo'ling!!!",
    "Saturday":
    "🌼 Hayrli tong, totli Shanba!\nBugun sizni oilangiz quvonch bilan kutmoqda, yuragingiz esa tinchlik bilan to‘lsin. Hozirgi osoyishtalikni qadrlang, yaqinlaringiz bilan vaqtni go‘zal o‘tkazing. Bugun dam oling, yuragingizni quvontiring!\n\n\n\nHurmat bilan https://t.me/Tongi_Salomlar_2025 !!!, biz sizni yahshi ko'ramiz!\nSog' salomat bo'ling!!!",
    "Sunday":
    "🌤 Hayrli tong, quvonchli Yakshanba!\nBu kun sizga orom, ichki quvvat, yaqinlar bilan suhbatu dam olish olib kelsin. Tongdagi quyosh nuri qalbingizni ham yoritib, sizga yangi haftaga kuch bersin!\n\n\n\nHurmat bilan https://t.me/Tongi_Salomlar_2025 !!!, biz sizni yahshi ko'ramiz!\nSog' salomat bo'ling!!!"
}

kech_salomlari = [
    "🌙 Hayrli tun, aziz inson!\nBugungi kuningiz bardavom bo‘lib o‘tgan bo‘lsa, shukr qiling. Endi esa tanaffus va osoyishtalik vaqti. Tuningiz tinch, uyqungiz oromli bo‘lsin!\n\n\n\nHurmat bilan https://t.me/Tongi_Salomlar_2025 !!!, biz sizni yahshi ko'ramiz!\nSog' salomat bo'ling!!!",
    "💫 Dam oling, bugungi mehnatingiz beqiyos edi.\nEndi esa rohatlaning va ajoyib tushlar og‘ushida yoting. Ertaga yangi kuch, yangi imkoniyatlar kutmoqda. Hayrli tun!\n\n\n\nHurmat bilan https://t.me/Tongi_Salomlar_2025 !!!, biz sizni yahshi ko'ramiz!\nSog' salomat bo'ling!!!",
    "🌌 Yulduzlar charog‘on, tun esa sokin.\nShunday betakror kechada qalbingizda tinchlik, yuzingizda esa tabassum bo‘lsin. Har bir orzuingiz yulduzdek porlasin!\n\n\n\nHurmat bilan https://t.me/Tongi_Salomlar_2025 !!!, biz sizni yahshi ko'ramiz!\nSog' salomat bo'ling!!!",
    "🛌 Tanaffus vaqti keldi. Yaxshi tunlar!\nBugun qanday bo‘lgan bo‘lsa ham, ertaga yangi sahifa kutmoqda. Oromli dam oling, ertangi kunga quvvat bilan chiqing!\n\n\n\nHurmat bilan https://t.me/Tongi_Salomlar_2025 !!!, biz sizni yahshi ko'ramiz!\nSog' salomat bo'ling!!!",
    "📋 Kun yakuni – xotirjamlik bilan yakunlansin.\nEndi fikrlarni bir chetga surib, qalbingizni osoyishtaga topshiring. Tushlaringiz yorug‘, qalbingiz esa yengil bo‘lsin. Hayrli tun!\n\n\n\nHurmat bilan https://t.me/Tongi_Salomlar_2025 !!!, biz sizni yahshi ko'ramiz!\nSog' salomat bo'ling!!!"
]


def get_image_url_by_weather(icon, vaqt_turi='kun'):
    kun_rasmlari = {
        'clear':
        'https://images.pexels.com/photos/417173/pexels-photo-417173.jpeg',
        'clouds':
        'https://images.pexels.com/photos/158163/clouds-cloudporn-weather-lookup-158163.jpeg',
        'rain':
        'https://images.pexels.com/photos/459451/pexels-photo-459451.jpeg',
        'snow':
        'https://images.pexels.com/photos/417173/pexels-photo-417173.jpeg',
        'thunderstorm':
        'https://images.pexels.com/photos/167755/pexels-photo-167755.jpeg',
        'mist':
        'https://images.pexels.com/photos/4827/nature-forest-trees-fog.jpeg',
    }

    tun_rasmlari = {
        'clear':
        'https://images.pexels.com/photos/417173/pexels-photo-417173.jpeg',
        'clouds':
        'https://images.pexels.com/photos/158163/clouds-cloudporn-weather-lookup-158163.jpeg',
        'rain':
        'https://images.pexels.com/photos/459451/pexels-photo-459451.jpeg',
        'snow':
        'https://images.pexels.com/photos/417173/pexels-photo-417173.jpeg',
        'thunderstorm':
        'https://images.pexels.com/photos/167755/pexels-photo-167755.jpeg',
        'mist':
        'https://images.pexels.com/photos/4827/nature-forest-trees-fog.jpeg',
    }

    rasmlar = tun_rasmlari if vaqt_turi == 'tun' else kun_rasmlari
    return rasmlar.get(icon, kun_rasmlari['clear'])


def log_yoz(matn):
    sana = datetime.datetime.now(
        pytz.timezone("Asia/Tashkent")).strftime('%Y-%m-%d %H:%M:%S')
    print(f"[{sana}] {matn}")


def vaqt_turini_aniqlash():
    hozir = datetime.datetime.now(pytz.timezone("Asia/Tashkent"))
    return 'kun' if 6 <= hozir.hour < 18 else 'tun'


def get_weather(lat=None, lon=None):
    params = {'appid': OWM_API_KEY, 'units': 'metric', 'lang': 'en'}
    if lat and lon:
        params['lat'] = lat
        params['lon'] = lon
    else:
        params['q'] = 'Tashkent,UZ'

    try:
        res = requests.get(WEATHER_URL, params=params, timeout=10)
        res.raise_for_status()
        data = res.json()
        temp = data['main']['temp']
        desc_en = data['weather'][0]['description'].lower()
        weather_main = data['weather'][0]['main'].lower()
        desc_uz = UZ_TRANSLATIONS.get(desc_en, desc_en)

        if weather_main == 'clear':
            icon = 'clear'
        elif weather_main == 'clouds':
            icon = 'clouds'
        elif weather_main in ['rain', 'drizzle']:
            icon = 'rain'
        elif weather_main == 'snow':
            icon = 'snow'
        elif weather_main == 'thunderstorm':
            icon = 'thunderstorm'
        elif weather_main in [
                'mist', 'fog', 'haze', 'dust', 'sand', 'ash', 'squall',
                'tornado'
        ]:
            icon = 'mist'
        else:
            icon = 'clear'

        return {
            'text': f"🌡️ Ob-havo: {temp:.0f}°C, {desc_uz.capitalize()}",
            'icon': icon
        }
    except Exception as e:
        log_yoz(f"Ob-havo xatosi: {e}")
        return {'text': "Ob-havo ma'lumotlari mavjud emas.", 'icon': 'clear'}


async def tongi_salom():
    now = datetime.datetime.now(pytz.timezone("Asia/Tashkent"))
    day = now.strftime('%A')
    salom = kun_salomlari.get(day, "🌞 Hayrli tong!")
    weather = get_weather()
    img = get_image_url_by_weather(weather['icon'], vaqt_turini_aniqlash())
    await bot.send_photo(chat_id=CHAT_ID,
                         photo=img,
                         caption=f"{salom}\n\n{weather['text']}")
    log_yoz("🌅 Tongi salom yuborildi.")


async def faqat_obhavo():
    weather = get_weather()
    img = get_image_url_by_weather(weather['icon'], vaqt_turini_aniqlash())
    await bot.send_photo(chat_id=CHAT_ID, photo=img, caption=weather['text'])
    log_yoz("🌤 Ob-havo yuborildi.")


async def kechki_salom():
    salom_matn = random.choice(kech_salomlari)
    weather = get_weather()
    img = get_image_url_by_weather(weather['icon'], 'tun')
    await bot.send_photo(chat_id=CHAT_ID,
                         photo=img,
                         caption=f"{salom_matn}\n\n{weather['text']}")
    log_yoz("🌙 Kechki salom yuborildi.")


async def handle_location(update: Update, context: CallbackContext):
    location = update.message.location
    if location:
        lat = location.latitude
        lon = location.longitude
        weather = get_weather(lat, lon)
        img = get_image_url_by_weather(weather['icon'], vaqt_turini_aniqlash())
        await update.message.reply_photo(
            photo=img, caption=f"📍 Siz yuborgan joy: \n{weather['text']}")
        log_yoz("📍 Joylashuvdan ob-havo yuborildi.")

async def handle_text(update: Update, context: CallbackContext):
    user = update.effective_user
    text = update.message.text
    save_user(user)
    log_yoz(f"✉️ {user.first_name} (@{user.username}): {text}")
    await update.message.reply_text("Xabaringiz qabul qilindi. Rahmat!")



# Schedule
schedule.every().day.at("23:00").do(lambda: asyncio.run(tongi_salom()))
schedule.every().day.at("12:00").do(lambda: asyncio.run(faqat_obhavo()))
schedule.every().day.at("18:00").do(lambda: asyncio.run(faqat_obhavo()))
schedule.every().day.at("23:00").do(lambda: asyncio.run(kechki_salom()))


async def schedule_loop():
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)


import nest_asyncio

from telegram.ext import CommandHandler


async def start_command(update: Update, context: CallbackContext):
    save_user(update.effective_user)
    await update.message.reply_text("Assalomu alaykum! Lokatsiya yuboring!")


async def help_command(update: Update, context: CallbackContext):
    await update.message.reply_text(
        "Botdan foydalanish uchun lokatsiya yuboring yoki /start ni bosing.")


if __name__ == '__main__':
    keep_alive()
    log_yoz("Bot ishga tushmoqda...")

    nest_asyncio.apply()

    async def start():
        application = ApplicationBuilder().token(TOKEN).build()
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(MessageHandler(filters.LOCATION, handle_location))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))


        asyncio.create_task(schedule_loop())
        await application.run_polling()

    asyncio.get_event_loop().run_until_complete(start())
