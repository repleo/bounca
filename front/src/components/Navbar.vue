<template>
  <ul class="navbar" id="navbar">
    <li><router-link to="/logout">logout</router-link></li>
    <li><router-link to="/about">about</router-link></li>
  </ul>
</template>

<script>
export default {
  name: 'navbar',
};
</script>

<style scoped>
ul {
  list-style-type: none;
  margin: 0;
  padding: 0;
  overflow: hidden;
}

li {
  display: inline;
  float: right;
}

a {
  color: #1a1a1a;
  display: inline-block;
  text-align: center;
  padding: 6px 12px;
  text-decoration: none;
  font-size: 14px;
}

a:hover {
  color: #cc0000;
  text-decoration: none;
}
</style>
