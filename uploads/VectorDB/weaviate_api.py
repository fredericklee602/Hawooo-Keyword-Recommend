
import weaviate
from langchain.vectorstores import Weaviate
from langchain.embeddings import HuggingFaceEmbeddings
import time
import pandas as pd
keywords_process_path = "./data/keywords_data/process/"+"keywords.csv"
keywords_DBID_path = "./data/keywords_data/process/"+"keywords_DBID.csv"
table_name = "Hawoo_Keywords"

class API:
    def __init__(self):
        self.WEAVIATE_URL = "http://localhost:8080"
        self.client = weaviate.Client(self.WEAVIATE_URL)
        self.DB_set = {"class":None,"already":False}
        self.flask_return = {"data":"Model training is not started","over":False,"reload":True}
    def creat_table(self,create_class_name):
        class_list = self.get_tables()
        if create_class_name in class_list:
            self.flask_return["data"] = "create_class_name:{0}已存在於Vector DB".format(create_class_name)
            print("create_class_name:{0}已存在於Vector DB".format(create_class_name))
            return False
        elif create_class_name not in class_list:
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
            self.client.schema.create(schema)
            self.flask_return["data"] = "新增create_class_name:{0}".format(create_class_name)
            print("新增create_class_name:{0}".format(create_class_name))
            return True 
    def remove_table(self,class_name):
        class_list = self.get_tables()
        if class_name in class_list:
            self.client.schema.delete_class(class_name)
            df = pd.read_csv(keywords_DBID_path)[["Keywords","VectorDB ID"]][:0]
            df.to_csv(keywords_DBID_path)
            print("keywords_DBID_path資料清除。")
            return True
        elif class_name not in class_list:
            return False 

    def get_tables(self):
        schema_get = self.client.schema.get()  # Get the schema to test connection
        class_list = []
        for schema in schema_get["classes"]:
            class_list.append(schema["class"])
        return class_list

    def setEmbeddingDB(self,create_class_name):
        self.flask_return["reload"] = False
        # model_name = "Azion/e-commerce-bert-base-multilingual-cased"
        model_name = "./AI_Model"
        model_kwargs = {'device': 'cuda'}
        encode_kwargs = {'normalize_embeddings': False}
        hf = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )
        self.Weaviate_client = Weaviate(client=self.client,index_name=create_class_name,text_key="keyword",embedding=hf,by_text=False)
        self.DB_set = {"class":create_class_name,"already":True}
        self.flask_return["data"] = "Weaviate client AI model設置完成"
    def insertEmbedding(self,word_list):
        if self.DB_set["already"]:
            last_word_df = pd.read_csv(keywords_DBID_path)
            last_word_list = last_word_df["Keywords"].tolist()
            word_list = list(word_list)
            word_list = [x for x in word_list if pd.isnull(x) == False and x not in last_word_list]
            vdb_id_list = []
            batch_texts_list = []
            s = time.time()
            self.flask_return["data"] = "資料總筆數：{}".format(len(word_list))
            print("資料總筆數：{}".format(len(word_list)))
            for i in range(len(word_list)):
                batch_texts_list.append(word_list[i])
                if (i+1)%1000==0:
                    batch_id_list = self.Weaviate_client.add_texts(texts=batch_texts_list)
                    vdb_id_list.extend(batch_id_list)
                    now = time.time()
                    print("已完成到第{}筆資料".format(i+1))
                    print("已花費時間：{} sec".format(now-s))
                    log_string = "已完成到第{0}筆資料，花費時間：{1} sec".format(i+1,format(now-s, '.4f'))
                    self.flask_return["data"] = log_string
                    batch_texts_list = []
            if len(batch_texts_list)!=0:
                print("batch_texts_list",len(batch_texts_list))
                batch_id_list = self.Weaviate_client.add_texts(texts=batch_texts_list)
                vdb_id_list.extend(batch_id_list)
                now = time.time()
                print("已完成到第{}筆資料".format(i+1))
                print("已花費時間：{} sec".format(now-s))
                batch_texts_list = []
            df = pd.DataFrame(zip(word_list,vdb_id_list),columns=["Keywords","VectorDB ID"])
            df = pd.concat([last_word_df,df],axis=0)[["Keywords","VectorDB ID"]]
            # df.columns = ["keywords","VectorDB ID"]
            df.to_csv(keywords_DBID_path)
            return "已經完成Vector DB"
        else:
            print("請先設定完整的Vector DB")
            return "請先設定完整的Vector DB"
    def forward_request(self,create_class_name):
        self.flask_return["reload"]=False
        isAdd = self.creat_table(create_class_name)
        self.setEmbeddingDB(create_class_name)
        word_list = pd.read_csv(keywords_process_path)["Keywords"]
        result = self.insertEmbedding(word_list)
        print(result)
        self.flask_return["data"] = result

    def recommend_keywords(self,search_string):
        print("self.DB_set",self.DB_set)
        most_sim = self.Weaviate_client.similarity_search(search_string,k=20)
        most_sim_result = []
        for doc in most_sim:
            most_sim_result.append(doc.page_content)
        return ", ".join(most_sim_result)
    
    def recommend_keywords_list(self,search_string):
        print("search_string",search_string)
        print("self.DB_set",self.DB_set)
        most_sim = self.Weaviate_client.similarity_search(search_string,k=20)
        most_sim_result = []
        for doc in most_sim:
            most_sim_result.append(doc.page_content)
        return most_sim_result
    
    def remove_keyword(self,uuid):
        self.client.data_object.delete(
            uuid=uuid,
            class_name=table_name, # ONLY with Weaviate >= 1.14.0
        )
        return True

