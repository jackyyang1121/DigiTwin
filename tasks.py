import requests

# 放你的 API 金鑰（記得換成你自己的！）
WEATHER_API_KEY = '3560ea03a0ed72d11a18483ba3144222'
NEWS_API_KEY = '10695b33612f4d0f902f27f85bd136f5'

# 查天氣
def get_weather(city):
    # 用城市名跟 API 拿天氣資料
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}"
    response = requests.get(url).json()  # 送請求，拿回 JSON 格式資料
    if response.get('weather'):  # 如果有天氣資訊
        return response['weather'][0]['description']  # 回傳天氣描述（像「晴天」）
    return "無法獲取天氣"  # 沒拿到就回這個

# 找新聞
def get_news(preferences):
    # 用喜好（像 "technology"）跟 API 拿新聞
    url = f"https://newsapi.org/v2/top-headlines?category={preferences}&apiKey={NEWS_API_KEY}"
    response = requests.get(url).json()
    if response.get('articles'):  # 如果有新聞
        return response['articles'][0]['title']  # 回傳第一篇新聞標題
    return "無法獲取新聞"  # 沒拿到就回這個