# 第 8 讲：seccomp 到底是什么

> 这一讲专门解决一个问题：为什么“禁止某些 syscall”真的能形成 Sandbox？

## 1. 程序为什么需要 System Call

用户程序不能直接操作 Kernel。

例如读取文件：

    Application
       ↓
    libc / runtime
       ↓
    openat()
       ↓
    Linux Kernel
       ↓
    Filesystem

建立网络连接：

    Application
       ↓
    socket()
       ↓
    connect()
       ↓
    Linux Kernel
       ↓
    Network Stack

所以 System Call 是：

> 用户态程序请求 Kernel 执行特权操作的正式入口。

## 2. seccomp 是什么

seccomp 是 Secure Computing。

Linux Kernel 提供 seccomp 机制，让进程可以安装一个 filter。

之后进程每次进入 Kernel 发起 system call：

    syscall
       ↓
    seccomp filter
       ↓
    allow / deny / error / kill / log / notify
       ↓
    Kernel

这就是它为什么重要。

## 3. 为什么不是“禁止 Linux 命令”

例如：

    curl https://example.com

curl 只是一个用户态程序。

内部可能调用：

    socket()
    connect()
    send()
    recv()
    close()

如果 Sandbox 禁止 socket：

    curl
      ↓
    socket()
      ↓
    Kernel
      ↓
    seccomp
      ↓
    DENY

所以：

> 不管程序叫 curl、Python、Node 还是自定义二进制，只要它最终调用被过滤的 syscall，就会在 Kernel 入口被拦截。

## 4. seccomp 使用什么过滤器

seccomp filter 使用 BPF。

可以把它想成：

    syscall request
          ↓
    ┌────────────────────┐
    │ BPF filter         │
    │                    │
    │ syscall == read ?  │
    │ syscall == write ? │
    │ syscall == mount ? │
    │ syscall == ptrace? │
    └─────────┬──────────┘
              ↓
          decision

Filter 不只可以判断 syscall number，还可以检查 seccomp 提供的原始参数值（例如整数、flags、fd、socket family 等）。

**关键限制：** syscall 参数中的指针只是用户态地址。seccomp BPF 不能像普通程序一样安全地解引用指针内容。因此它不能直接读取 `openat("/workspace/a")` 中的路径字符串，也不能直接解析 `connect()` 指向的 sockaddr 并按域名做白名单。文件路径应该交给 Landlock / mount namespace 等机制，网络目的地应该交给 Network Namespace、Firewall 或强制 Proxy。

## 5. 为什么需要它

AI Agent 可以执行任意语言：

    bash
    python
    node
    go
    rust

你无法靠：

    if command contains "mount"

来保证安全。

因为程序最终可能通过：

    Python
      ↓
    native library
      ↓
    syscall

真正可靠的边界应该靠 OS / Kernel。

## 6. seccomp 的常见动作

### ALLOW

继续执行 syscall。

### ERRNO

不执行 syscall，直接给程序返回错误。

    EPERM

### KILL_PROCESS / KILL_THREAD

直接终止。

### TRAP

触发 SIGSYS，用于特殊处理。

### LOG

记录 syscall，同时允许继续执行。它不是拒绝动作；被标记的 syscall 仍会执行。该动作是否可用、日志是否实际写入，取决于 Kernel 版本、配置和审计设置。可用 `SECCOMP_GET_ACTION_AVAIL` 检查动作支持情况。

### USER_NOTIF

把特定 syscall 请求通知用户态 supervisor。

这个机制很重要，因为它意味着：

    Program
      ↓
    Kernel
      ↓
    seccomp notification
      ↓
    Supervisor
      ↓
    allow / deny / respond

这已经开始接近 Policy Engine。

但 USER_NOTIF 不是“把任意 syscall 安全搬到用户态执行”的通用机制。特别是涉及用户态指针、文件路径、文件描述符和 TOCTOU 的请求，supervisor 必须谨慎处理；不要把收到通知后直接代替目标进程执行操作当成安全设计。

## 7. 为什么不能全部禁止

一个普通程序启动就需要很多 syscall，例如：

    execve
    openat
    mmap
    mprotect
    read
    close
    futex
    exit_group

Python、Node、Go、Rust 又有不同运行时。

如果 filter 太严格：

    Program
      ↓
    startup
      ↓
    syscall denied
      ↓
    Program crashes

所以 seccomp 最大的工程难点之一是：

> Security 和 Compatibility 的平衡。

## 8. 生产环境怎么建立 syscall policy

推荐流程：

### 第一步：观察

使用 strace 等工具观察程序正常运行需要什么 syscall。

    strace -f -o trace.log python -c "print('hello')"

注意：

> strace 是观察工具，不是 Sandbox。

### 第二步：建立 baseline

分别观察：

    python
    node
    git
    npm
    pytest

### 第三步：识别高风险 syscall

    mount
    ptrace
    reboot
    kexec_load
    bpf
    keyctl
    unshare
    setns

不要直接复制网上 profile。真正允许什么取决于程序、架构和内核。

## 9. seccomp 什么时候安装

常见的启动模型：

    Parent
      ↓
    fork
      ↓
    Child
      ↓
    no_new_privs
      ↓
    install seccomp filter
      ↓
    exec target

注意三件事：

1. 如果在 `exec target` 之前安装 filter，filter 必须允许启动目标程序所需的 `execve` / `execveat`；否则目标根本启动不了。
2. filter 默认安装在调用它的线程上。新创建的子进程 / 线程会继承限制，但已经存在的其他线程不会自动全部被同步限制。
3. 如果要同步限制一个多线程进程的现有线程，需要研究 libseccomp 的 TSYNC 属性 / Kernel 对应能力；更简单可靠的设计通常是在创建工作线程前安装 filter。

## 10. no_new_privs 为什么经常出现

无特权进程安装 seccomp filter 时，通常需要先设置 `no_new_privs`，除非调用者具备相应 namespace 中的 `CAP_SYS_ADMIN`。

常见模型：

    PR_SET_NO_NEW_PRIVS
           ↓
    seccomp filter
           ↓
    exec target

no_new_privs 可以防止 exec 过程中通过 setuid / file capabilities 等机制获得新的特权。

## 11. libseccomp

手写 BPF 很容易出错。

实际工程通常可以使用 libseccomp 这样的高层库。

概念代码：

    ctx = seccomp_init(ERRNO(EPERM))

    allow(ctx, read)
    allow(ctx, write)
    allow(ctx, close)

    seccomp_load(ctx)

库负责把更容易理解的规则转换成 Kernel 可执行的 filter。

补充：seccomp 的默认动作和允许规则必须结合目标程序启动流程设计。不要为了“默认拒绝”而漏掉运行时需要的 syscall；也不要把一个 Python profile 当成 Node、Git、编译器都能安全复用的通用 profile。

## 12. seccomp 和 Landlock 的区别

这是本课程最重要的对比之一：

| 技术 | 主要问题 |
|---|---|
| Namespace | 我能看到什么 |
| Landlock | 我能对哪些文件/网络资源做什么 |
| seccomp | 我能向 Kernel 请求什么 |
| cgroups | 我最多消耗多少资源 |
| capabilities | 我有哪些特权 |
| no_new_privs | exec 后不能获得新特权 |

记忆：

> Namespace 看见什么，Landlock 能做什么，seccomp 能调用什么，cgroups 能用多少。

## 13. 为什么 seccomp 不能代替 Filesystem Sandbox

假设允许：

    openat()

那么程序仍然可以请求：

    openat("/home/user/.ssh/id_rsa")

seccomp 不适合直接表达：

> 只允许 /workspace。

所以需要：

    seccomp
      +
    Landlock / mount namespace

## 14. 为什么 AI Coding Sandbox 要组合

完整模型：

    AI Agent
       ↓
    Sandbox Manager
       ↓
    Filesystem Policy → Landlock / namespace
       ↓
    Network Policy    → proxy / namespace
       ↓
    Syscall Policy    → seccomp
       ↓
    Resource Policy   → cgroups
       ↓
    Kernel

## 15. 本讲实验

建议在 Linux 测试 VM 中完成。

第一步：

观察 Python 启动时的 syscall。

第二步：

比较：

    python
    node
    git

第三步：

使用一个最小 seccomp 示例，让一个测试 syscall 返回 EPERM。

不要直接在日常工作机上安装未知的严格 filter。

## 16. 这一讲真正应该理解的结论

> seccomp 是 Linux Kernel 提供的 syscall filtering 机制。进程进入 Kernel 请求 system call 时，Kernel 可以依据 filter 决定允许、返回错误、记录、终止或交给用户态 supervisor。

再加一句：

> seccomp 解决的是“进程可以向 Kernel 请求什么”，不是“进程可以访问哪个目录”。

## 面试题

### Q1：为什么 seccomp 比命令黑名单可靠？

因为它工作在 syscall 边界，而不是命令字符串边界。

### Q2：seccomp 能直接限制路径吗？

它不是做路径授权的主要机制。文件路径通常交给 Landlock、mount namespace 等机制。

### Q3：为什么生产环境不能随便复制 seccomp profile？

因为不同程序需要不同 syscall；过严会破坏兼容性，过松又可能扩大攻击面。

## 官方资料

Linux Kernel Seccomp:
https://kernel.org/doc/html/latest/userspace-api/seccomp_filter.html

seccomp(2):
https://man7.org/linux/man-pages/man2/seccomp.2.html

PR_SET_SECCOMP:
https://man7.org/linux/man-pages/man2/PR_SET_SECCOMP.2const.html

Docker Seccomp:
https://docs.docker.com/engine/security/seccomp/

## 17. 对应实战代码

本仓库提供一个最小 libseccomp 实验：

    labs/01-seccomp/seccomp_demo.c

它故意使用：

    default = ALLOW
    mkdir = ERRNO(EPERM)

原因是教学阶段我们只想观察一个明确的变化：

    普通程序
      ↓
    mkdir
      ↓
    success

变成：

    seccomp loaded
      ↓
    mkdir
      ↓
    Kernel
      ↓
    EPERM

这比直接给一个巨大 allowlist 更适合第一次理解 seccomp。

运行：

    cd labs/01-seccomp
    make
    ./seccomp_demo

### 18. 为什么这个例子比“read / write / open allowlist”更适合入门

因为生产级 allowlist 很容易让初学者陷入：

    “到底允许多少 syscall？”

但第一次学习 seccomp 真正应该理解的是：

    1. filter 是进程的一部分；
    2. filter 被加载到 Kernel；
    3. syscall 发生时 Kernel 会检查；
    4. 命中规则后可以返回 EPERM；
    5. 没命中的 syscall 继续执行。

等这个模型理解后，再学习：

    default deny
    syscall allowlist
    argument filtering
    USER_NOTIF
    filter stacking
    TSYNC

会容易很多。

## 19. 线程、继承和参数检查的三个考点

### Filter 是按线程安装的

seccomp filter 作用于调用它的线程。由该线程创建的子进程 / 线程会继承 filter；已经存在的其他线程不一定自动受到影响。多线程程序应在创建线程前安装，或明确使用 TSYNC 同步策略。

### Filter 是随进程继承的

在允许 `fork` / `clone` 的前提下，子进程会继承父进程 filter；`execve` 后 filter 仍然生效。这也是为什么应该在目标程序启动前建立限制。

### 指针参数不能直接作为路径策略

seccomp 可以检查 syscall 参数中的数值，但不能直接检查 `openat` 的 pathname 字符串或 `connect` 的 sockaddr 内容。不要尝试用 seccomp 单独实现“只允许访问 /workspace”或“只允许访问 github.com”。

## 20. 本节代码的实验范围

本仓库 Lab 01 使用 `default = ALLOW`，仅拦截一个明确 syscall，让你观察 Kernel 返回 EPERM。它不是生产级 allowlist，也不是完整 Sandbox。

更重要的是，示例通过 `syscall(SCMP_SYS(mkdir), ...)` 直接调用目标 syscall，避免 libc 包装函数可能选择 `mkdirat` 等实现路径导致实验结果不一致。

## 参考补充

- Seccomp filter：https://www.kernel.org/doc/html/latest/userspace-api/seccomp_filter.html
- seccomp(2)：https://man7.org/linux/man-pages/man2/seccomp.2.html
- libseccomp：https://github.com/seccomp/libseccomp
