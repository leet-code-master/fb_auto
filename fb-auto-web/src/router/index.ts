import {
  createRouter,
  createWebHistory,
  type RouteRecordRaw,
} from "vue-router";

import decode from "./account-decode/index.ts";

const routes: Array<RouteRecordRaw> = [
  decode,
  // {
  //   path: "/decode",
  //   component: AccountDecoding,
  // },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  next();
});

export default router;
