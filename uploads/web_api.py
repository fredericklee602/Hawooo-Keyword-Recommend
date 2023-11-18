from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
from train import SBERT_Train
from VectorDB import weaviate_api
# from multiprocessing import Process, Value
import threading
AI_data_process_path = "./data/AI_data/process/"+"train_df.csv"
keywords_process_path = "./data/keywords_data/process/"+"keywords.csv"
keywords_DBID_path = "./data/keywords_data/process/"+"keywords_DBID.csv"
search_word = "./data/search_word/"+"search_word_count.csv"
sbert = SBERT_Train.SBERT_init()
vectorDB_API = weaviate_api.API()
stop_training_signal = threading.Event()
def train_model():
    while not stop_training_signal.is_set():
        sbert.model_train()
        stop_training_signal.set()
    print("Training stopped!")
app = Flask(__name__)
cors = CORS(app, resources={r"/*": {"origins": "*"}})    # 

# Train part
@app.route("/upload_train_data/", methods=["POST"])
def save_train_data_file():
    form_data = request.form
    data = request.files
    columns = request.files
    file = data['file']
    columns = form_data['columns'].split(",")
    print("columns:",columns)
    path = "./data/AI_data/original/"+file.filename
    file.save(path)
    print("Receive file successfully...")
    try:
        if "csv" in file.filename:
            df = pd.read_csv(path)
        if "xl" in file.filename:
            df = pd.read_excel(path)
        newdf = df[columns]
        newdf.columns=["sentence1","sentence2"]
        newdf.to_csv(AI_data_process_path)
        return jsonify("已經建立好訓練資料")
    except Exception as e:
        print(e)
        return e
    
@app.route("/return_train_data/", methods=["GET"])
def return_train_data():
    df = pd.read_csv(AI_data_process_path)[["sentence1","sentence2"]][:10]
    return jsonify(df.to_dict(orient='records'))

@app.route("/train/", methods=["GET"])
def train_model_route():
    stop_training_signal.clear()
    t = threading.Thread(target=train_model)
    t.start()
    return jsonify({'data':"開始訓練"})

@app.route('/stop_training/', methods=['GET'])
def stop_training():
    # 設置信號以停止訓練
    # stop_training_signal.set()
    file_path = "./log/file.txt"
    f = open(file_path, 'w')
    f.write('Hello World')
    f.close()
    return jsonify({'data':"訓練終止"})

@app.route('/get_train_log', methods=['GET'])
def get_train_log():
    return jsonify(sbert.flask_return)

@app.route("/upload_keywords_data/", methods=["POST"])
def save_keywords_data_file():
    from opencc import OpenCC
    from nltk.stem import PorterStemmer
    ps = PorterStemmer()
    cc = OpenCC('s2t')
    form_data = request.form
    data = request.files
    file = data['file']
    columns = form_data['columns']
    print("columns:",columns)
    path = "./data/keywords_data/original/"+file.filename
    file.save(path)
    print("Receive file successfully...")
    try:
        if "csv" in file.filename:
            df = pd.read_csv(path)
        if "xl" in file.filename:
            df = pd.read_excel(path)
        keywords_series = df[columns].tolist()
        print("keywords欄位資料數{}".format(len(keywords_series)))
        keywords_set = []
        c=0
        for keywords in keywords_series:
            c=c+1
            if c%10000==0:
                print("已完成到第{}筆keyword".format(c))
            if type(keywords)==str:
                keywords_list = keywords.split(",")
                for keyword in keywords_list:
                    keyword = keyword.replace(' ', '', 1)
                    keyword = cc.convert(keyword)
                    keyword = ps.stem(keyword)
                    if keyword not in keywords_set:
                        keywords_set.append(keyword)
        keywords_set = list(set(keywords_set))
        keywords_set = [keyword.lstrip() for keyword in keywords_set]
        keywords_set.sort()
        newdf = pd.DataFrame(keywords_set)
        newdf.columns=["Keywords"]
        newdf.to_csv(keywords_process_path)
        return jsonify("已經建立好Keywords資料集")
    except Exception as e:
        print(e)
        return e

@app.route("/return_keywords_data/", methods=["GET"])
def return_keywords_data():
    df = pd.read_csv(keywords_process_path)[["Keywords"]].dropna().reset_index()
    keywords_count = len(df)
    df = df[:20]
    return jsonify({"dataframe":df.to_dict(orient='records'),"keywords_count":keywords_count})

@app.route("/return_table_information/", methods=["GET"])
def return_table_information():
    class_list = vectorDB_API.get_tables()
    return jsonify({"vectorDB_table_name":class_list})

@app.route("/add_new_vector_table/", methods=["GET"])
def add_new_vector_table():
    isCreated = vectorDB_API.creat_table()
    return jsonify({"isCreated":isCreated})

@app.route("/update_vector_DB/", methods=["POST"])
def update_vector_DB():
    form_data = request.form
    print("form_data",form_data)
    VBTable_name = form_data['VBTable_name']
    t = threading.Thread(target=vectorDB_API.forward_request(VBTable_name))
    t.start()
    return jsonify({'data':"開始更新Vector DB"})

@app.route("/remove_vector_table/", methods=["POST"])
def remove_vector_table():
    form_data = request.form
    print("form_data",form_data)
    VBTable_name = form_data['VBTable_name']
    isRemoved = vectorDB_API.remove_table(VBTable_name)
    return jsonify({"isRemoved":isRemoved})

@app.route('/get_vector_DB_log', methods=['GET'])
def get_vector_DB_log():
    return jsonify(vectorDB_API.flask_return)

@app.route('/recommend_keywords/', methods=['POST'])
def recommend_keywords():
    message = request.json['message']
    class_name = request.json['class'][0]
    if vectorDB_API.DB_set["class"]!=class_name:
        vectorDB_API.setEmbeddingDB(class_name)
        print("設置DB完成")
    recommend = vectorDB_API.recommend_keywords(message)
    print(recommend)
    return jsonify({"reply": recommend})

@app.route('/recommend_keywords_list/', methods=['POST'])
def recommend_keywords_list():
    form_data = request.form
    print("form_data",form_data)
    message = form_data['message']
    class_name = form_data['class']
    if vectorDB_API.DB_set["class"]!=class_name:
        vectorDB_API.setEmbeddingDB(class_name)
        print("設置DB完成")
    recommend = vectorDB_API.recommend_keywords_list(message)
    print(recommend)
    return jsonify({"reply": recommend})

@app.route('/synonyms_base/', methods=['GET'])
def synonyms_base():
    synonyms_base_path = "./data/synonyms_data/similarity_keywords.csv"
    df = pd.read_csv(synonyms_base_path).dropna().reset_index()
    df = df.iloc[::-1]
    return jsonify({"dataframe":df.to_dict(orient='records')})

@app.route('/synonyms_write/', methods=['POST'])
def synonyms_write():
    form_data = request.form
    keyword = form_data['keyword']
    synonyms = form_data['synonyms']
    synonyms_base_path = "./data/synonyms_data/similarity_keywords.csv"
    df = pd.read_csv(synonyms_base_path).dropna().reset_index()[["keyword","similarity_keywords"]]
    keywords_list = df["keyword"].tolist()
    if keyword in keywords_list:
        keywordID = keywords_list.index(keyword)
        similarity_keywords = df["similarity_keywords"][keywordID]
        similarity_keywords_list = similarity_keywords.split(",")
        synonyms_list = synonyms.split(",")
        similarity_keywords_list.extend(synonyms_list)
        similarity_keywords_list = list(set(similarity_keywords_list))
        similarity_keywords = ",".join(similarity_keywords_list)
        df.at[keywordID, 'similarity_keywords'] = similarity_keywords
    else:
        df.loc[len(df.index)] = [keyword, synonyms]
    df.to_csv(synonyms_base_path)
    print("synonyms_base_path 寫入")
    return jsonify({'data':"synonyms_base_path 寫入"})

@app.route("/return_keywords_data_all/", methods=["GET"])
def return_keywords_data_all():
    # df_last = pd.read_csv(keywords_process_path).sort_values(by=['Keywords']).dropna().reset_index()[['Keywords']].reset_index()
    # df_VDB = pd.read_csv(keywords_DBID_path).sort_values(by=['Keywords']).dropna().reset_index()[['Keywords']].reset_index()
    # print("df_last",df_last.head().to_dict(orient='records'))
    df_last = pd.read_csv(keywords_process_path)
    df_VDB = pd.read_csv(keywords_DBID_path)
    df = pd.read_csv(search_word)
    df = df.rename(columns={'search word': 'Keywords'})
    df_last = df_last.merge(df, on='Keywords', how='left').sort_values(by=['count'],ascending=False).reset_index()[['Keywords']].dropna().reset_index()
    df_VDB = df_VDB.merge(df, on='Keywords', how='left').sort_values(by=['count'],ascending=False).reset_index()[['Keywords']].dropna().reset_index()
    print("df_last",df_last.head())
    return jsonify({"lastdataframe":df_last.to_dict(orient='records'),"VDBdataframe":df_VDB.to_dict(orient='records')})

@app.route("/remove_keyword_on_VectorDB/", methods=["POST"])
def remove_keyword_on_VectorDB():
    form_data = request.form
    keyword = form_data['keyword']
    df_VDB = pd.read_csv(keywords_DBID_path)
    Keywordslist = df_VDB["Keywords"].tolist()
    try:
        ID = Keywordslist.index(keyword)
        uuid = df_VDB["VectorDB ID"][ID]
        isRemoved = vectorDB_API.remove_keyword(uuid)
        df_VDB = df_VDB.drop(index=ID)
        df_VDB = df_VDB[["Keywords","VectorDB ID"]]
        df_VDB.to_csv(keywords_DBID_path)
        return jsonify({"isRemoved":isRemoved})
    except Exception as e:
        print(e)
        return jsonify({"isRemoved":e})


if __name__ == '__main__':
    app.debug=True    # 啟用調試支持
    app.run(host="0.0.0.0", port=7500)