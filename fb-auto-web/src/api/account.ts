import { request } from "@/api/request";

const baseUrl = "/api";
export const getAccountList = (params: any) => {
  return request({
    url: `${baseUrl}/account/list`,
    method: "get",
    params,
  });
};
