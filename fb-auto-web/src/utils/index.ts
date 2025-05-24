import type { AccountItem } from "../types/account.type";

/**
 * 根据 | 分割字符串
 * @param value
 * @returns
 */
export const transformPipeString = (value: string): AccountItem[] | [] => {
  if (!value) {
    return [];
  }
  return value.split("\n").map((line) => {
    const [account, password, twoFA, email, emailPassword, spareEmail] = line
      .trim()
      .split("|");

    return {
      account,
      password,
      twoFA,
      email,
      emailPassword,
      spareEmail,
    };
  });
};
