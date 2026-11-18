# 第 28 讲：VS Code / GitHub Copilot Agent Sandbox

## 1. 为什么 VS Code 的设计值得学

VS Code Agent 运行环境非常复杂：

    Terminal
    MCP Server
    Language Server
    Remote Host
    Local Host
    Cloud Session

因此它特别适合学习：

> Sandbox 到底应该保护哪个进程？

答案不是只保护 Agent Host。

## 2. Terminal Sandbox

Agent 可能执行：

    npm test
    python test.py
    go test
    git diff

这些最终都是操作系统进程。

所以 Sandbox 应该覆盖：

    Agent
      ↓
    Terminal
      ↓
    Shell
      ↓
    child process

## 3. MCP Server 为什么也要 Sandbox

假设：

    Agent
      ↓
    MCP Server
      ↓
    filesystem
    network
    database

如果 MCP Server 完全不受 Sandbox：

    Agent Sandbox
        ↓
    MCP
        ↓
    outside world

那么 Agent 可以通过 MCP 绕过自己的边界。

因此：

> Tool Server 本身也是不可信执行面。

## 4. Language Server 也一样

LSP Server 可能是：

    typescript-language-server
    pylsp
    gopls
    rust-analyzer

它们可能：

- 读取 workspace；
- 启动子进程；
- 访问网络；
- 读取配置；
- 加载插件。

所以现代 Agent Sandbox 会把：

    MCP
    LSP
    Terminal

一起考虑。

## 5. Local 与 Remote

本地：

    VS Code
      ↓
    Local Agent
      ↓
    Local OS Sandbox

Remote：

    VS Code
      ↓
    Remote Host
      ↓
    Agent
      ↓
    Remote OS Sandbox

关键：

> Sandbox 必须建立在真正执行代码的机器上。

如果命令跑在 Remote Host，就不能只在本地做 Sandbox。

## 6. Sandbox 与 Cloud Session

Cloud Agent：

    User
      ↓
    Cloud Agent
      ↓
    Dedicated machine
      ↓
    Sandbox / VM / Container

这时保护目标发生变化：

本地：

> 防止 Agent 破坏用户电脑。

云端：

> 防止 Agent 影响其他租户和控制平面。

所以 Threat Model 会改变。

## 7. VS Code 的安全提醒

官方文档明确强调：

> Sandbox 不是 VM，也不是完整用户账号边界。

这句话非常重要。

如果 Sandbox 进程仍然使用你的账户：

    UID = user

那么：

    Credential
    SSH Agent
    Browser data
    Docker socket

仍可能成为风险来源。

## 8. 实验

设计：

    Agent
      ├── Terminal
      ├── MCP
      └── LSP

然后给每一个画：

    process?
    network?
    filesystem?
    credential?

你会发现：

> Agent Sandbox 实际上是“整个 Tool Runtime Sandbox”。

## 9. 参考

VS Code Agent Sandboxing:
https://code.visualstudio.com/docs/agents/run/agent-sandboxing

VS Code Trust & Safety:
https://code.visualstudio.com/docs/agents/concepts/trust-and-safety
