# 第 30 讲：Windows 为什么难——从 Codex Windows Sandbox 看“自己造安全边界”

## 1. Windows 没有一个统一的“AI Coding Sandbox 实现”

不同产品组合了不同的 Windows 原语。必须分开研究：

- Codex native Windows Sandbox；
- Gemini CLI Windows Native Sandbox；
- Anthropic 独立 sandbox-runtime 的 Windows Alpha；
- VS Code Copilot Harness 的 Windows BaseContainer（Experimental）。

它们不是同一套实现，也不能互相推导。

## 2. 为什么 Windows 是一个很好的案例

macOS 有：

    Seatbelt

Linux 有：

    seccomp
    Landlock
    namespaces

但 Windows 上要实现：

    arbitrary developer tool
       +
    filesystem restriction
       +
    network restriction
       +
    process tree

并不简单。

OpenAI 在 Codex Windows Sandbox 的公开文章中详细讨论了这个问题。

## 3. 为什么 AppContainer 不够

AppContainer 很适合：

    “我知道这个应用需要哪些能力”

但 Coding Agent 的特点是：

    shell
    git
    python
    node
    npm
    powershell
    arbitrary binaries

它不是一个固定能力集合。

所以：

> Coding Agent 是开放式程序执行器。

这使得传统应用 Sandbox 的能力模型不一定直接适用。

## 4. Windows ACL 的问题

可以用：

    ACL

限制：

    C:\workspace
      allow

    C:\Users\...
      deny

但如果每次 Sandbox policy 变化都需要修改大量 ACL：

    create ACL
      ↓
    run
      ↓
    cleanup ACL

就会产生：

- 性能成本；
- 复杂性；
- race condition；
- 清理失败；
- 系统状态污染。

## 5. Network 更难

只靠环境变量：

    HTTP_PROXY
    HTTPS_PROXY

不够。

因为程序可能：

    自己创建 socket

因此：

    Proxy restriction

不等于：

    Kernel-level network restriction

这就是为什么真正的 Network Sandbox 非常难。

## 6. Windows 的一个关键思想

如果操作系统没有刚好提供你需要的原语：

> Sandbox Runtime 本身就可能需要组合多个 OS 机制。

例如：

    identity
    +
    ACL
    +
    network filtering
    +
    process management
    +
    cleanup

最终形成：

    WindowsSandboxBackend

## 7. 为什么这是一个非常好的面试题

面试官问：

> “如果你要在 Windows 实现 AI Coding Sandbox 怎么办？”

不要回答：

    Docker

应该回答：

    先定义 threat model
       ↓
    filesystem boundary
       ↓
    process boundary
       ↓
    network boundary
       ↓
    credential boundary
       ↓
    resource boundary
       ↓
    选择 Windows primitives
       ↓
    build runtime

## 8. 实验

不用真的改 ACL。

先设计：

    WindowsSandboxPolicy

    workspace
    readRoots
    writeRoots
    denyRoots
    networkMode
    allowedDomains
    processLimit
    timeout

然后实现：

    validatePolicy()

这一步先把 Policy 和 Enforcement 分开。

## 9. Codex Windows Sandbox 的公开实现要点

OpenAI 2026 年工程文章描述的当前设计包含：

- setup 阶段创建专用 Sandbox 用户和相关身份；
- 用 restricted token 限制命令进程；
- 用 ACL 控制工作区和受保护路径；
- 用 Windows Firewall 对专用 Sandbox 用户应用出站网络规则；
- 使用单独 setup binary 和 command-runner binary 跨越提权 / 用户边界。

早期 unelevated prototype 主要靠环境变量把代理流量导向失败端口，这只能作为 advisory；直接创建 socket 的程序可以绕过，因此不能当作最终的强制网络边界。

## 10. 其他产品不要混为一谈

### Gemini CLI

Windows Native Sandbox 使用 Low Mandatory Level（MIC），并用 `icacls` 设置完整性级别。官方提醒这些 ACL / integrity level 变化可能持久保留，需要按文档复原。

### Anthropic sandbox-runtime

独立的 `@anthropic-ai/sandbox-runtime` Windows 支持目前标注为 Alpha，使用专用 `srt-sandbox` 本地用户、Windows Filtering Platform（WFP）出站过滤、write-restricted token 和文件系统 ACE。

这不是 Claude Code Native Windows Bash Sandbox；Claude Code 产品本身的本地 Bash Sandbox 文档仍要求 Windows 用户使用 WSL2 或容器环境。

### VS Code Copilot Harness

当前 Windows Agent Sandbox 采用 BaseContainer，官方标注为 Experimental，并有特定 Windows 11 版本要求。

## 11. 参考

OpenAI:
https://openai.com/index/building-codex-windows-sandbox/


- Codex Windows Sandbox：https://openai.com/index/building-codex-windows-sandbox/
- Gemini CLI Sandbox：https://geminicli.com/docs/cli/sandbox/
- Anthropic sandbox-runtime：https://github.com/anthropics/sandbox-runtime
- VS Code Agent Sandbox：https://code.visualstudio.com/docs/agents/run/agent-sandboxing

**核验日期：2026-11-18。** Windows Sandbox 的平台要求、Alpha / Experimental 状态和提权行为可能随产品版本变化。
