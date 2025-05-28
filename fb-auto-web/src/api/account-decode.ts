import request from "@/api/request";

const baseUrl = "/api";

/**
 * 获取列表
 * @param params
 * @returns
 */
export const getAccountList = (params: any) => {
  return request({
    url: `${baseUrl}/account/decode`,
    method: "get",
    params,
  });
};
