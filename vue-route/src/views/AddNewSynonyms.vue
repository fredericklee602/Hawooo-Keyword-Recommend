<template>
    <div class="pipline">
    <!-- 加載指示器 -->
    <div v-if="isLoading" class="loading-overlay">
      <img src="/jumpingsheep.gif" alt="上傳中..." class="loading-image"/>
    </div>
     <div class="piplinestep">
     <h3 >Step1：自訂或點擊關鍵字</h3>
      <div>
        <input v-model="input_text" placeholder="自訂關鍵字" @keyup.enter="showRecommendations(input_text)" />
        <button @click="showRecommendations(input_text)">送出</button>
      </div>

      <div class="radiobutton">
        <div>
          <label>
            <input type="radio" value="lastKeywords" v-model="radioselectedOption" @change="KeywordsData"/> 剛上傳關鍵字
          </label>
        </div>
        <div>
          <label>
            <input type="radio" value="VectorDBKeywords" v-model="radioselectedOption" @change="KeywordsData"/> 向量資料庫關鍵字
          </label>
        </div>
      </div>

      <table class="step1-table">
        <thead>
          <tr>
              <th>序號</th>
              <th>關鍵字集合</th>
              <th v-if="radioselectedOption=='VectorDBKeywords'" >刪除</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="keyword in paginatedKeywords[currentPage]" :key="keyword">
            <td >{{ keyword.index + 1}}</td>
            <td class="clickable" @click="showRecommendations(keyword.Keywords)">{{ keyword.Keywords }}</td>
            <td v-if="radioselectedOption=='VectorDBKeywords'" ><button @click="removeKeyword(keyword.Keywords)">Delete</button></td>
          </tr>
        </tbody>
      </table>
      <div class="PageControl">
        <button id="prevPage1" @click="prevPage($event)">上一頁</button>
        <input id="pagenumber1" class="pagenumber" type="number" v-model.number="inputPage" @change="goToPage" />
        /{{ totalPages }}
        <button id="nextPage1" @click="nextPage($event)">下一頁</button>
      </div>
     </div>
     <div class="piplinestep">
     <h3 >Step2：選取多個同義詞，並提交同義詞庫</h3>
      <RecommendationKeywords @update-keyword="removeRecommandKeyword" @update-newData="AddSynonyms" @synonymsArray="SubmitRecommend" class="step2-table" v-if="showRecommendationsTable" :keyword="selectedKeyword" :recommendKeywords_list="recommendKeywords_list" />
     </div>
     <div class="piplinestep">
     <h3 >Step3：同義詞庫</h3>
     <table class="step3-table">
        <thead>
            <tr>
              <th>關鍵字</th>
              <th>同義詞</th>
            </tr>
        </thead>
        <tbody>
          <tr v-for="synonyms in synonyms_list" :key="synonyms">
            <td >{{ synonyms.keyword }}</td>
            <td >{{ synonyms.similarity_keywords }}</td>
          </tr>
        </tbody>
      </table>
      <div class="PageControl">
        <button id="prevPage2" @click="prevPage($event)">上一頁</button>
        <input id="pagenumber2" class="pagenumber" type="number" v-model.number="inputPage2" @change="goToPage" />
        /{{ totalPages2 }}
        <button id="nextPage2" @click="nextPage($event)">下一頁</button>
      </div>
      <!-- <button class="submit-button" @click="synonymsData" >更新顯示同義詞庫</button> -->
     </div>
    </div>
</template>

<script>
const web_api_url = 'http://192.168.110.110:7500';
import RecommendationKeywords from '@/components/RecommendationKeywords.vue';
export default {
    components: {
      RecommendationKeywords
    },
    async created(){
      await this.KeywordsData(),
      await this.synonymsData()
    },
    data() {
      return {
        isLoading: false,  // 默認為false
        radioselectedOption:'lastKeywords',
        input_text:'',
        keywords: [],
        lastkeywords: [],
        VDBkeywords:[],
        currentPage: 0,
        currentPage2: 0,
        selectedKeyword: '',
        showRecommendationsTable: false,
        recommendKeywords_list: [],
        synonyms_list:[],
        inputPage: 1,
        inputPage2: 1
      }
    },
    computed: {
      paginatedKeywords() {
        let pageSize = 15;
        return Array.from({ length: Math.ceil(this.keywords.length / pageSize) }, (_, i) =>
          this.keywords.slice(i * pageSize, i * pageSize + pageSize)
        );
      },
      paginatedSynonyms() {
        let pageSize = 15;
        return Array.from({ length: Math.ceil(this.synonyms_list.length / pageSize) }, (_, i) =>
          this.synonyms_list.slice(i * pageSize, i * pageSize + pageSize)
        );
      },
      totalPages() {
        return this.paginatedKeywords.length;
      },
      totalPages2() {
        return this.paginatedSynonyms.length;
      }
    },
    methods: {
        async AddSynonyms(Synonyms){
          const Synonyms_array = []
          Synonyms_array.push(Synonyms);
          if (Synonyms_array == 0) {
            alert("請確定輸入完整字串");
            return;
          }
          // 使用FormData來上傳文件和列名
          const formData = new FormData();
          formData.append('keyword', this.selectedKeyword);
          formData.append('synonyms', Synonyms);
          // 開始上傳
          try {
            const response = await fetch(web_api_url+'/synonyms_write/', { 
              method: 'POST',
              body: formData
            });
            this.synonymsData()
            if (response.ok) {
              alert('文件上傳成功！');
            } else {
              alert('文件上傳失敗:' + response.message);
            }
          } catch (error) {
            console.error("上傳錯誤:", error);
            alert('上傳過程中出現錯誤，請重試！');
          }
        },
        async removeKeyword(keyword) {
          this.isLoading = true;  // 結束
          const formData = new FormData();
          formData.append('keyword', keyword);
          // this.isLoading = true;
          try{
            const response = await fetch(web_api_url+'/remove_keyword_on_VectorDB/', { 
              method: 'POST',
              body: formData
            });
            // const data = await response.json();
            if (response.ok) {
              this.keywords = this.keywords.filter(k => k.Keywords !== keyword);
              this.recommendKeywords_list = this.recommendKeywords_list.filter(k => k !== keyword);
              this.VDBkeywords = this.VDBkeywords.filter(k => k !== keyword);
            }
          }
          catch (error) {
            console.error("Error loading data:", error);
          } finally {
              this.isLoading = false;  // 結束
          }
        },
        async removeRecommandKeyword(keyword) {
          this.isLoading = true;  // 結束
          const formData = new FormData();
          formData.append('keyword', keyword);
          // this.isLoading = true;
          try{
            const response = await fetch(web_api_url+'/remove_keyword_on_VectorDB/', { 
              method: 'POST',
              body: formData
            });
            // const data = await response.json();
            if (response.ok) {
              this.keywords = this.keywords.filter(k => k.Keywords !== keyword);
              this.recommendKeywords_list = this.recommendKeywords_list.filter(k => k !== keyword);
              this.VDBkeywords = this.VDBkeywords.filter(k => k !== keyword);
            }
          }
          catch (error) {
            console.error("Error loading data:", error);
          } finally {
              this.isLoading = false;  // 結束
          }
        },
        async showRecommendations(keyword) {
            this.isLoading = true;
            this.selectedKeyword = keyword;
            this.showRecommendationsTable = true;
            const formData = new FormData();
            formData.append('message', this.selectedKeyword);
            formData.append('class', ["Hawoo_Keywords"]);
            const response = await fetch(web_api_url+'/recommend_keywords_list/', { // 替換為你的服務器端點
            method: 'POST',
            body: formData
            });

            const data = await response.json();
            this.recommendKeywords_list = data.reply
            this.isLoading = false;
        },
        prevPage(event) {
          let clickedButtonid = event.target.id;
          // console.log(clickedButtonid);
          switch (clickedButtonid) {
            case "prevPage1":
              if (this.currentPage > 0) {
                this.currentPage--;
                this.inputPage = this.currentPage + 1; // Adjust for user understanding
              }
              break
            case "prevPage2":
              if (this.currentPage2 > 0) {
                this.currentPage2--;
                this.inputPage2 = this.currentPage2 + 1; // Adjust for user understanding
              }
              break
          }
        },
        nextPage(event) {
          let clickedButtonid = event.target.id;
          // console.log(clickedButtonid);
          switch (clickedButtonid) {
            case "nextPage1":
              if (this.currentPage < this.totalPages - 1) {
                  this.currentPage++;
                  this.inputPage = this.currentPage + 1; // Adjust for user understanding
              }
              break
            case "nextPage2":
              if (this.currentPage2 < this.totalPages2 - 1) {
                  this.currentPage2++;
                  this.inputPage2 = this.currentPage2 + 1; // Adjust for user understanding
              }
              break
          }
        },
        goToPage(event) {
          let inputpageid = event.target.id;
          switch (inputpageid) {
            case "pagenumber1":
              if (this.inputPage > 0 && this.inputPage <= this.totalPages) {
                  this.currentPage = this.inputPage - 1; // Adjust for 0-based index
              }
              break
            case "pagenumber2":
              if (this.inputPage2 > 0 && this.inputPage2 <= this.totalPages2) {
                  this.currentPage2 = this.inputPage2 - 1; // Adjust for 0-based index
              }
              break
          }
        },async KeywordsData() {
          try {
            const response = await fetch(web_api_url+'/return_keywords_data_all/');
            const data = await response.json();

            // 假設API返回的是一个標準的JSON格式的DataFrame
            this.lastkeywords = data.lastdataframe;
            this.VDBkeywords = data.VDBdataframe;
            if (this.radioselectedOption=='lastKeywords'){
              this.keywords = this.lastkeywords;
            }
            if (this.radioselectedOption=='VectorDBKeywords'){
              this.keywords = this.VDBkeywords;
            }
          } catch (error) {
            console.error("Error loading data:", error);
          }        
      },async synonymsData() {
        try {
          const response = await fetch(web_api_url+'/synonyms_base/');
          const data = await response.json();

          // 假設API返回的是一个標準的JSON格式的DataFrame
          this.synonyms_list = data.dataframe;

        } catch (error) {
          console.error("Error loading data:", error);
        }        
      },
      async SubmitRecommend(synonymsArray) {
  
        if (synonymsArray.length == 0) {
          alert("請選擇1或1以上的欄位數量");
          return;
        }  
        // 使用FormData來上傳文件和列名
        const formData = new FormData();
        formData.append('keyword', this.selectedKeyword);
        formData.append('synonyms', synonymsArray);
        // 開始上傳
        try {
          const response = await fetch(web_api_url+'/synonyms_write/', { 
            method: 'POST',
            body: formData
          });
          this.synonymsData()
          if (response.ok) {
            alert('文件上傳成功！');
          } else {
            alert('文件上傳失敗:' + response.message);
          }
        } catch (error) {
          console.error("上傳錯誤:", error);
          alert('上傳過程中出現錯誤，請重試！');
        }
      }
    }
}
</script>
<style scoped>
.radiobutton{
  display: flex;
}
.pipline {
    display: flex;
    border-radius: 10px;
    margin-left: 20px; /* 調整數值以獲得所需的間距 */
    margin-right: 20px; /* 調整數值以獲得所需的間距 */
}
.piplinestep {
    margin-left: 50px; /* 調整數值以獲得所需的間距 */
    margin-right: 50px; /* 調整數值以獲得所需的間距 */
}
.step1-table{
    margin-top: 10px;
    margin-bottom: 0px;
}
.pagenumber{
  margin-top: 0px;
  max-width: 60px;
  max-height: 15px;
  margin-left: 10px; /* 調整數值以獲得所需的間距 */
  margin-right: 10px; /* 調整數值以獲得所需的間距 */
}
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
.PageControl{
  margin-top: 10px;
  margin-bottom: 10px;
}
/* 使得詞彙看起來像是可點擊的 */
.clickable {
  cursor: pointer;
  color: blue; /* 讓文字為藍色，使其更像是一個連結 */
  text-decoration: underline; /* 加上底線 */
}

.clickable:hover {
  background-color: #f5f5f5; /* 滑鼠滑過時的背景色 */
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
</style>