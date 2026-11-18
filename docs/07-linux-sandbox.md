# 第 7 讲：Linux Sandbox——Namespace、Landlock、bubblewrap

## 1. Linux Sandbox 不是一个技术

常见组合：

    Namespace
    Landlock
    seccomp
    capabilities
    no_new_privs
    cgroups

每个东西解决的问题不同。

## 2. Namespace：改变“我看到的世界”

PID Namespace：

宿主机可能有：

    PID 1
    PID 100
    PID 200
    PID 300

Sandbox 内看到：

    PID 1
    PID 2
    PID 3

Mount Namespace：

宿主机：

    /
      home
      etc
      var
      secret

Sandbox：

    /
      usr
      workspace
      tmp

所以 Namespace 更偏向：

> Resource View Isolation

## 3. User Namespace

User Namespace 可以建立独立的 UID/GID 映射。

它是很多 unprivileged sandbox 的基础。

但：

> Namespace 本身不是完整安全边界。

还需要考虑 capabilities、Landlock、seccomp、no_new_privs 等。

## 4. bubblewrap

bubblewrap 是 Linux 上常见的 sandbox 构造工具。

概念命令：

    bwrap       --ro-bind /usr /usr       --proc /proc       --dev /dev       --unshare-pid       --new-session       bash

它主要负责：

    创建 namespace
       ↓
    构造 filesystem view
       ↓
    启动 child process

它不是 Docker 的替代品，而是一个更聚焦的 sandbox builder。

## 5. Landlock

Landlock 是 Linux Kernel 提供的 unprivileged access-control 机制。

它更适合表达：

    /workspace
      read
      write
      execute

    /other
      deny

也可以限制网络访问。

## 6. seccomp

seccomp 更关注：

> 这个进程可以调用哪些 system call？

所以：

    Namespace
      → 看见什么

    Landlock
      → 文件/网络能做什么

    seccomp
      → 能请求哪些 Kernel API

## 7. no_new_privs

no_new_privs 的目标之一是防止进程通过 exec 等方式获得新的特权。

它不是 Sandbox，但常作为 self-sandboxing 的重要基础。

## 8. 现代 AI Coding 的组合

可以理解成：

    Agent
      ↓
    Sandbox Manager
      ↓
    Permission Profile
      ↓
    ┌──────────────┐
    │ Filesystem   │ → Landlock / mount namespace
    │ Process      │ → PID namespace
    │ Syscall      │ → seccomp
    │ Network      │ → proxy / namespace
    └──────────────┘

OpenAI Codex 当前公开实现可以看到 Linux 路径组合 Landlock/seccomp，并使用 sandbox manager 与 bubblewrap 等组件。

## 面试题

Namespace、Landlock、seccomp 的区别？

Namespace 改变资源视图，Landlock 对资源访问增加限制，seccomp 过滤 system call。它们互补，不是互相替代。

## 参考

Landlock:
https://docs.kernel.org/userspace-api/landlock.html

bubblewrap:
https://github.com/containers/bubblewrap

Codex sandbox manager:
https://github.com/openai/codex/blob/main/codex-rs/sandboxing/src/manager.rs
