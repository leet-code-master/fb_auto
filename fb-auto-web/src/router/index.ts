import {
  createRouter,
  createWebHistory,
  type RouteRecordRaw,
} from "vue-router";

import AccountDecoding from "@/views/AccountDecoding/index.vue";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    component: AccountDecoding,
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
