<template>
  <a-layout>
    <a-layout-header :style="headerStyle">
      <a-menu
        v-model:selectedKeys="selectedKeys"
        mode="horizontal"
        :items="menuItems"
        @click="handleClickMenu"
      />
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
import { h, ref, watch, type CSSProperties } from "vue";
import { FacebookOutlined, SettingOutlined } from "@ant-design/icons-vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();
const selectedKeys = ref<number[]>(["/account-decode"]);
const headerStyle: CSSProperties = {
  position: "fixed",
  zIndex: "1",
  width: "100%",
  backgroundColor: "#fff",
};
const contentStyle: CSSProperties = {
  backgroundColor: "#f8f8f8",
  marginTop: "64px",
  padding: "16px",
  height: "calc(100vh - 64px)",
  overflowY: "auto",
};

const menuItems = ref<MenuProps["items"]>([
  {
    key: "/account-decode",
    label: "账号解码",
    title: "账号解码",
    icon: () => h(FacebookOutlined),
  },
  {
    key: "/config-manage",
    label: "配置管理",
    title: "配置管理",
    icon: () => h(SettingOutlined),
  },
]);

watch(
  () => route.path,
  (val) => {
    selectedKeys.value = [val];
  },
  {
    immediate: true,
  }
);

const handleClickMenu = (e) => {
  router.push(e.key);
};
</script>
