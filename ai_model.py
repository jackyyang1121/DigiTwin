from sklearn.linear_model import LogisticRegression
import numpy as np

# 假資料：模擬用戶過去的行為
X_train = np.array([[1, 2], [2, 3], [3, 4]])  # 特徵，像時間和心情
y_train = np.array([0, 1, 1])  # 結果，0=不看新聞，1=看新聞

model = LogisticRegression()  # 用這個模型來學
model.fit(X_train, y_train)   # 訓練模型

# 預測你要幹嘛
def predict_action(features):
    return model.predict([features])[0]  # 輸入特徵，猜你要不要看新聞