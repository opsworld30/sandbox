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

公开的 Codex 安全资料显示，本地 Codex 会根据平台使用不同 Sandbox：

    macOS
      → Seatbelt

    Linux
      → seccomp + Landlock

    Windows
      → 原生 Windows sandbox implementation
      → 或 WSL/Linux sandbox 路径

而云端 Codex 则运行在隔离的容器环境中。

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
    │ Linux         │
    │ Landlock      │
    │ seccomp       │
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

## 10. 参考

OpenAI Codex sandboxing:
https://github.com/openai/codex/tree/main/codex-rs/sandboxing

OpenAI Codex security:
https://developers.openai.com/codex/security

OpenAI Codex Windows sandbox:
https://openai.com/index/building-codex-windows-sandbox/
