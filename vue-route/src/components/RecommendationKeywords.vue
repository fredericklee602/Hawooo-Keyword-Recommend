<template>
    <div>
      <h4>關鍵字[{{ keyword }}]之候選同義詞</h4>
      <!-- Input for adding new data -->
      <div>
        <input v-model="newData" placeholder="手動新增同義詞..." />
        <button @click="addData">新增同義詞</button>
        <button @click="SubmitRecommend" >上傳選取同義</button>
      </div>
      <table>
        <thead>
            <tr>
                <th>選取</th>
                <th>關鍵字</th>
                <th >刪除</th>
            </tr>
        </thead>
        <tbody>
          <tr v-for="recommended in recommendKeywords_list" :key="recommended">
            <td><input type="checkbox" v-model="selectedColumns[recommended]"></td>
            <td>{{ recommended }}</td>
            <td><button @click="removeKeywordrequest(recommended)">Delete</button></td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  
  <script>
  // const web_api_url = 'http://127.0.0.1:5000';
  export default {
    data(){
        return{
            newData: '',
            selectedColumns:{}
        }
    },
    props: {
      keyword: String,
      recommendKeywords_list: Array
    },
    methods: {
      removeKeywordrequest(keyword) {
        this.$emit('update-keyword', keyword);
      },
      addData() {
        if (this.newData) {
          this.$emit('update-newData', this.newData);
          // console.log("this.selectedColumns",this.selectedColumns)
        }
      },
      async SubmitRecommend() {
        this.selectedColumnsArray = Object.keys(this.selectedColumns).filter(column => this.selectedColumns[column]);
        this.$emit('synonymsArray', this.selectedColumnsArray);
        this.selectedColumns = {};
      }
    }
  };
  </script>

<style scoped>
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
</style>