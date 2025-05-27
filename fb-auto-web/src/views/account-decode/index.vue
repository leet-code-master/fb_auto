<template>
  <div class="account-decode">
    <div class="account-decode-wrapper">
      <a-row :gutter="16">
        <a-col :span="12">
          <a-card title="导入字符串" :bordered="false">
            <template #extra>
              <a-flex gap="middle" justify="flex-end">
                <a-button @click="handleDecodeString"> 解码 </a-button>
                <a-button type="primary" @click="handleAddToQueue">
                  添加到队列
                </a-button>
              </a-flex>
            </template>
            <a-textarea
              v-model:value="accountInput"
              allow-clear
              placeholder="请输入账号字符串"
              :rows="10"
            />
          </a-card>
        </a-col>
        <a-col :span="12">
          <a-card title="配置" :bordered="false">
            <template #extra>
              <a-flex gap="middle">
                <a-button type="primary" @click="handleStart">启动</a-button>
                <!-- <a-progress type="circle" :percent="75" :size="30" /> -->
                <a-button type="primary" danger @click="handleTerminate">
                  终止
                </a-button>
              </a-flex>
            </template>
            <a-form :model="formState" :label-col="{ span: 4 }">
              <a-form-item label="进程数">
                <a-input-number v-model:value="formState.process" min="1" />
              </a-form-item>
              <a-form-item label="后台模式">
                <a-switch v-model:checked="formState.backMode" />
              </a-form-item>
              <a-form-item label="执行模块">
                <a-checkbox-group
                  v-model:value="formState.modules"
                  :options="modulesOptions"
                />
              </a-form-item>
              <a-form-item :wrapper-col="{ offset: 4 }">
                <a-progress :percent="progress" status="active" />
              </a-form-item>
            </a-form>
          </a-card>
        </a-col>
      </a-row>
    </div>
    <div class="account-table-wrapper">
      <a-card title="任务列表">
        <template #extra>
          <a-flex justify="space-between">
            <a-space>
              <a-button type="primary">
                <span>刷新</span>
                <ReloadOutlined />
              </a-button>
              <a-button>
                <span>导出</span>
                <ExportOutlined />
              </a-button>
              <a-button type="primary" danger>
                清空数据
                <DeleteOutlined />
              </a-button>
            </a-space>
          </a-flex>
        </template>
        <a-table
          rowKey="(record) => record.taskId)"
          :dataSource="dataSource"
          :columns="columns"
          :pagination:="false"
          :scroll="{ y: 600 }"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.dataIndex === 'status'">
              <a-tag>
                {{ record.status }}
              </a-tag>
            </template>
            <template v-if="column.dataIndex === 'operation'">
              <a-button type="link" danger> 删除 </a-button>
            </template>
          </template>
        </a-table>
      </a-card>
    </div>

    <Drawer
      :open="drawerVisible"
      :data="drawerData"
      @close="drawerVisible = false"
    />
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import type { UnwrapRef } from "vue";
import { message } from "ant-design-vue";
import Drawer from "./components/drawer.vue";
import { transformPipeString } from "@/utils";
import type { AccountItem } from "@/types/account.type";
import {
  ReloadOutlined,
  ExportOutlined,
  DeleteOutlined,
} from "@ant-design/icons-vue";

interface FormState {
  process: number;
  backMode: boolean;
  modules: number[];
}
interface DataSource {
  taskId: number;
  account: string;
  accountStr: string;
  status: string;
  logResult: string;
  updateTime: string;
}
const modulesOptions = [
  {
    label: "登陆",
    value: 1,
  },
  {
    label: "年份，性别，地区，好友",
    value: 2,
  },
  {
    label: "其他主页",
    value: 3,
  },
  {
    label: "找回密码",
    value: 4,
  },
];
const formState: UnwrapRef<FormState> = reactive({
  process: 5,
  backMode: true,
  modules: [1, 2, 3, 4],
});

const accountInput = ref("");
const progress = ref(0);
const drawerVisible = ref(false);
const drawerData = ref([]);
const dataSource = ref<DataSource[]>([
  {
    taskId: 1,
    account: "123456789",
    accountStr: "eqweqwe|qwe",
    status: "进行中",
    logResult: "logResult",
    updateTime: "jintian ",
  },
]);
const columns = [
  {
    title: "任务ID",
    dataIndex: "taskId",
    key: "taskId",
    width: 100,
    align: "center",
  },
  {
    title: "账号",
    dataIndex: "account",
    key: "account",
    width: 120,
    ellipsis: true,
  },
  {
    title: "账号串",
    dataIndex: "accountStr",
    key: "accountStr",
    ellipsis: true,
  },
  {
    title: "状态",
    dataIndex: "status",
    key: "status",
    ellipsis: true,
  },
  {
    title: "日志结果",
    dataIndex: "logResult",
    key: "logResult",
    ellipsis: true,
  },
  {
    title: "更新日期",
    dataIndex: "updateTime",
    key: "updateTime",
    ellipsis: true,
  },
  {
    title: "操作",
    dataIndex: "operation",
    align: "center",
    width: 100,
  },
];

/**
 * 账号解码
 */
const handleDecodeString = () => {
  if (!accountInput.value.trim()) {
    message.error("请输入账号字符串");
    return;
  }
  drawerData.value = transformPipeString(accountInput.value);
  drawerVisible.value = true;
};
/**
 * 添加到队列
 */
const handleAddToQueue = () => {
  if (!accountInput.value.trim()) {
    message.error("请输入账号字符串");
    return;
  }
  message.success("已添加到队列");
};

/**
 * 开始执行
 */
const handleStart = () => {
  message.success("开始执行");
};
/**
 * 终止执行
 */
const handleTerminate = () => {
  message.error("终止执行");
};
</script>

<style>
.account-table-wrapper {
  margin-top: 16px;
}
</style>
