<template>
    <div> 
      <div v-if="!start_recommned">
          <table  v-if="VBTables.length">
              <thead>
                  <tr>
                      <th>選取</th>
                      <th>向量數據庫Table</th>
                  </tr>
              </thead>
              <tbody>
                  <tr v-for="item in VBTables"  :key="item">
                      <td><input type="checkbox" v-model="VBselectedColumns[item]"></td>
                      <td>{{ item }}</td>
                  </tr>
              </tbody>
          </table>
          <button class="submit-button" @click="StartRecommend" v-if="VBTables.length">選取向量資料庫，推薦同義詞</button>
      </div>
        <div v-if="start_recommned">
          <div class="searchMessages" v-for="(msg, index) in messages" :key="index">
            <div :class="[msg.type, 'boxed']">{{ msg.content }}</div>
          </div>
          <input type="text" v-model="userMessage" @keyup.enter="sendMessage">
          <button @click="sendMessage">Send</button>
        </div>
    </div>
</template>

<script>
const web_api_url = 'http://192.168.110.110:7500';
export default {
    async created(){
      this.vectorDB_info();
    },
    data() {
      return {
        VBTables: { attributeName: 'array'  // 初始化屬性
                    },
        VBselectedColumns: {},
        userMessage: "",
        messages: [],
        start_recommned : false
      }
    },
    methods: {
      async vectorDB_info() {
        try{
          this.isWatchData = false;
          const response = await fetch(web_api_url+'/return_table_information/');
          const data = await response.json();
          this.VBTables = data["vectorDB_table_name"];
          // console.log("return_table_information:", data["vectorDB_table_name"]);
        } 
        catch (error) {
          console.error("Error loading data:", error);
        }
      },async StartRecommend() {
        this.VBselectedColumnsArray = Object.keys(this.VBselectedColumns).filter(column => this.VBselectedColumns[column]);
        if (this.VBselectedColumnsArray.length != 1) {
          alert("請選擇1個欄位!");
          return;
        }
        try{
          this.start_recommned = true;
        } 
        catch (error) {
          console.error("Error loading data:", error);
        }
      },async sendMessage() {
        this.messages = []
        this.messages.push({ type: "user", content: this.userMessage });

        const response = await fetch(web_api_url+"/recommend_keywords/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ message: this.userMessage,'class':this.VBselectedColumnsArray }),
        });

        const data = await response.json();

        this.messages.push({ type: "bot", content: data.reply });
        this.userMessage = "";
      },async StartUpdateVDB(){
        this.VBselectedColumnsArray = Object.keys(this.VBselectedColumns).filter(column => this.VBselectedColumns[column]);
        // console.log("VBselectedColumnsArray", this.VBselectedColumnsArray);
  
        if (this.VBselectedColumnsArray.length != 1) {
          alert("請選擇1個欄位!");
          return;
        }

        // 使用FormData來上傳文件和列名
        const formData = new FormData();
        formData.append('VBTable_name', this.VBselectedColumnsArray);
        // console.log("formData", formData);
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
  .user {
  color: blue;
  }
  .bot {
    color: green;
  }
  .chat-room {
    display: flex;
    flex-direction: column;
    height: 100vh;
  }

  .messages {
    flex: 1;
    overflow-y: auto;
  }

  .input-area {
    display: flex;
    padding: 1rem;
  }

  input {
    flex: 1;
    padding: 0.5rem;
    margin-right: 0.5rem;
  }

  button {
    padding: 0.5rem 1rem;
    margin-top: 50px;
    margin-bottom: 50px;
  }
  .searchMessages{
    margin-top: 50px;
    margin-bottom: 50px;
  }
  .boxed {
    width: 30%;  /* 或者你可以设置为其他宽度值，例如 200px */
    border: 1px solid #ccc;  /* 灰色边框 */
    padding: 10px;
    background-color: white;  /* 白色背景 */
    border-radius: 4px;
    margin-bottom: 10px;
    box-sizing: border-box;  /* 这确保宽度包括内边距和边框 */
    /* ... 其他样式 ... */
    margin-left: auto;
    margin-right: auto;
  }
</style>