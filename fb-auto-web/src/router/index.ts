import {
  createRouter,
  createWebHistory,
  type RouteRecordRaw,
} from "vue-router";

import accountDecode from "./account-decode";
import configManage from "./config-manage";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    redirect: "/account-decode",
  },
  accountDecode,
  configManage,
  {
    path: "/:catchAll(.*)",
    redirect: "/account-decode",
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  next();
});

export default router;
