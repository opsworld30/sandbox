# 第 25 讲：拆解 Codex 的 Sandbox——真正的 Agent Runtime 是怎么分层的

这一讲不讨论“Codex 好不好用”，只做工程拆解：

> 一个 AI Coding Agent 为什么需要 Sandbox Manager，而不是简单地执行 shell？

## 1. 先看完整执行链

用户：

    “帮我修复这个项目，然后跑测试”

Agent 不会直接执行一句固定命令，而是不断产生：

    shell
    file read
    file write
    git
    test
    package manager

因此实际链路更接近：

    User
      ↓
    Model
      ↓
    Agent / Harness
      ↓
    Permission Policy
      ↓
    Sandbox Manager
      ↓
    OS Sandbox
      ↓
    child process tree

这里最重要的是：

> Model 决定“想做什么”，Sandbox 决定“最多能做到什么”。

## 2. Codex 为什么不是简单 Docker

截至 2026-11-18，Codex 官方 Sandbox 文档对本地执行环境的描述是：

    macOS
      → Seatbelt

    Linux / WSL2
      → bubblewrap（bwrap）Linux sandbox

    Windows PowerShell
      → native Windows sandbox

    Windows WSL2
      → Linux sandbox implementation

注意：不要把 Codex 当前 Linux 实现概括成 Landlock + seccomp。公开文档描述的主路径是 bwrap；Codex 的不同版本、不同平台和不同执行面可能有实现差异。

Codex Cloud 是远程执行环境，不能把它和本地 Codex 的 OS Sandbox 当成同一个 Backend。

这说明一个重要事实：

> Sandbox 是一个抽象，Backend 才是具体实现。

## 3. 你自己的项目应该怎么抽象

推荐：

    SandboxManager
          |
          +-- MacOSBackend
          |
          +-- LinuxBackend
          |
          +-- WindowsBackend
          |
          +-- ContainerBackend
          |
          +-- MicroVMBackend

Agent 只调用：

    sandbox.exec(...)
    sandbox.readFile(...)
    sandbox.writeFile(...)
    sandbox.destroy()

而不是：

    os.system("docker ...")

## 4. Permission 和 Sandbox 的关系

假设 Agent 要：

    git push

Permission Policy 先判断：

    是否需要用户批准？

如果批准：

    Sandbox 再判断：

    是否允许网络？
    是否允许访问 git credential？
    是否允许写 workspace？

所以：

    Permission
       ↓
    “允许不允许做”

    Sandbox
       ↓
    “即使允许，技术上最多做到哪里”

这是两个不同问题。

## 5. 为什么“Sandbox 失败后允许 Unrestricted”很危险

一种常见设计：

    sandbox exec
        ↓
    failed
        ↓
    retry without sandbox

从兼容性角度很方便。

但安全上意味着：

> Sandbox failure 可能自动变成 privilege escalation。

更安全：

    sandbox failed
       ↓
    explain reason
       ↓
    ask / policy review
       ↓
    explicit approval
       ↓
    unrestricted

## 6. Workspace Policy

典型 Agent Workspace：

    /project
      READ
      WRITE

    ~/.ssh
      DENY

    ~/.aws
      DENY

    /other-project
      DENY

    network
      DENY

如果需要安装依赖：

    network
      ↓
    allow selected destinations

而不是：

    network
      ↓
    allow all

## 7. Process Tree 是真正的边界

Agent：

    codex
      ↓
    bash
      ↓
    npm
      ↓
    node
      ↓
    child_process

如果只有第一层受限制：

    codex  ← sandbox
    bash   ← outside
    npm    ← outside

那 Sandbox 几乎没有意义。

正确目标：

    codex
      ↓ sandbox
    bash
      ↓ sandbox
    npm
      ↓ sandbox
    node
      ↓ sandbox

## 8. 这一讲你应该自己画出来

不要只记“Codex 使用 Seatbelt”。

请画：

    Codex
      ↓
    Permission
      ↓
    Sandbox Manager
      ↓
    ┌───────────────┐
    │ macOS         │
    │ Seatbelt      │
    ├───────────────┤
    │ Linux / WSL2  │
    │ bubblewrap    │
    ├───────────────┤
    │ Windows       │
    │ native        │
    └───────────────┘
      ↓
    Process Tree

## 9. 实验

在自己的 sandbox 项目中定义：

    interface SandboxBackend {
        Create(session)
        Exec(session, argv)
        ReadFile(session, path)
        WriteFile(session, path)
        Destroy(session)
    }

先实现：

    LocalBackend

再实现：

    LinuxBubblewrapBackend

这样你会真正理解：

> Runtime abstraction 为什么比“调用 Docker”更重要。

## 10. Windows 实现值得单独研究什么

OpenAI 2026 年公开的 Windows 工程文章描述了 Codex Windows Sandbox 的设计演进：

- AppContainer 对固定能力应用有价值，但对任意 shell / Git / Python / Node / build tool 这类开放式开发工作流不够合适；
- 早期 unelevated prototype 使用 synthetic SID、ACL 和 restricted token，但网络限制主要依赖环境变量，作者明确指出这属于 advisory，不能抵御直接 socket；
- 当前文章描述的 elevated design 使用专门的 Sandbox 用户、restricted token、ACL、Windows Firewall 规则，以及独立 setup / command-runner 进程。

不要把这篇文章的 Windows 实现简化成“只用 ACL”或“只用 WFP”。

## 11. 参考

OpenAI Codex sandboxing:
https://github.com/openai/codex/tree/main/codex-rs/sandboxing

Codex Sandbox docs:
https://developers.openai.com/codex/concepts/sandboxing

Codex Agent approvals & security:
https://learn.chatgpt.com/docs/agent-approvals-security

OpenAI Codex Windows sandbox engineering:
https://openai.com/index/building-codex-windows-sandbox/

**核验日期：2026-11-18。** Codex 的本地 Sandbox 会随版本更新；产品内部实现以当前官方文档和对应版本源码为准。


## 12. 需要避免的两个误解

1. Permission / Approval 和 Sandbox 是两层控制。批准某次操作，不等于 Sandbox 已自动扩大；是否允许在 Sandbox 外执行，取决于当前模式、规则和用户审批。
2. 不同 Codex surface（CLI、IDE、Desktop、Cloud、Agents API）不是同一套部署环境。讨论实现时必须先说清楚具体是哪一个产品面和执行位置。


## 13. Codex Linux 兼容性不是“安装 bwrap 就一定能启动”

当前官方文档指出，Codex 需要能够创建所需的 unprivileged user namespace。某些 Linux 发行版（例如特定 Ubuntu AppArmor 配置）会限制这一能力。遇到启动警告时，应先按官方说明配置 bwrap / AppArmor，而不是直接关闭系统的 user namespace 安全限制。

此外，Codex 的 Sandbox 适用于 Agent 启动的命令及其子进程；不要把它理解为系统上所有由 IDE 或其他服务独立启动的进程都会自动受限。

## 本讲实验代码

- [Runner / Session](../labs/03-runner-session/README.md)
- [Linux bubblewrap](../labs/04-bubblewrap/README.md)
- [Mini Runtime](../labs/17-mini-runtime/README.md)

这些是对应主题的可运行教学实验或产品设计复现；并非厂商内部实现的源码副本。
