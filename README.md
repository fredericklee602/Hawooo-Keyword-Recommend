# Searching-for-exact-keyword-using-sbert-models
## AI鬥智賽-好會飛網路股份有限公司
- 題目：透過NLP技術分辨消費者輸入的搜尋字串是否正確，以提高搜尋結果之正確性。

### Vector DB - Weaviate

* 下載Weaviate Docker：https://weaviate.io/developers/weaviate/installation/docker-compose
* ```pip install weaviate-client```
* 建立Vector DB，對應docker container port設置。
```
import weaviate
client = weaviate.Client("http://localhost:8080")
schema = {
          "classes": [{
            "class": create_class_name,
            "description": "Hawoo product search keywords",
            "vectorizer": "none",
            "properties": [{
                "name": "keyword",
                "dataType": ["text"],
            }]
          }]
        }
client.schema.create(schema)
```
* `/uploads/VectorDB/weaviate_api.py`：控制Weaviate Function，寫入Doc Embedding、推薦相關關鍵字、刪除關鍵字。

### 後端Flask

* `/uploads/web_api.py`：前端vue.js呼叫後端API之Flask。
1. 呼叫訓練SBERT，開啟及停止功能。
2. 上傳訓練資料功能。
3. 回傳資料。
4. 呼叫Vector DB功能。

### SBERT
* `/uploads/train/SBERT_Train.py`：訓練SBERT Fuction，用Sentence Transformers建立SBERT訓練架構。
* 訓練狀態會以callback回傳出來。

### 資料集 `/uploads/data`
*  `AI_data`：存放訓練語意的資料。
*  `keywords_data`：存放存在於VectorDB的Keywords，防止可能重複性存入VectorDB。
*  `search_word`：Hawooo網站中最常搜尋關鍵字統計數量。
*  `synonyms_data`：同義詞庫資料建立。
*  `test_data`：於Web UI上傳資料時可以測試用資料。

### log
* `/uploads/log/file.txt`：如果存在則關閉訓練SBERT。

### VUE.JS Web UI
1. 詞彙向量化模型訓練：上傳訓練資料集，並且開始訓練SBERT。
2. 建立詞彙向量資料庫：使用訓練好的SBERT模型做Embedding，建立詞彙向量資料庫。
3. 從Vector DB推薦想要找的可能同義詞，並將其整理在同義詞庫中。

#### 首頁

<img width="700" src="https://github.com/fredericklee602/Searching-for-exact-keyword-using-sbert-models/blob/main/sceenshot/home.PNG">

#### 推薦同義詞庫

<img width="700" src="https://github.com/fredericklee602/Searching-for-exact-keyword-using-sbert-models/blob/main/sceenshot/synonyms.PNG">

### Hawoo電商可能問題
- 錯別字輸入
- 用戶可能因為輸入錯別字，在網站的搜索欄中輸入查詢詞時無法得到正確或相似、相關結果。

<img width="700" src="https://github.com/fredericklee602/Searching-for-exact-keyword-using-sbert-models/blob/main/sceenshot/hawoo1.png">

- 商品/品牌之多重名稱
- 商品可能有品牌的同義詞，但用戶有可能擇一輸入，在平台上會找到不同的結果。

<img width="700" src="https://github.com/fredericklee602/Searching-for-exact-keyword-using-sbert-models/blob/main/sceenshot/hawoo2.png">

- 字串比對的侷限
- 商品品牌必須完全正確才有最多結果，用戶有可能需要多次輸入才能在平台上找到目標商品。

<img width="700" src="https://github.com/fredericklee602/Searching-for-exact-keyword-using-sbert-models/blob/main/sceenshot/hawoo3.png">

- 無法單次查詢多個詞彙
- 一般常見的入口網站搜尋體驗可透過空白間隔進行複數查詢，但現平台無法以同樣方式檢索。

<img width="700" src="https://github.com/fredericklee602/Searching-for-exact-keyword-using-sbert-models/blob/main/sceenshot/hawoo4.png">

## 如何解決出題廠商痛點？
1. 別字輸入->校正用戶輸入條件
2. 商品/品牌之多重名稱->引進同義詞檢索
3. 字串比對的侷限->引進斷詞機制
4. 無法單次查詢多個詞彙->引進布林檢索
### 搜尋引擎Gufonet
- 校正用戶輸入條件
- 左圖為出題單位既有檢索結果，右圖為Gufonet校正輸入之技術效果範例。

<img width="700" src="https://github.com/fredericklee602/Searching-for-exact-keyword-using-sbert-models/blob/main/sceenshot/hawoo5.png">

### Before (依照SQL LIKE做搜尋)
- 原Hawooo網站只使用DB的SQL LIKE方法，得完整相同字串才可以搜尋到相關產品。

<img width="700" src="https://github.com/fredericklee602/Searching-for-exact-keyword-using-sbert-models/blob/main/sceenshot/hawoo6.png">

### AI技術應用流程示意
- SBERT 訓練過程。
- 導入Weaviate Vector DB流程。
- 推薦可能同義詞，選取同義詞匯出同義詞庫。

<img width="700" src="https://github.com/fredericklee602/Searching-for-exact-keyword-using-sbert-models/blob/main/sceenshot/hawoo7.png">

### After (搜尋引擎 + AI Model)
- AI推薦可能同義詞庫後再匯入到Gufonet。
- 由Gufonet搜尋引擎做產品推薦。

<img width="700" src="https://github.com/fredericklee602/Searching-for-exact-keyword-using-sbert-models/blob/main/sceenshot/hawoo8.png">

## 成效示意
- 啟用檢索引擎 -> 檢索結果上升**28.43**倍
- 加入同義詞 -> 每項檢索詞結果增幅**6%**
- A/B Test實測 點擊率提升 **4.5%**

<img width="700" src="https://github.com/fredericklee602/Searching-for-exact-keyword-using-sbert-models/blob/main/sceenshot/hawoo9.png">
<img width="700" src="https://github.com/fredericklee602/Searching-for-exact-keyword-using-sbert-models/blob/main/sceenshot/hawoo10.png">



