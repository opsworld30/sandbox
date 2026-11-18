# Lab 01：亲手跑一次 seccomp

这一实验只做一件事：

> 让一个正常的 Linux C 程序在运行过程中禁止 `mkdirat` 系统调用。

目的不是做生产 Sandbox，而是亲眼看到：

    Program
      ↓
    mkdir()
      ↓
    Kernel
      ↓
    seccomp filter
      ↓
    EPERM

## 环境

建议 Ubuntu / Debian 测试 VM。

安装：

    sudo apt-get update
    sudo apt-get install build-essential libseccomp-dev strace

## 编译

    make

## 运行

    ./seccomp_demo

程序会：

1. 初始化 libseccomp；
2. 默认允许 syscall；
3. 添加原生架构的 `mkdir` syscall → EPERM 规则；
4. 加载 filter；
5. 通过 `syscall(SCMP_SYS(mkdirat), AT_FDCWD, ...)` 直接发起这个 syscall；
6. 观察 Kernel 返回 EPERM。

这里直接调用目标 syscall，而不是依赖 `mkdtemp()` 或 libc 包装函数；使用 `mkdirat` 也能避免不同架构的 libc 选择不同底层 syscall 所产生的歧义。

## 你要观察什么

最重要的是：

    seccomp_rule_add(...)
        ↓
    seccomp_load(...)
        ↓
    syscall(SCMP_SYS(mkdir), ...)
        ↓
    mkdirat syscall
        ↓
    Kernel
        ↓
    EPERM

程序不是“被禁止执行 mkdtemp”。

真正被禁止的是它底层发出的 mkdir syscall。

## 用 strace 对比

先看普通程序：

    strace -f ./seccomp_demo

然后关注：

    mkdirat
    openat
    write
    exit_group

你会看到程序仍然可以正常执行大量 syscall，但 mkdir 被 filter 改变了结果。

## 进一步实验

把：

    SCMP_ACT_ERRNO(EPERM)

改成：

    SCMP_ACT_LOG

然后观察系统日志。

再把它改成：

    SCMP_ACT_KILL_PROCESS

程序会被 Kernel 直接终止。

不要在自己的 Shell、SSH 服务或 IDE 进程上做这个实验。

## 这个实验告诉你的真正结论

seccomp 不是：

    “禁止 mkdir 命令”

而是：

    “当进程向 Kernel 请求 mkdirat syscall 时，Kernel 根据 filter 决定如何处理。”

这就是 Kernel-level enforcement。
