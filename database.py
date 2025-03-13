import sqlite3

# 建立資料庫和表格
def init_db():
    conn = sqlite3.connect('digi_twin.db')  # 連到一個名叫 digi_twin.db 的檔案
    c = conn.cursor()  # 拿個「游標」來操作資料庫
    # 建一個表，裡面存用戶的 ID、名字、城市、喜好
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT,
                    city TEXT,
                    preferences TEXT
                )''')
    conn.commit()  # 確定儲存
    conn.close()   # 關掉連線

# 加一個新用戶進資料庫
def add_user(name, city, preferences):
    conn = sqlite3.connect('digi_twin.db')  # 連到資料庫
    c = conn.cursor()
    # 把名字、城市、喜好塞進表裡
    c.execute("INSERT INTO users (name, city, preferences) VALUES (?, ?, ?)", (name, city, preferences))
    conn.commit()  # 儲存
    conn.close()   # 關掉

# 找某個用戶的資料
def get_user(user_id):
    conn = sqlite3.connect('digi_twin.db')
    c = conn.cursor()
    # 用 ID 找用戶，找到就回傳他的資料
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = c.fetchone()  # 拿第一筆資料
    conn.close()
    return user  # 回傳找到的用戶