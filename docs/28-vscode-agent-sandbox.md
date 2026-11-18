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

截至 2026-11-18，VS Code 当前 Agent Sandbox 文档针对使用默认工具的 Copilot Harness sessions。不要把它泛化成所有 VS Code 扩展、所有自定义 Agent Harness 都使用同一实现。

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

VS Code 当前文档说明：由 Agent Host 为该 Session 启动或管理的 MCP Server，可以在启用 Sandbox 时一并受限；独立启动的 MCP Server 不在这项覆盖范围内。

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

同样，当前 Copilot Harness 文档支持对该 Session 启动或管理的 Language Server 施加 Sandbox。独立启动的 LSP 进程不应被假设自动纳入边界。

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

## 7. VS Code 当前默认值与平台支持

截至 2026-11-18，Copilot Harness 默认工具的公开配置包括：

- Sandbox enabled：默认 off，需要显式开启；
- outbound network `allowNetwork`：默认 true；
- local network `allowLocalNetwork`：默认 false；
- 托管 MCP Server / LSP Server 的 Sandbox 开关默认 true；
- Git HTTPS 凭证与 GitHub CLI 认证默认可在 Sandbox 中使用（`authenticategit` / `authenticategh` 均默认 true）；
- 允许申请 Sandbox 外执行的开关默认 true，实际执行仍需确认。

这意味着 Sandbox 中的命令默认可以通过 Git / GitHub 认证集成使用相应权限；但不要据此推断真实 Token 会以明文注入进程。当前 Copilot 还提供 Credential Proxy，用 placeholder 替代真实凭证，并由本机 Proxy 对批准的 HTTPS 目标完成凭证替换。即便 Token 不直接暴露，Agent 仍然拥有相应的操作能力；若任务不需要 GitHub 权限，应关闭对应认证能力。若 bwrap、slirp4netns、util-linux 或兼容 iptables 等依赖缺失，默认 Copilot Harness 工具不会静默退回到无 Sandbox 执行，而会提示修复；依赖必须安装在真正运行 Agent 命令的 Host / WSL / Remote Host 上。系统依赖缺失时，默认工具不会静默退回到无 Sandbox 执行，而会提示修复依赖；应在实际执行主机上安装并检查依赖。

平台支持：

    macOS 15+
      → Seatbelt

    glibc Linux / WSL2
      → bubblewrap + slirp4netns + util-linux + iptables

    Windows 11
      → BaseContainer（Experimental）

Alpine / musl Linux 和 WSL1 不在当前该 Runtime 的支持范围内。Windows 的 per-server MCP sandboxing 也有单独限制。

官方文档还明确强调：

> Sandbox 不是 VM，也不是完整用户账号边界。

受限进程仍在执行主机上运行，并可能仍使用当前用户身份；凭证、开发工具目录、额外路径和 Sandbox 外执行都会改变实际隔离强度。

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

## 9. Network 默认值是一个容易忽略的坑

打开 Sandbox 并不意味着默认断网。当前 Copilot Harness 文档中的 `chat.agent.sandbox.network.allowNetwork` 默认是 `true`，并通过 allowed / denied domains 进一步控制目的地。

如果要实现“默认断网”，必须显式设置网络策略并检查实际生效策略。还要注意 Sandbox 外执行请求会移除该次操作的文件系统和网络限制。

## 10. 参考

VS Code Agent Sandboxing:
https://code.visualstudio.com/docs/agents/run/agent-sandboxing

VS Code Trust & Safety:
https://code.visualstudio.com/docs/agents/concepts/trust-and-safety

**核验日期：2026-11-18。** 本讲针对 Copilot Harness 默认工具；Local Harness、Custom Terminal Tools、Cloud Sessions 和 per-server MCP sandboxing 有不同的设置与限制。


## 11. 一个重要区分：Built-in Tools 与 OS Process Tools

当前文档说明，Terminal 和被 Agent Host 管理的 MCP / LSP 进程可应用 Sandbox；不启动 OS 进程的 Built-in Tools 使用自身的权限检查。这些工具不能简单画成同一条操作系统进程树。


## 12. Windows 与 Credential Proxy 的特殊条件

当前 VS Code 文档还有两个容易漏掉的细节：

- Windows 上，使用 Proxy、hostname restriction 或 credential masking 时，需要允许 Sandbox 访问本机 loopback listener；这会要求 `allowLocalNetwork = true`，从而增加本地网络访问面。
- Credential masking 可以让工具看到 placeholder，再由 Proxy 只向批准的 HTTPS host 注入真实凭证；但它需要证书信任配置，且不是简单的“环境变量自动隐藏”。

此外，Windows 上的 per-server MCP Sandbox 目前不可用；不要把 macOS / Linux 的 MCP 隔离能力直接推断到 Windows。

## 13. 失败回退和远程执行

`allowUnsandboxedCommands` 默认 true：命令不能在 Sandbox 内执行时，Agent 可以请求用户批准在 Sandbox 外执行。设置为 false 才会拒绝该回退。

远程 Session 的 Sandbox 必须在实际运行 Agent 的远程 Host 配置；本机 VS Code 客户端的 Sandbox 设置不会自动限制远程执行主机。当前 Copilot Cloud Sessions 本身标注为 Experimental，属于托管云环境，不应把本地 Host Sandbox 的实现和默认值直接套用过去。

## 本讲实验代码

- [Tool Capability Model](../labs/15-tool-capabilities/README.md)
- [MCP stdio Server](../labs/22-mcp-stdio/README.md)

这些是对应主题的可运行教学实验或产品设计复现；并非厂商内部实现的源码副本。
