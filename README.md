# python 服务

## 账号解码

### 获取解码后的列表

`GET /api/account-decode`

请求参数：

| 字段名 | 类型   | 位置 | 描述   |
| ------ | ------ | ---- | ------ |
| params | string | body | 父节点 |

响应参数：

| 字段名             | 类型   | 位置 | 描述     |
| ------------------ | ------ | ---- | -------- |
| code               | Int    | body | 状态码   |
| message            | string | body | 消息描述 |
| data               | json   | body | 返回数据 |
| data.visitorsCount | Long   | body | 访问数   |
| data.registerCount | Long   | body | 注册数   |
| data.providerCount | Long   | body | 服务商数 |

响应示例：

```json
{
  "code": 200,
  "message": "操作成功",
  "data": {
    "visitorsCount": 5,
    "registerCount": 6,
    "providerCount": 6
  }
}
```
