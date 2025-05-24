import Layout from "@/layout/index.vue";

export default {
  path: "/",
  component: Layout,
  name: "account",
  meta: {
    title: "account",
  },
  children: [
    {
      path: "account-decode",
      component: () => import("@/views/account-decode/index.vue"),
      name: "accountList",
    },
  ],
};
