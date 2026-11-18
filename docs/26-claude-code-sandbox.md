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

## 4. 必须区分 Claude Code 产品 Sandbox 与独立 sandbox-runtime

### Claude Code 本地 Bash Sandbox（产品行为）

截至 2026-11-18，Claude Code 官方文档描述的本地 Bash Sandbox 平台路径为：

    macOS
      → Seatbelt

    Linux / WSL2
      → bubblewrap
      → 独立 Network Namespace
      → 本机 Sandbox Proxy
      → 可选 seccomp filter

Native Windows 不提供 Claude Code Bash Sandbox；Windows 用户需要通过 WSL2 或容器使用支持的 Linux 环境。

**产品覆盖范围：** 该 Sandbox 主要限制 Claude Code 的 Bash 命令及其子进程。官方文档明确说明，File tools、MCP servers、hooks 等并不自动处于同一个 Bash Sandbox 内。不能因为 Bash 被 Sandbox，就认为整个 Claude Code 进程、所有 MCP 或所有工具都自动受同一边界保护。

### Anthropic 独立的 sandbox-runtime 项目

这是另一个开源工具，目标是对任意进程施加文件和网络限制：

    macOS
      → sandbox-exec / Seatbelt profile

    Linux
      → bubblewrap + network namespace

    Windows
      → Alpha implementation
      → dedicated srt-sandbox local user
      → WFP egress fence
      → write-restricted token
      → filesystem ACEs

Windows 这一项属于独立 sandbox-runtime 的 Alpha 实现，不是 Claude Code 原生 Windows Bash Sandbox。

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

## 7. Cloud Session 的 GitHub Proxy 是另一种重要思路

Claude Code Cloud Session 的公开资料说明：在 Anthropic-hosted environment 中，GitHub 凭证保存在 Anthropic 服务端并加密，Session VM 不直接拿到真实 GitHub credential；VM 发起 Git 操作时由服务端 GitHub Proxy 代为附加凭证。

概念：

    Cloud Session VM
       ↓
    Git operation
       ↓
    GitHub Proxy
       ↓
    attach credential server-side
       ↓
    GitHub

这里可以确认的是 Credential Mediation：真实凭证留在 VM 外部。不要在没有对应技术文档的情况下，额外声称 Proxy 一定会按 branch / commit 做某种特定校验。

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
    proxy attaches credential server-side
       ↓
    GitHub

如果 Proxy 把 Token 返回给 Sandbox，Token 仍然是 Agent 可读取的 Secret。代理式访问的关键是凭证留在 Broker / Proxy 端。

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

Claude Code 本地 Bash Sandbox 展示的是：

    Bash process tree
      +
    Filesystem isolation
      +
    Network isolation
      +
    Permission / fallback controls

但 Claude Code 的 File tools、MCP servers、hooks 不应被默认视为已包含在同一个 Bash Sandbox 内。

Anthropic Cloud Session 则展示：

    isolated VM per session
      +
    network access controls
      +
    server-side credential proxy

而独立 sandbox-runtime 是另一个可研究的跨平台进程 Sandbox 项目。

三者必须分开讲，不能混成一个“Claude Code Sandbox 实现”。

## 参考

Claude Code Sandbox:
https://code.claude.com/docs/en/sandboxing

Claude Code Security:
https://code.claude.com/docs/en/security

Anthropic sandbox-runtime:
https://github.com/anthropics/sandbox-runtime

Claude Code Cloud Sessions:
https://code.claude.com/docs/en/claude-code-on-the-web

**核验日期：2026-11-18。** 产品平台支持与独立 sandbox-runtime 的平台支持是两个不同问题。


## 11. 关于网络限制的补充

Claude Code Linux / WSL2 Sandbox 会把命令放入独立 Network Namespace，并通过本机 Sandbox Proxy 处理允许的域名。能否联网取决于工具是否遵守 Proxy 环境变量；直接 SSH、UDP / QUIC、ICMP 等流量不等于自动获得允许。macOS 则通过 Seatbelt 阻止除代理路径外的直接网络连接。

因此 Proxy 的 allowlist 和 OS-level network enforcement 必须组合；单独注入 `HTTP_PROXY` 环境变量不是安全边界。


## 12. Claude Code Sandbox 的默认开关和失败回退必须讲清

截至 2026-11-18，Claude Code 本地 Bash Sandbox：

- 默认关闭，需要在会话中启用或通过设置开启；
- 如果平台不支持或依赖检查失败，默认可能回退到无 Sandbox 的命令执行；
- 命令在 Sandbox 内失败后，Claude 可能申请使用 `dangerouslyDisableSandbox` 在 Sandbox 外重试；
- 可以设置 `sandbox.failIfUnavailable = true`，在 Sandbox 无法启动时拒绝启动 / 执行；
- 可以设置 `sandbox.allowUnsandboxedCommands = false`，关闭 Sandbox 外重试；
- `excludedCommands` 和用户自己在 shell-mode 输入的命令也需要单独审查。

严格部署通常要同时考虑：

```json
{
  "sandbox": {
    "enabled": true,
    "failIfUnavailable": true,
    "allowUnsandboxedCommands": false
  }
}
```

还要注意：这并不自动保护 File tools、MCP、hooks、LSP、plugin monitors、helper commands。若要把这些组件也放进同一边界，需要把 Claude Code 整体运行在 Container、VM 或独立 sandbox-runtime 内。

## 13. 环境变量和凭证默认不是“自动消失”

Claude Code 官方文档指出，Sandboxed Bash 默认继承 Claude Code 的环境变量，其中可能包含 Secret。需要通过 `credentials`、环境变量清理和凭证文件 mask 等配置减少暴露；不要假设“Bash 已 Sandbox”就代表 Token 不可见。

## 14. Proxy 的域名过滤也有边界

本地 Sandbox Proxy 根据连接目标的 hostname 做 allow / deny 判断，但普通 HTTPS CONNECT 不会解密 TLS 内容。允许某个大域名可能形成数据外传路径；若威胁模型要求更强控制，需要考虑 TLS interception / 自定义 Proxy、证书管理和更窄的域名规则。

参考：
- https://code.claude.com/docs/en/sandboxing
- https://code.claude.com/docs/en/security
