<template>
  <div class="Description">
    <h1>{{ msg }}</h1>
  <div class="pipline">
    <div class="piplinestep">
      <h3><router-link to="/train">詞彙向量化模型訓練</router-link></h3>
      <p >
        1. 上傳產品中英文名稱，以進行模型訓練(csv,xlsx)<br>
        2. 選取中英文名稱欄位(2)<br>
        3. 點選submit<br>
        4. 資料上傳完成後，開始訓練<br>
      </p>
    </div>
    <div class="piplinestep">
      <h3><router-link to="/UpdateVectorDB">建立詞彙向量資料庫</router-link></h3>
      <p >
        1. 上傳需要的關鍵字<br>
        2. 選取關鍵字欄位(1)<br>
        3. 將所有關鍵字轉成向量後，匯入Vector Data Base<br>
      </p>
    </div>
    <!-- <div class="piplinestep">
      <h3><router-link to="/KeywordRecommend">同義詞搜尋</router-link></h3>
      <p>
        1.根據指定的關鍵詞，找出潛在同義詞<br>
      </p>
    </div> -->
    <div class="piplinestep">
      <h3><router-link to="/AddNewThesaurus">建立同義詞庫</router-link></h3>
      <p>
        1.點選列表關鍵字<br>
        2.推薦相似詞彙<br>
        3.選取相似詞，匯入同義詞庫<br>
      </p>
    </div>
  </div>
  </div>
</template>

<script>
export default {
  name: 'WebsiteDescription',
  props: {
    msg: String
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
.Description {
    display: grid;
    place-items: center; /* 水平和垂直置中 */
}
.pipline {
    display: flex;
    border: 2px solid rgb(112, 68, 208);
    border-radius: 10px;
}
.piplinestep {
    margin-left: 50px; /* 調整數值以獲得所需的間距 */
    margin-right: 50px; /* 調整數值以獲得所需的間距 */
}
h3 {
  margin: 40px 0 0;
  border-bottom: 2px solid rgb(112, 68, 208);
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
h3 {
  text-align: left;
}
p {
  text-align: left;
}
</style>
