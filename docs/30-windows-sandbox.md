# 第 30 讲：Windows 为什么难——从 Codex Windows Sandbox 看“自己造安全边界”

## 1. 为什么 Windows 是一个很好的案例

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

## 2. 为什么 AppContainer 不够

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

## 3. Windows ACL 的问题

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

## 4. Network 更难

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

## 5. Windows 的一个关键思想

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

## 6. 为什么这是一个非常好的面试题

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

## 7. 实验

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

## 8. 参考

OpenAI:
https://openai.com/index/building-codex-windows-sandbox/
