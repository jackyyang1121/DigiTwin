from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import sqlite3
import requests
from sklearn.linear_model import LogisticRegression
import numpy as np
import os

app = FastAPI()

WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
NEWS_API_KEY = os.getenv('NEWS_API_KEY')

if not WEATHER_API_KEY or not NEWS_API_KEY:
    raise ValueError("請設置 WEATHER_API_KEY 和 NEWS_API_KEY 環境變數")

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

# 訓練一個簡單的 AI 模型
X_train = np.array([[1, 2], [2, 3], [3, 4]])
y_train = np.array([0, 1, 1])
model = LogisticRegression()
model.fit(X_train, y_train)

# 查天氣
def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}"
    response = requests.get(url).json()
    if response.get('weather'):
        return response['weather'][0]['description']
    return "無法獲取天氣"

# 找新聞
def get_news(preferences):
    url = f"https://newsapi.org/v2/top-headlines?category={preferences}&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    if response.get('articles'):
        return response['articles'][0]['title']
    return "無法獲取新聞"

# 預測行動
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
        features = [10, 5]  # 假設的特徵值
        action = predict_action(features)
        if action == 1:
            return {"weather": weather, "news": news}
        else:
            return {"message": "今天不建議看新聞"}
    return {"error": "用戶不存在"}