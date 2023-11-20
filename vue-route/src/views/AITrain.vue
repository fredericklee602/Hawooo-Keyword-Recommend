<template>
    <div>
      
      <!-- 加載指示器 -->
      <div v-if="isLoading" class="loading-overlay">
        <img src="/jumpingsheep.gif" alt="上傳中..." class="loading-image"/>
      </div>
      <!-- 第一部分 -->
      <div class="First-Part">
        <h3 class="title_description">
            上傳產品中英文名稱，以進行模型訓練(csv,xlsx)
        </h3>
  
        <input type="file" @change="handleFileChange">
        <!-- 按鈕加載數據 -->
        <button class="loadData-button" @click="WatchData">觀看前處理資料</button>
        <button class="start-train-button" @click="StartTrain">Train SBERT Model</button>
        <button class="stop-train-button" @click="StopTrain">Stop Training</button>
        
      <div v-if="columns.length && isServerReturn==false">
        <h3 class="title_description">
          選取2個相似對應欄位
        </h3>
        <!-- 呈現欄位名稱的表格 -->
        <table>
          <thead>
            <tr>
              <th>Select</th>
              <th>Column Name</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="column in columns" :key="column">
              <td><input type="checkbox" v-model="selectedColumns[column]"></td>
              <td>{{ column }}</td>
            </tr>
          </tbody>
        </table>
        <button class="submit-button" @click="handleSubmit" v-if="columns.length">提交選取欄位</button>
      </div>
    </div>
  
      <!-- 第二部分 -->
      <div class="Next-Part">
        <!-- 按鈕加載數據 -->
        <table v-if="isWatchData">
          <thead>
            <tr>
              <!-- 假設你知道你的DataFrame的列名 -->
              <th>Sentence1</th>
              <th>Sentence2</th>
              <!-- ... 其他列名 ... -->
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in dataTable" :key="row.id">
              <td>{{ row['sentence1'] }}</td>
              <td>{{ row['sentence2'] }}</td>
              <!-- ... 其他數據列 ... -->
            </tr>
          </tbody>
        </table>
      </div>
    <div class="trainlog">
        <h4>{{Flaskdata.data }}</h4>
    </div>
    </div>
  </template>
  
  <script>
  import Papa from 'papaparse';
  import * as XLSX from 'xlsx';
  import axios from 'axios';
  const web_api_url = 'http://192.168.110.110:7500';
  export default {
    async created(){
      await this.createFetching()
    },
    data() {
      return {
        data: [],
        columns: [],          // 用於儲存 CSV 中的欄位名稱
        selectedColumns: {},  // 用於儲存欄位的勾選狀態
        selectedColumnsArray:[],
        uploadedFile: null,  // 存儲上傳文件
        isLoading: false,  // 默認為false
        isWatchData:false,
        isServerReturn: false,
        dataTable: [],
        Flaskdata: {},
        isTraining:false,
        fetchInterval: null,  // 用於存儲定期抓取的ID
        isTrained: false,
      }
    },
    methods: {
        handleFileChange(event) {
        this.uploadedFile = event.target.files[0];
        if (this.uploadedFile.name.includes('csv')) {
          let hasExtractedColumns = false;
          Papa.parse(this.uploadedFile, {
            chunk: (results,parser) => {
              if (!hasExtractedColumns) {
                this.columns = results.data[0];
                console.log("Column Names:", this.columns);
                hasExtractedColumns = true;
                
                // 中止解析
                parser.abort();
              }
            },
            complete: () => {
              console.log("Column Names:", this.columns); // assuming first row is header
            }
          });
        }
        else if (this.uploadedFile.name.includes('xl')) {
          const reader = new FileReader();
          
          reader.onload = (e) => {
            const data = e.target.result;
            const workbook = XLSX.read(data, { type: 'binary' });
            
            // Assuming first sheet and first row is header
            const firstSheetName = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[firstSheetName];
            const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
            this.columns = jsonData[0]
          };
          reader.readAsBinaryString(this.uploadedFile);
          }
          else {
              alert("請上傳CSV或Excel文件！");
            }
        },async handleSubmit() {
        this.selectedColumnsArray = Object.keys(this.selectedColumns).filter(column => this.selectedColumns[column]);
        if (!this.uploadedFile) {
            alert("請先選擇文件");
            return;
          }
  
          if (this.selectedColumnsArray.length != 2) {
            alert("請選擇2個欄位!");
            return;
          }
  
          // 使用FormData來上傳文件和列名
          const formData = new FormData();
          formData.append('file', this.uploadedFile);
          formData.append('columns', this.selectedColumnsArray);
          // 開始上傳
          this.isLoading = true;
          try {
            const response = await fetch(web_api_url+'/upload_train_data/', { // 替換為你的服務器端點
              method: 'POST',
              body: formData
            });
            if (response.ok) {
              alert('文件上傳成功！');
              console.log(response); // 處理来自服務器的響應
            } else {
              alert('文件上傳失敗:' + response.message);
            }
          } catch (error) {
            console.error("上傳錯誤:", error);
            alert('上傳過程中出現錯誤，請重試！');
          } finally {
            this.isLoading = false;  // 結束上傳
            this.isServerReturn = true;
          }
      },async WatchData() {
        this.isWatchData = !this.isWatchData;
  
        if (this.isWatchData) {
          try {
            const response = await fetch(web_api_url+'/return_train_data/');
            const data = await response.json();
  
            // 假設API返回的是一个標準的JSON格式的DataFrame
            this.dataTable = data;
  
          } catch (error) {
            console.error("Error loading data:", error);
          }
        }
      },async StartTrain(){
        if (this.isTraining){
          alert('訓練進行中，需中斷再重啟訓練。');
        }
        else{
          try{
            const response = await axios.get(web_api_url+'/train/');
            // const data = await response.json();
            console.log("StartTrain data:", response.data);
          } 
          catch (error) {
            console.error("Error loading data:", error);
          }
        }
        
      },async StopTrain(){
        try{
          const response = await axios.get(web_api_url+'/stop_training/');
          console.log("Stop Training data:", response.data);
        } 
        catch (error) {
          console.error("Error loading data:", error);
        }
      },fetchData() {
        axios.get(web_api_url+'/get_train_log')
          .then(response => {
            this.Flaskdata = response.data;
            if (response.data['trained']===true){
              this.isTrained = true;
            }
            this.isTraining = response.data['training'];
          });
      },createFetching() {
        this.fetchData();
        this.fetchInterval = setInterval(this.fetchData, 1000);
      }
    }
  }
  </script>
  
  <style>
  h3 {
    margin-top: 20px;
  }


  /* 你可以加入些基本的樣式，讓表格看起來更整齊 */
  table {
    margin-top: 10px;
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
    width: 500px;
    margin-left: auto;
    margin-right: auto;
  }
  
  th, td {
    border: 1px solid #ddd;
    padding: 8px;
  }
  
  th {
    background-color: #f2f2f2;
  }
  .loading-overlay {
    position: fixed;   /* 全屏覆盖 */
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(255, 255, 255, 0.8);  /* 半透明的白色背景 */
    display: flex;  /* 使用 Flexbox */
    justify-content: center;  /* 水平居中 */
    align-items: center;  /* 垂直居中 */
    z-index: 1000;  /* 保證在最前面 */
  }
  
  .loading-image {
    max-width: 400px;  /* 或其他合適的大小 */
    max-height: 400px;
  }
  
  .submit-button {
    background: linear-gradient(to bottom, #b0b0b0, #d9d8d8); /* 灰色漸變從較亮到較暗 */
    color: rgb(4, 4, 4);  /* 文本顏色為白色 */
    border: none;  /* 去除邊框 */
    padding: 10px 20px;  /* 添加一些內邊距 */
    border-radius: 5px;  /* 輕微的圓角 */
    cursor: pointer;  /* 鼠標懸停時顯示手形 */
    transition: 0.3s;  /* 平滑的過渡效果 */
    margin-bottom: 20px;
  }
  
  /* 當屬標懸停在按鈕上時，為其應用一個稍微亮一些的漸變背景 */
  .submit-button:hover {
    background: linear-gradient(to bottom, #c0c0c0, #d9d8d8);
  }
  
  /* 如果你還想在按鈕被點擊時有樣式變化，可以添加以下樣式 */
  .submit-button:active {
    background: linear-gradient(to bottom, #dedede, #b0b0b0); /* 顏色轉變 */
  }
  </style>