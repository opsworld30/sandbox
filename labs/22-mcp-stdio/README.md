# Lab 22：最小 MCP stdio Server

## 环境与运行

Python 3.10+，无第三方依赖：

```bash
python3 client.py
```

Client 会启动 Server 子进程，通过 stdio 发送 JSON-RPC 消息：

1. `initialize`
2. `notifications/initialized`
3. `tools/list`
4. `tools/call`

Server 提供一个只返回模拟数据的 `issue.read` Tool。

## 安全边界

这是用于理解 MCP 生命周期与 Tool Schema 的最小教学实现，不包含完整 MCP SDK 的所有协议细节、采样、资源、提示模板、认证和传输能力。Server 不连接真实 GitHub，也不读取本地文件。生产 MCP Server 仍需要独立进程权限、网络和凭证边界。
