<template>
  <div class="account-decoding">
    <a-flex>
      <div class="account-input card">
        <!-- <div class="card-title">字符串输入</div> -->
        <div class="card-content">
          <a-textarea
            v-model:value="accountInput"
            placeholder="请输入"
            :rows="12"
          />
          <div class="card-footer">
            <a-button type="primary">解码</a-button>
          </div>
        </div>
      </div>
      <div class="accountconfig card">
        <!-- <div class="card-title">配置</div> -->
        <div class="card-content">
          <a-form :model="formState">
            <a-form-item label="进程数">
              <a-input-number
                id="inputNumber"
                v-model:value="formState.process"
              />
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
          </a-form>

          <span>运行进度</span>
          <a-slider id="test" v-model:value="progress" disabled />
        </div>

        {{ formState }}
        <div class="card-footer">
          <a-flex gap="middle">
            <a-button type="primary">启动</a-button>
            <a-button type="primary" danger>终止</a-button>
          </a-flex>
        </div>
      </div>
    </a-flex>
    <div class="account-table-wrapper">
      <div class="table-header">
        <a-flex justify="space-between">
          <a-space>
            <a-button type="primary">刷新</a-button>
            <a-button type="primary">导出</a-button>
          </a-space>
          <a-button type="primary">清除数据</a-button>
        </a-flex>
      </div>
      <div class="table-content">
        <a-table :dataSource="dataSource" :columns="columns" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from "vue";
import type { UnwrapRef } from "vue";

interface FormState {
  process: number;
  backMode: boolean;
  modules: number[];
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
  backMode: false,
  modules: [1, 2, 3, 4],
});

const accountInput = ref("");
const progress = ref(0);
const dataSource = ref([]);

const columns = [
  {
    title: "任务ID",
    dataIndex: "taskId",
    key: "taskId",
  },
  {
    title: "账号",
    dataIndex: "account",
    key: "account",
  },
];
</script>

<style>
.account-decoding {
  background-color: #f8f8f8;
}
.card {
  width: 50%;
  /* height: 500px; */
  margin: 10px;
  background-color: #fff;
  border-radius: 10px;
  padding: 12px;
}
.card-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 10px;
}
.card-content {
}
.account-table-wrapper {
  /* background-color: #fff; */
}
</style>
