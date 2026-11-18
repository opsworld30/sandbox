# Lab 16：Control Plane / Worker 的本地 API 模拟

## 环境与运行

Python 3.10+，无第三方依赖。

终端一：

```bash
LAB_SESSION_TOKEN=local-demo-token python3 server.py
```

终端二：

```bash
python3 client.py
```

## API

- `POST /sessions`：创建临时 Session；
- `POST /sessions/{id}/exec`：执行有限的命令 allowlist；
- `DELETE /sessions/{id}`：销毁 Session。

## 安全边界

为了避免把教学服务变成宿主机任意命令执行接口，本实验只允许 `pwd`、`ls` 和 `echo` 三种命令，并且只监听 `127.0.0.1`。它模拟 Control Plane / Worker API，不是真正的远程 Sandbox。生产版本还需要 OS Sandbox、认证授权、并发限制、资源控制、审计和远端 Worker 隔离。
