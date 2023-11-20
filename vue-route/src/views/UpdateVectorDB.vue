<template>
  
  <div>
    <!-- 加載指示器 -->
    <div v-if="isLoading" class="loading-overlay">
      <img src="/jumpingsheep.gif" alt="上傳中..." class="loading-image"/>
      <!-- <h4>{{Flaskdata.data }}</h4> -->
    </div>
    <!-- 第一部分 -->
    <!-- <div v-if="isServerReturn==false" class="First-Part"> -->
    <div class="First-Part">
      
      <h3 class="title_description">
        上傳產品關鍵字資料(csv,xlsx)
      </h3>
      <input type="file" @change="handleFileChange">
      <button class="loadData-button" @click="WatchKeywordsData">觀看前處理資料</button>
      <button class="update-vectorDB-button" @click="vectorDB_info">新增或更新Keywords向量資料庫</button>
      <button class="delete-VectorDB" @click="deleteVectorDB">刪除向量資料庫</button>

      <!-- 呈現欄位名稱的表格 -->
      <div v-if="columns.length">
        <h3 class="title_description">
          選取1個Keywords對應欄位
        </h3>
        <table v-if="columns.length">
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
      </div>
      <button class="submit-button" @click="handleSubmit" v-if="columns.length">提交選取欄位</button>
    </div>
    
    <!-- 第二部分 -->
    <!-- <div v-if="isServerReturn" class="Part2"> -->
      <!-- 按鈕加載數據 -->
      <!-- <button class="loadData-button" @click="WatchKeywordsData">觀看前處理資料</button>
      <button v-if="isFetching==false" class="update-vectorDB-button" @click="vectorDB_info">新增或更新Keywords向量資料庫</button> -->
      <!-- <button class="delete-VectorDB" @click="deleteVectorDB">刪除向量資料庫</button> -->
    <table v-if="isWatchData">
      <thead>
        <tr>
          <!-- 假設你知道你的DataFrame的列名 -->
          <th>Keywords</th>
          <!-- ... 其他列名 ... -->
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in dataTable" :key="row.id">
          <td>{{ row['Keywords'] }}</td>
          <!-- ... 其他數據列 ... -->
        </tr>
      </tbody>
    </table>
    <table v-if="isWatchData">
          <tr>
              <th>Keywords總數量</th>
          </tr>
          <tbody>
              <tr>
                  <td>{{ keywordcount }}</td>
              </tr>
          </tbody>
      </table>
    <!-- </div> -->

    <!-- 第三部分 -->
    <!-- <div v-if="isPart3" class="Part3"> -->
      <!-- <table  v-if="VBTables.length">
          <thead>
              <tr>
                  <th>Select</th>
                  <th>Vector DB Table Name</th>
              </tr>
          </thead>
          <tbody>
              <tr v-for="item in VBTables"  :key="item">
                  <td><input type="checkbox" v-model="VBselectedColumns[item]"></td>
                  <td>{{ item }}</td>
              </tr>
          </tbody>
      </table> -->
      <!-- <input type="text" v-model="newVBData" placeholder="Enter new data">
      <button @click="addData">Add New Table Name</button> -->
    <!-- </div> -->
    <button class="submit-button" @click="toggleFetching" v-if="VBTables.length">開始更新VectorDB</button>
    <div v-if="isFetching | isOver" class="insertVectorDBlog">
        <h4>{{Flaskdata.data }}</h4>
    </div>
  </div>
</template>
<script>
  import Papa from 'papaparse';
  import * as XLSX from 'xlsx';
  import axios from 'axios';
  const web_api_url = 'http://127.0.0.1:7500';
  export default {
    data() {
      return {
        data: [],
        columns: [],          // 用於儲存 CSV 中的欄位名稱
        selectedColumns: {},  // 用於儲存欄位的勾選狀態
        selectedColumnsArray:[],
        uploadedFile: null,  // 存儲上傳文件
        isServerReturn: false,
        isLoading: false,  // 默認為false
        isWatchData:false,
        dataTable: { attributeName: 'array'  // 初始化屬性
                    },
        keywordcount:0,
        VBTables: { attributeName: 'array'  // 初始化屬性
                    },
        // newVBData: '',
        isPart3: false,
        // VBselectedColumns: {},
        VBselectedColumnsArray: ["Hawoo_Keywords"],
        Flaskdata: {},
        isFetching:false,
        fetchInterval: null,  // 用於存儲定期抓取的ID
        isOver: false,
      }
    },
    methods: {
        handleFileChange(event) {
        this.uploadedFile = event.target.files[0];
        if (!this.uploadedFile){
          return
        }
        // if (this.uploadedFile.name.includes('csv')) {
        //   Papa.parse(this.uploadedFile, {
        //     complete: (results) => {
        //       this.data = results.data;
        //       this.columns = results.data[0];
        //     }
        //   });
        // }
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
  
          if (this.selectedColumnsArray.length != 1) {
            alert("請選擇1個欄位!");
            return;
          }
  
          // 使用FormData來上傳文件和列名
          const formData = new FormData();
          formData.append('file', this.uploadedFile);
          formData.append('columns', this.selectedColumnsArray);
          // 開始上傳
          this.isLoading = true;
          try {
            const response = await fetch(web_api_url+'/upload_keywords_data/', { // 替換為你的服務器端點
              method: 'POST',
              body: formData
            });
            if (response.ok) {
              alert('文件上傳成功！');
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
      },async WatchKeywordsData() {
        this.isWatchData = !this.isWatchData;
  
        if (this.isWatchData) {
          try {
            const response = await fetch(web_api_url+'/return_keywords_data/');
            const data = await response.json();
  
            // 假設API返回的是一个標準的JSON格式的DataFrame
            this.dataTable = data.dataframe;

            this.keywordcount = data.keywords_count;
  
          } catch (error) {
            console.error("Error loading data:", error);
          }
        }
      },async deleteVectorDB(){
        if (window.confirm('確定要刪除向量資料庫嗎？')) {
          const formData = new FormData();
          formData.append('VBTable_name', this.VBselectedColumnsArray);
          this.isLoading = true;
          try{
            const response = await fetch(web_api_url+'/remove_vector_table/', { // 替換為你的服務器端點
              method: 'POST',
              body: formData
            });
            const data = await response.json();
            if (response.ok) {
              if (data.isRemoved==true){alert('Vector DB刪除成功');}
              if (data.isRemoved==false){alert('Vector DB原本就不存在');}
            } else {
              alert('Vector DB刪除發生異常:' + response.message);
            }
            console.log("Delete vector DB:", data);
          } 
          catch (error) {
            console.error("Error loading data:", error);
          } finally {
              this.isLoading = false;  // 結束
              this.isFetching = false;
          }
        }
      },async StartUpdateVDB(){
  
        if (this.VBselectedColumnsArray.length != 1) {
          alert("請選擇1個欄位!");
          return;
        }

        // 使用FormData來上傳文件和列名
        const formData = new FormData();
        formData.append('VBTable_name', this.VBselectedColumnsArray);
        
        this.isFetching = !this.isFetching;   
        try{
          const response = await fetch(web_api_url+'/update_vector_DB/', { // 替換為你的服務器端點
            method: 'POST',
            body: formData
          });
          const data = await response.json();
          console.log("Start Update vector DB:", data);
        } 
        catch (error) {
          console.error("Error loading data:", error);
        }
      },async vectorDB_info() {
        try{
          this.isWatchData = false;
          const response = await fetch(web_api_url+'/return_table_information/');
          const data = await response.json();
          this.VBTables = data["vectorDB_table_name"];
          this.isPart3 = !this.isPart3;
        } 
        catch (error) {
          console.error("Error loading data:", error);
        }
      },async handleVBSubmit() {
        this.VBselectedColumnsArray = Object.keys(this.VBselectedColumns).filter(column => this.VBselectedColumns[column]);
  
        if (this.VBselectedColumnsArray.length != 1) {
          alert("請選擇1個欄位!");
          return;
        }

        // 使用FormData來上傳文件和列名
        const formData = new FormData();
        formData.append('VBTable_name', this.VBselectedColumnsArray);
        // console.log("formData", formData);
        // 開始上傳
        this.isLoading = true;
        try {
          const response = await fetch(web_api_url+'/update_vector_DB/', { // 替換為你的服務器端點
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
      // },addData() {
      //           if (this.newVBData) {
      //               this.VBTables.push(this.newVBData);
      //               this.newVBData = '';
      //           } else {
      //               alert('Please enter some data.');
      //           }
      },fetchData() {
        axios.get(web_api_url+'/get_vector_DB_log')
          .then(response => {
            this.Flaskdata = response.data;
            if (response.data['reload']===true){
              this.isFetching = false;
            }
            if (response.data['over']===true){
              this.isFetching = false;
              this.isOver = true;
            }
          });
      },toggleFetching() {
        this.StartUpdateVDB() 
        if (this.isFetching) {
          this.fetchData();
          this.fetchInterval = setInterval(this.fetchData, 1000);
        } else {
          clearInterval(this.fetchInterval);  // 如果不抓取, 則停止定期抓取
        }
      }
    }

  }
</script>

<style>
/* 加入些基本的樣式，讓表格看起來更整齊 */
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

  .submit-button{
    margin-top: 50px;
    margin-bottom: 50px;
  }
</style>