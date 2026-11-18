# 第 26 讲：拆解 Claude Code Sandbox——为什么它强调“文件 + 网络”双边界

## 1. Claude Code 为什么需要 Sandbox

Claude Code 运行在开发者机器上。

它可以：

    读代码
    改代码
    跑 shell
    安装依赖
    调 Git
    启动工具
    使用 MCP

这意味着 Agent 一旦被 Prompt Injection 影响，攻击者可能间接获得：

    文件访问
    +
    网络访问

因此只做审批是不够的。

## 2. Approval 为什么会失效

最开始可以：

    Agent
      ↓
    “我要执行 npm test”
      ↓
    Ask
      ↓
    User Allow

但如果 Agent 一小时请求几十次：

    Allow
    Allow
    Allow
    Allow
    Allow
    ...

用户最终会出现：

> Approval Fatigue

于是审批越多，不一定越安全。

## 3. Sandbox 的思路

Claude Code 的公开设计把两个边界放在一起：

    Filesystem Isolation
           +
    Network Isolation

原因非常直观。

### 只有文件隔离

    Agent
      ↓
    read ~/.ssh/id_rsa
      ↓
    network
      ↓
    attacker.example

### 只有网络隔离

    Agent
      ↓
    network blocked
    但仍然可以修改：
      ~/.ssh
      ~/.bashrc
      其他项目

两个都要限制。

## 4. Claude 的 OS-level Runtime

公开的 sandbox-runtime 项目使用：

    macOS
      → sandbox-exec / Seatbelt

    Linux
      → bubblewrap + network namespace

    Windows
      → dedicated local user
      → Windows Filtering Platform
      → write-restricted token
      → ACL

这就是一个非常好的学习案例：

> 不要求所有平台使用同一种技术，而是保持统一的 Sandbox API。

## 5. 为什么“无容器”也可以 Sandbox

很多人会认为：

    Sandbox = Container

实际上：

    Sandbox
       ├── OS sandbox
       ├── Container
       ├── MicroVM
       └── VM

Claude Code 的本地 Runtime 证明了：

> 如果你的目标只是限制一个进程树的文件和网络能力，不一定需要启动一个完整容器。

## 6. 为什么这对 AI Coding 很重要

本地 Agent 需要使用：

    node
    python
    go
    rust
    git
    make
    xcodebuild

这些工具本来就是用户机器上的开发环境。

如果强制：

    Agent
      ↓
    Linux Container

就可能出现：

    宿主机环境
       ≠
    Container 环境

所以 OS-level Sandbox 可以提供一个折中：

    使用宿主机工具
       +
    限制宿主机能力

## 7. Git Proxy 是另一种重要思路

Claude Code Web 的公开资料还展示了一种非常值得学习的设计：

    Git
      ↓
    Custom Proxy
      ↓
    Validate credential
      ↓
    Validate repository / branch
      ↓
    Attach real credential
      ↓
    GitHub

重点：

> 不把高价值 Git Credential 直接暴露给 Sandbox。

这叫：

> Credential Isolation / Credential Mediation

## 8. 这比“把 token 放环境变量”高级很多

危险：

    SANDBOX
       ↓
    GITHUB_TOKEN=xxxxx
       ↓
    Agent

Agent 一旦被攻击：

    printenv
       ↓
    token

更安全：

    SANDBOX
       ↓
    git proxy
       ↓
    short-lived / scoped credential
       ↓
    GitHub

## 9. 实验

设计一个假的 Git Proxy：

    POST /git/push

请求：

    repository
    branch
    commit

Proxy 检查：

    repository == allowed_repo
    branch == agent-branch

然后才真正执行 push。

你会发现：

> Proxy 本身也是 Sandbox 安全体系的一部分。

## 10. 这一讲的核心

Claude Code 案例告诉你：

    Sandbox
      =
    Filesystem Boundary
      +
    Network Boundary
      +
    Process Boundary
      +
    Credential Boundary

而不是：

    Sandbox = Docker

## 参考

Anthropic sandboxing:
https://www.anthropic.com/research/claude-code-sandboxing

Anthropic sandbox-runtime:
https://github.com/anthropics/sandbox-runtime

How Anthropic contains Claude:
https://www.anthropic.com/research/how-we-contain-claude
