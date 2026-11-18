# 第 38 讲：Sandbox Escape——真正理解“隔离”要从绕过开始

## 1. 为什么必须学 Escape

如果只学习：

    allow
    deny

你只能知道 Sandbox 怎么工作。

学习 Escape 后才能知道：

> Sandbox 到底在哪里可能失效？

## 2. 常见绕过面

### A. 文件系统

    symlink
    hardlink
    path traversal
    mount
    inherited fd

### B. 进程

    fork
    exec
    daemon
    background process

### C. 网络

    direct socket
    DNS
    IPv6
    proxy bypass
    localhost
    Unix socket

### D. 凭证

    environment
    /proc
    SSH agent
    Docker socket

### E. Kernel

    syscall
    namespace
    capabilities
    kernel vulnerability

## 3. Symlink Escape

假设：

    /workspace/link
       ↓
    /home/user/.ssh

程序访问：

    /workspace/link/id_rsa

如果策略只检查：

    path.startsWith("/workspace")

就可能被绕过。

所以路径安全必须考虑：

    canonicalization
    symlink resolution
    race conditions

## 4. TOCTOU

这是非常重要的概念：

    Check
      ↓
    file == safe

然后：

    attacker changes file
      ↓
    Use

于是：

    Time Of Check
       !=
    Time Of Use

这就是：

> TOCTOU

所以安全代码尽量让：

    Check
    +
    Open
    +
    Enforcement

由 OS 原语共同完成，而不是只依赖字符串路径判断。

## 5. /proc

Linux：

    /proc

可能暴露：

    process information
    environment
    file descriptors
    command line

因此 Sandbox 的 process isolation 经常需要：

    PID namespace
    mount namespace
    restricted proc

否则：

    Agent
      ↓
    /proc
      ↓
    host process information

## 6. Unix Socket Escape

例如：

    /var/run/docker.sock
    /tmp/important-service.sock

如果 Agent 可以访问：

    socket
      ↓
    privileged service

它可能完全绕过文件和 syscall policy。

所以：

> Socket 本身就是一种 capability。

## 7. Capability 思维

不要只问：

    “Agent 能不能访问文件？”

应该问：

    “Agent 拿到了哪些 capability？”

例如：

    file read
    file write
    network connect
    process spawn
    credential sign
    docker control

每一个都是能力。

## 8. Sandbox Escape 的正确学习方式

不要一开始在真实机器上做攻击实验。

使用：

    disposable VM
    toy sandbox
    intentionally vulnerable lab

然后：

    attack
      ↓
    observe
      ↓
    patch
      ↓
    regression test

## 9. Escape Test Matrix

    Filesystem
      ├── ../
      ├── symlink
      ├── hardlink
      └── inherited fd

    Network
      ├── localhost
      ├── private IP
      ├── IPv6
      └── proxy bypass

    Process
      ├── fork
      ├── daemon
      └── background

    Credential
      ├── env
      ├── /proc
      └── socket

## 10. 核心结论

> 一个 Sandbox 是否安全，不应该只通过“正常命令能不能跑”判断，而应该通过“恶意进程能不能越界”判断。

这就是为什么后面要做：

    Security Test Suite
    +
    Escape Challenge
