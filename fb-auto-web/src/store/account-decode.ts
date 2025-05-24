import { defineStore } from "pinia";
import { ref } from "vue";
const useAccountDecodeStore = defineStore(
  "account-decode",
  () => {
    return {};
  },
  {
    persist: true,
  }
);
export default useAccountDecodeStore;
