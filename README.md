# Searching-for-exact-keyword-using-sbert-models
AI鬥智賽-好物飛行電商平台題目。解決搜尋字串正確性問題。

## Vector DB - Weaviate

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

## 後端Flask

* `/uploads/web_api.py`：前端vue.js呼叫後端API之Flask。
1. 呼叫訓練SBERT，開啟及停止功能。
2. 上傳訓練資料功能。
3. 回傳資料。
4. 呼叫Vector DB功能。

## SBERT
* `/uploads/train/SBERT_Train.py`：訓練SBERT Fuction，用Sentence Transformers建立SBERT訓練架構。
* 訓練狀態會以callback回傳出來。

## log
* `/uploads/log/file.txt`：存在與否與訓練SBERT是否終止有關。

## 資料集 `/uploads/data`
*  `AI_data`：存放訓練語意的資料。
*  `keywords_data`：存放存在於VectorDB的Keywords，防止可能重複性存入VectorDB。
*  `search_word`：Hawooo網站中最常搜尋關鍵字統計數量。
*  `synonyms_data`：同義詞庫資料建立。
*  `test_data`：於Web UI上傳資料時可以測試用資料。

## VUE.JS Web UI
* 



