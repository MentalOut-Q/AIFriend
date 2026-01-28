<script setup>

import NavBar from "@/components/navbar/NavBar.vue";
</script>

<template>
    <NavBar>
        <RouterView/> <!--根据url在router的index.js里面找, 把对应的Index渲染出来-->
    </NavBar>
</template>

<style scoped>

</style>
