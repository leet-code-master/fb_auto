import Layout from "@/layout/index.vue";

export default {
  path: "/",
  component: Layout,
  name: "config",
  meta: {
    title: "配置管理",
  },
  children: [
    {
      path: "config-manage",
      component: () => import("@/views/config-manage/index.vue"),
      name: "config-manage",
    },
  ],
};
