# Lab 07：Fake Credential Broker

## 目标

模拟 Agent 请求 Broker 执行 Git 操作。Fake Token 只存在于 Broker 进程环境中：

- Agent 只提交 repository / branch / commit；
- Broker 校验仓库和分支；
- Broker 模拟执行 push；
- 返回结果，不把 Token 返回给 Agent。

## 运行

终端一：

```bash
FAKE_GITHUB_TOKEN='ghp_FAKE_NOT_REAL' python3 broker.py
```

终端二：

```bash
python3 client.py
```

预期返回 `{"ok": true, "operation": "simulated_push"}`，响应中不包含 Fake Token。

## 拒绝测试

把 client 的 repository 改成其他仓库，或把 branch 改成 `main`，Broker 应返回 HTTP 403。

## 安全边界

这是本地模拟服务，不会连接 GitHub，也不执行真实 Git Push。生产 Broker 还需要认证调用方、校验用户和仓库授权、签名与重放保护、审计、速率限制和安全存储凭证。不要把真实 Token 放入实验。
