import request from "@/api/request";

const baseUrl = "/api";

interface DecodeParams {
  account: string;
}
/**
 * 字符串解码
 * @param params
 * @returns
 */
export const decodeAccount = (params: DecodeParams) => {
  return request({
    url: `${baseUrl}/account/decode`,
    method: "get",
    params,
  });
};

/**
 * 获取列表
 * @param params
 * @returns
 */
export const getAccountList = (params: any) => {
  return request({
    url: `${baseUrl}/account/list`,
    method: "get",
    params,
  });
};
