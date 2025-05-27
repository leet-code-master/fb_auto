# 创建并激活虚拟环境

```bash
python3 -m venv venv
```

# 激活虚拟环境

```bash
# Linux/MacOS
source venv/bin/activate
```

```bash
# Windows
venv\Scripts\activate
```

```bash

# 退出虚拟环境
deactivate
```

# 安装依赖

```bash
pip3 install -r requirements.txt
```

# 启动服务（自动重载模式）

```bash
uvicorn main:app --reload
```

# 生产环境启动

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

清除 pip 缓存

```bash
pip3 cache purge
```
