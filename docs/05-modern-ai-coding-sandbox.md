# 第 5 讲：为什么现代 AI Coding Agent 不一定使用 Docker

## 1. 这是整个课程的转折点

很多初学者会自然想到：

    AI
      ↓
    Docker
      ↓
    Code

这对云端执行环境很常见，但不是本地 AI Coding Agent 的唯一答案。

现代本地 Agent 更关注：

> 保留宿主机开发环境，同时限制 Agent 的危险能力。

典型模型：

    AI Agent
       ↓
    Host OS
       ↓
    OS-level Sandbox
       ↓
    Shell / Python / Node / Go

## 2. Docker 的主要问题：开发环境兼容性

用户可能在 macOS：

    Xcode
    Swift
    Homebrew
    macOS SDK
    iOS Simulator
    Git
    Python
    Node

Linux Container 提供：

    Linux user space
    glibc
    Python
    Node

这不是同一个环境。

如果 Agent 需要操作用户真实的 Mac 工具链，完整容器化就会增加复杂度。

## 3. OS Sandbox 的思路

不是创建一台新机器，而是在现有 OS 中约束进程。

例如：

    /workspace      READ + WRITE
    /tmp            READ + WRITE
    ~/.ssh          DENY
    ~/.aws          DENY
    other-project   DENY
    network         POLICY

程序仍然可以运行宿主机的 Python、Node、Git，但系统级安全边界限制了它能触达什么。

## 4. 主流实现为什么值得研究

Claude Code 的公开资料说明其 Sandbox Runtime 使用 macOS Seatbelt 和 Linux bubblewrap，并同时建立文件系统和网络边界。

Codex 的公开代码可以看到平台 Sandbox Manager：macOS 使用 Seatbelt，Linux 路径结合 Landlock/seccomp，并与网络代理和 workspace policy 配合。

Cursor 文档也说明其本地 Sandbox 会限制文件、网络以及整个子进程树。

VS Code Copilot 当前文档也把审批和 Sandbox 明确作为两层不同的保护，并对 terminal、MCP server、LSP server 等进程应用 Sandbox。

因此：

> Docker 只是 Sandbox 的一种实现，不是 Sandbox 的定义。

## 5. 这也是为什么本课程后面要学 OS 原语

macOS：

    Seatbelt

Linux：

    Namespace
    Landlock
    seccomp
    bubblewrap

Windows：

    Restricted Token
    AppContainer
    其他平台机制

## 6. 一个非常重要的判断方法

以后看到任何 AI Coding 产品，不要先问：

> “它是不是 Docker？”

先问：

1. 安全边界在哪一层？
2. 文件怎么限制？
3. 网络怎么限制？
4. 子进程是否继承？
5. 凭证怎么处理？
6. 是否有审批绕过？
7. Session 是否在云端？
8. 如果是本地，使用什么 OS 原语？

## 参考

Claude Code:
https://www.anthropic.com/research/claude-code-sandboxing

Codex:
https://github.com/openai/codex/tree/main/codex-rs/sandboxing

Cursor:
https://cursor.com/docs/agent/security/run-modes

VS Code:
https://code.visualstudio.com/docs/agents/run/agent-sandboxing
