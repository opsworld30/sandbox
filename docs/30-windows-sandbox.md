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

## 3. 为什么 Codex 没有直接把 AppContainer 当成完整答案

AppContainer 是 Windows 正式的应用隔离机制，也可以运行任意可执行代码；不能说它“不能 Sandbox 任意程序”。

Codex 面临的具体问题是：开发工具链动态、开放、需要访问用户指定的 Workspace，还会启动 shell、Git、Python、Node、编译器和其他子进程。AppContainer 的身份、Capability、文件 ACL 和网络配置模型并不是一个可以无成本套用到所有本地开发工具的现成答案。

因此更准确的说法是：

> AppContainer 是一种可选机制，但 Codex 选择了更适合其本地开发工作流的 restricted-token + 专用身份 + ACL + Firewall 组合。

这不是说 AppContainer 本身不安全，也不是说其他产品不能使用它。

## 4. Windows ACL 的问题

可以用：

    ACL

限制：

    C:\workspace
      allow

    C:\Users\...
      deny

但如果运行时频繁创建和清理 ACL：

    prepare ACL
      ↓
    run
      ↓
    cleanup ACL

就会增加：

- 性能成本；
- 配置和清理复杂度；
- 权限变更窗口；
- 清理失败后遗留的系统状态。

这不是说 ACL 本身必然存在 race condition，而是动态修改宿主机 ACL 时必须设计好并发、原子性、回滚和失败恢复。

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

独立的 `@anthropic-ai/sandbox-runtime` Windows 支持目前标注为 Alpha。默认 `srt-win` Backend 使用专用 `srt-sandbox` 本地用户、Windows Filtering Platform（WFP）出站过滤、write-restricted token、Job Object 和文件系统 ACE。

当前项目还提供可选的 **实验性** `mxc` Backend：在支持的 Windows BaseContainer 环境中通过 `@microsoft/mxc-sdk` 执行，不使用 `srt-sandbox` 用户和 ACL 安装流程。它需要 Node.js 24+ 与可用的 MXC SDK；MXC 的 AppContainer tiers 不在此 Backend 使用。若 Host 不支持所需策略，会返回 `backend_unsupported`，不会自动回退到 `srt-win`。两种 Backend 不能混为一谈。

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


## 12. Windows Sandbox 的共同教训

不同产品都在组合 Windows 身份、ACL、网络过滤和进程管理，但这些机制并不自动形成完整安全边界：

- Restricted Token / Low Integrity Level 是不同的安全机制，不要混为一谈；
- ACL 的修改可能持久化，必须设计回滚和异常清理；
- WFP 过滤需要核对实际 socket 创建 Token、代理路径和系统服务代发流量等限制；
- Job Object 管理进程树，不等于文件和网络隔离；
- AppContainer、Windows Sandbox VM、BaseContainer、产品自定义 Sandbox 的隔离层次和兼容性不同。

每个实现都应该有明确的 Threat Model、策略验证和 Escape Test；不能因为名称里有 Sandbox 就假设它阻止了所有宿主机访问。


## 13. WFP 的边界不能被忽略

Anthropic sandbox-runtime 的 Windows Alpha `srt-win` Backend 文档明确列出 WFP 方案的限制：过滤器以专用 Sandbox 用户的 SID 为条件，若受限进程在创建 Socket 前把另一个 Token 应用到线程，或由系统服务代为发起网络流量，过滤器未必能按预期跟踪该动作。

因此 WFP 过滤器不是“所有网络都无条件封死”的魔法开关。需要把 Token 变更、服务代发流量、Loopback Proxy、进程树和实际 Socket 创建身份纳入测试。注意这些限制针对 `srt-win` Backend，不能直接套用到可选的 MXC Backend。


## 14. srt-win 的共享 Windows 主机风险

当前 `srt-win` 还有一个容易漏掉的部署边界：

- Sandbox 用户与 Sandbox 组是**每台机器一份**，不是每个 Windows 用户各一份；
- 安装流程可把调用用户的 Profile 授权给 Sandbox 组读取（凭证目录会被排除）；这项 grant 由机器级 Sandbox 组持有；
- 因为 Sandbox 组是机器级的，同一台机器上其他有权使用 Sandbox 的本地用户，也可能通过自己的 Sandbox 命令读取已 grant 的目录；
- 在多人共用的 Windows 主机上，应使用 `--skip-profile-grant` / `skipProfileGrant: true`，或撤销已有 Profile grant；不要把单用户开发机的默认安装假设套到共享主机。

因此，`srt-win` 的专用用户并不等于“每个租户拥有独立 Sandbox 用户”。共享主机需要额外验证本地用户之间的读写隔离、持久 ACL grant 和代理身份。
