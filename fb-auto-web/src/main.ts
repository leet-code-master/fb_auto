import { createApp } from "vue";
import App from "./App.vue";
import Antd from "ant-design-vue";
import "ant-design-vue/dist/reset.css";
import router from "./router";
import "@/style/index.css";

// pinia
import { createPinia } from "pinia";
// pinia中数据持久化
import piniaPluginPersistedstate from "pinia-plugin-persistedstate";

const pinia = createPinia();
pinia.use(piniaPluginPersistedstate);

const app = createApp(App);

app.use(Antd).use(router).use(pinia).mount("#app");
