<template>
  <nav>
    <router-link to="/">首頁</router-link> |
    <router-link to="/train">詞彙向量化模型訓練</router-link>|
    <router-link to="/UpdateVectorDB">建立詞彙向量資料庫</router-link> |
    <!-- <router-link to="/KeywordRecommend">同義詞搜尋</router-link> | -->
    <router-link to="/AddNewSynonyms">建立同義詞庫</router-link> |
  </nav>
  <router-view/>
</template>
<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}

nav {
  padding: 30px;
}

nav a {
  font-weight: bold;
  color: #2c3e50;
}

nav a.router-link-exact-active {
  color: #42b983;
}
</style>
