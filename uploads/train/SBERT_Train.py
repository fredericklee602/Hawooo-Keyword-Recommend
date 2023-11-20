import pandas as pd
from sentence_transformers import SentenceTransformer, SentencesDataset, InputExample, evaluation, losses
from torch.utils.data import DataLoader
import os
from copy import deepcopy
from random import randint
def shuffle(lst):
    temp_lst = deepcopy(lst)
    m = len(temp_lst)
    while (m):
        m -= 1
        i = randint(0, m)
        temp_lst[m], temp_lst[i] = temp_lst[i], temp_lst[m]
    return temp_lst

class SBERT_init():
    def __init__(self):
        self.flask_return = {"data":"Model training has not been started","trained":False,"training":False,"reload":True}
        self.dataloader_len = 0
        self.progress_len = 1
        self.train_step = 0
        self.callback_result = {"score":0, "epoch":0, "steps":0}
    def callback(self,score, epoch, steps):
        score = round(score, 5)
        self.callback_result = {"score":score, "epoch":epoch, "steps":steps}
        if os.path.exists("./log/file.txt"):
            self.flask_return["training"] = False
            self.flask_return["data"] = "Model training was terminated"
            os.remove("./log/file.txt")
            print("Stop file detected. Stopping training...")
            exit(0)  # 中斷訓練
        if steps>=0:
            print("progress_len:{}".format(self.progress_len))
            print("steps:{}".format(steps))
            self.train_step = epoch*self.dataloader_len+steps
            progress_rate = int(self.train_step/self.progress_len*100)
            print("progress_rate:{}".format(progress_rate))
            Training_log = "Training State({3}%):  Model score:{0} ------ epoch no.{1} ------ steps:{2}".format(score, epoch, steps,progress_rate)
            self.flask_return["data"] = Training_log

    def model_train(self):
        self.flask_return["reload"] = False
        # print("開始訓練")
        self.flask_return["data"] = "Loading model 'Azion/e-commerce-bert-base-multilingual-cased'."
        model = SentenceTransformer('Azion/e-commerce-bert-base-multilingual-cased')
        process_path = "./data/AI_data/process/"+"train_df.csv"
        self.flask_return["data"] = "Loading train data..."
        df = pd.read_csv(process_path)
        sen1_list = []
        sen2_list = []
        for i,raw in df.iterrows():
            if type(raw["sentence1"])==str and type(raw["sentence2"])==str:
                sen1_list.append(raw["sentence1"])
                sen2_list.append(raw["sentence2"])
        shuffle_sen1_list = shuffle(sen1_list) # 所有的中文句子打亂排序
        shuffle_sen2_list = shuffle(sen2_list) #　所有的英文句子打亂排序
        train_size = int(len(sen2_list) * 0.8)
        eval_size = len(sen2_list) - train_size

        # Define your train examples.
        train_data = []
        for idx in range(train_size):
            train_data.append(InputExample(texts=[sen2_list[idx], sen1_list[idx]], label=1.0))
            train_data.append(InputExample(texts=[shuffle_sen2_list[idx], shuffle_sen1_list[idx]], label=0.0))
        self.logger = "Number of training data: {}".format(len(train_data))
        self.flask_return["data"] =self.logger
        # Define your evaluation examples
        sentences1 = sen1_list[-5:]
        sentences2 = sen2_list[-5:]
        sentences1.extend(list(shuffle_sen1_list[-5:]))
        sentences2.extend(list(shuffle_sen2_list[-5:]))
        scores = [1.0] * 5 + [0.0] * 5
        evaluator = evaluation.EmbeddingSimilarityEvaluator(sentences1, sentences2, scores)
        # Define your train dataset, the dataloader and the train loss
        train_dataset = SentencesDataset(train_data, model)
        train_dataloader = DataLoader(train_dataset, shuffle=True, batch_size=16)
        train_loss = losses.CosineSimilarityLoss(model)
        # Define the model. Either from scratch of by loading a pre-trained model
        self.logger = "Start Traing Model"
        self.flask_return["data"]=self.logger
        num_epochs=2
        self.dataloader_len = len(train_dataloader)
        self.progress_len = len(train_dataloader)*num_epochs
        warmup_steps = int(len(train_dataloader) * num_epochs * 0.1) #10% of train data
        # Tune the model
        self.flask_return["training"] = True
        model.fit(train_objectives=[(train_dataloader, train_loss)], epochs=num_epochs, warmup_steps=warmup_steps, evaluator=evaluator, evaluation_steps=1, output_path='./AI_Model2',callback=self.callback)
        model.save('./AI_Model2')
        self.flask_return["training"] = False
        self.logger = "Model training has been completed. Model score:{0}".format(self.callback_result["score"])
        self.flask_return["data"]=self.logger
        self.flask_return["trained"]=True
        
