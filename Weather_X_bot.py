from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import requests

# 🔹 API KEYS (Replace with your actual keys)
BOT_TOKEN = "7880903198:AAE9L8v6vbbpLSi_M-6ZqsH38hC608glYz8"
WEATHER_API_KEY = " da8e40190c581ab56fd4e94bb9bf11c1  "

# 🔹 Function to Get Current Weather
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url).json()
    
    if "main" in response:
        temp = response["main"]["temp"]
        humidity = response["main"]["humidity"]
        weather_desc = response["weather"][0]["description"]
        
        return (
            f"🌍 **{city.upper()} Weather Report**\n"
            f"🌡 **Temperature:** {temp}°C\n"
            f"💧 **Humidity:** {humidity}%\n"
            f"🌤 **Condition:** {weather_desc.capitalize()}\n\n"
            f"🔔 Stay safe and have a great day! 😊"
        )
    return "❌ City not found!"

# 🔹 Function to Get 7-Day Forecast
def get_forecast(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url).json()
    
    if "list" in response:
        forecast_text = f"📍 **{city} - 7-Day Forecast 🌦**\n"
        for i in range(0, len(response["list"]), 8):  # Every 8th entry (24-hour gap)
            date = response["list"][i]["dt_txt"].split()[0]
            temp = response["list"][i]["main"]["temp"]
            weather_desc = response["list"][i]["weather"][0]["description"]
            forecast_text += f"📅 {date} - {temp}°C, {weather_desc}\n"
        return forecast_text
    return "❌ City not found!"

# 🔹 Weather Alert Function (Heavy Rain, Storm, Heatwave)
def get_alert(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url).json()

    if "weather" in response:
        weather_desc = response["weather"][0]["description"]
        if "rain" in weather_desc or "storm" in weather_desc:
            return f"⚠️ **Weather Alert for {city.upper()}!** 🌧️🌪️\nHeavy Rain/Storm expected! Stay safe! 🙏"
        elif "hot" in weather_desc or response["main"]["temp"] > 40:
            return f"🔥 **Heatwave Alert in {city.upper()}!** 🌡️\nStay hydrated & avoid going out in extreme heat! 🥵"
    return None

# 🔹 Command for Weather
async def weather(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = " ".join(context.args)
    if not city:
        await update.message.reply_text("❌ Please provide a city name! Example: `/weather Mumbai`")
    else:
        weather_report = get_weather(city)
        alert_message = get_alert(city)
        if alert_message:
            weather_report += f"\n\n{alert_message}"  # Add alert to weather report
        await update.message.reply_text(weather_report)

# 🔹 Command for 7-Day Forecast
async def forecast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    city = " ".join(context.args)
    if not city:
        await update.message.reply_text("❌ Please provide a city name! Example: `/forecast Mumbai`")
    else:
        await update.message.reply_text(get_forecast(city))

# 🔹 Start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌆 Mumbai", callback_data="Mumbai"),
         InlineKeyboardButton("🏙 Delhi", callback_data="Delhi")],
        [InlineKeyboardButton("🌇 Kolkata", callback_data="Kolkata"),
         InlineKeyboardButton("🏔 Shimla", callback_data="Shimla")],
        [InlineKeyboardButton("🌎 Auto-Detect Location", callback_data="location")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🌤 **Welcome to WeatheryX!**\n"
        "📌 Get real-time weather updates:\n"
        "📝 Use `/weather CityName` for current weather.\n"
        "🔮 Use `/forecast CityName` for a 7-day forecast.\n"
        "🔘 Click below to select a city:",
        reply_markup=reply_markup
    )

# 🔹 Button Click Handler
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    city = query.data

    if city == "location":
        await query.message.reply_text("📍 Please share your live location for weather updates.")
    else:
        weather_report = get_weather(city)
        alert_message = get_alert(city)
        if alert_message:
            weather_report += f"\n\n{alert_message}"
        await query.message.reply_text(weather_report)

# 🔹 Bot Setup
application = Application.builder().token(BOT_TOKEN).build()

# 🔹 Add Handlers
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("weather", weather))
application.add_handler(CommandHandler("forecast", forecast))
application.add_handler(CallbackQueryHandler(button_click))

# 🔹 Start Bot
application.run_polling()