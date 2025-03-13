from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import requests
from sklearn.linear_model import LogisticRegression
import numpy as np
import os
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextSendMessage

app = FastAPI()

# 從環境變數獲取金鑰
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')
LINE_CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
LINE_CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

if not all([WEATHER_API_KEY, NEWS_API_KEY, LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET]):
    raise ValueError("請設置所有環境變數")

line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 初始化資料庫
def init_db():
    conn = sqlite3.connect('digi_twin.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    city TEXT,
                    preferences TEXT
                )''')
    conn.commit()
    conn.close()

init_db()

# 簡單的 AI 模型
X_train = np.array([[1, 2], [2, 3], [3, 4]])
y_train = np.array([0, 1, 1])
model = LogisticRegression()
model.fit(X_train, y_train)

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}"
    response = requests.get(url).json()
    if response.get('weather'):
        return response['weather'][0]['description']
    return "無法獲取天氣"

def get_news(preferences):
    preference_map = {
        "科技": "technology",
        "體育": "sports",
        "商業": "business",
        "娛樂": "entertainment",
        "健康": "health",
        "科學": "science",
        "一般": "general"
    }
    category = preference_map.get(preferences, preferences)
    url = f"https://newsapi.org/v2/everything?q=AI+robotics+space+-game&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    if response.get('status') == 'ok' and response.get('articles'):
        # 返回前 10 篇新聞標題
        articles = response['articles'][:10]
        return [article['title'] for article in articles]
    else:
        return [f"無法獲取新聞: {response.get('message', '未知錯誤')}"]

def predict_action(features):
    return model.predict([features])[0]

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("static/index.html") as f:
        return f.read()

@app.post("/add_user")
async def add_user(request: Request):
    data = await request.json()
    conn = sqlite3.connect('digi_twin.db')
    c = conn.cursor()
    c.execute("INSERT INTO users (name, city, preferences) VALUES (?, ?, ?)", 
              (data['name'], data['city'], data['preferences']))
    conn.commit()
    conn.close()
    return {"message": "用戶已添加"}

@app.get("/get_task/{user_id}")
async def get_task(user_id: int):
    conn = sqlite3.connect('digi_twin.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        city = user[2]
        preferences = user[3]
        weather = get_weather(city)
        news = get_news(preferences)
        features = [10, 5]
        action = predict_action(features)
        if action == 1:
            return {"weather": weather, "news": news}
        else:
            return {"message": "今天不建議看新聞"}
    return {"error": "用戶不存在"}

# Line Webhook
@app.post("/line_webhook")
async def line_webhook(request: Request):
    signature = request.headers.get('X-Line-Signature')
    body = await request.body()
    try:
        handler.handle(body.decode('utf-8'), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    return "OK"

@handler.add(event='message')
def handle_message(event):
    user_id = 1  # 假設 ID 為 1，未來可以用 Line User ID
    conn = sqlite3.connect('digi_twin.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    if user:
        city = user[2]
        preferences = user[3]
        weather = get_weather(city)
        news = get_news(preferences)
        # 將 10 篇新聞組成訊息
        message = f"天氣: {weather}\n新聞:\n" + "\n".join([f"{i+1}. {title}" for i, title in enumerate(news)])
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=message))