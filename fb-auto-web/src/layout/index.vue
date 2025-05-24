<template>
  <a-layout>
    <a-layout-header :style="headerStyle">
      <a-menu
        v-model:selectedKeys="selectedKeys"
        theme="dark"
        mode="horizontal"
      >
        <a-menu-item :key="1">账号解码</a-menu-item>
      </a-menu>
    </a-layout-header>
    <a-layout-content :style="contentStyle">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" :key="$route.path" />
        </transition>
      </router-view>
    </a-layout-content>
  </a-layout>
</template>
<script lang="ts" setup>
import { ref, type CSSProperties } from "vue";

const selectedKeys = ref<number[]>([1]);
const headerStyle: CSSProperties = {
  position: "fixed",
  zIndex: "1",
  width: "100%",
};
const contentStyle: CSSProperties = {
  backgroundColor: "#f8f8f8",
  marginTop: "64px",
  padding: "16px",
  height: "calc(100vh - 64px)",
  overflowY: "auto",
};
</script>
