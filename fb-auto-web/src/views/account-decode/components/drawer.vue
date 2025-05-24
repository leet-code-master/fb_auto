<template>
  <a-drawer
    v-model:open="visible"
    title="账号列表"
    width="90%"
    placement="right"
    @close="handleClose"
  >
    <a-table
      :dataSource="dataSource"
      :columns="columns"
      :pagination="false"
      :scroll="{ y: 600 }"
    />
  </a-drawer>
</template>
<script lang="ts" setup>
import { computed } from "vue";
import type { AccountItem } from "@/types/account.type";

const props = defineProps<{
  open: boolean;
  data: AccountItem[];
}>();

const emits = defineEmits<{
  (e: "close", val: boolean): void;
}>();
const visible = computed({
  get() {
    return props.open;
  },
  set(val: boolean) {
    emits("close", val);
  },
});

const handleClose = () => {
  //   visible.value = false;
  emits("close", false);
};

const dataSource = computed(() => {
  return props.data;
});
const columns = [
  {
    title: "账号",
    dataIndex: "account",
    key: "account",
    width: 120,
    ellipsis: true,
  },
  {
    title: "密码",
    dataIndex: "password",
    key: "password",
    width: 120,
    ellipsis: true,
  },
  {
    title: "双重验证",
    dataIndex: "twoFA",
    key: "twoFA",
    width: 120,
    ellipsis: true,
  },
  {
    title: "邮箱",
    dataIndex: "email",
    key: "email",
    width: 120,
    ellipsis: true,
  },
  {
    title: "邮箱密码",
    dataIndex: "emailPassword",
    key: "emailPassword",
    width: 120,
    ellipsis: true,
  },
  {
    title: "辅助邮箱",
    dataIndex: "spareEmail",
    key: "spareEmail",
    width: 120,
    ellipsis: true,
  },
];
</script>
