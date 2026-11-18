# Lab 02：亲手跑一次 Landlock

这个实验解决：

> seccomp 已经知道“哪些 syscall”，那怎么表达“只能访问 workspace”？

答案：Landlock。

## 环境

Linux 测试 VM。

建议：

    sudo apt-get update
    sudo apt-get install build-essential

较新的 Linux Kernel 和内核头文件需要支持 Landlock。

## 准备

    mkdir -p workspace
    echo "hello from workspace" > workspace/hello.txt
    echo "fake secret" > secret.txt

目录：

    lab/
      workspace/
        hello.txt
      secret.txt

## 编译

    make

## 运行

    ./landlock_demo

预期：

    workspace/hello.txt
      → allow

    ../secret.txt
      → deny

    workspace/created.txt
      → allow write

## 这个实验和 seccomp 的区别

seccomp：

    syscall
      ↓
    filter
      ↓
    allow / deny

Landlock：

    path
      ↓
    access rule
      ↓
    allow / deny

所以：

    seccomp
      解决“能调用什么”

    Landlock
      解决“能对哪些文件做什么”

## 关键调用顺序

程序大致做：

    landlock_create_ruleset
          ↓
    landlock_add_rule
          ↓
    PR_SET_NO_NEW_PRIVS
          ↓
    landlock_restrict_self
          ↓
    normal file operations

一旦 restrict_self 成功：

> 当前线程进入 Landlock domain，后续创建的 child 也会受到这个限制。

## 注意

这个程序是教学 Demo，不是生产 Sandbox。

生产环境还需要考虑：

- symlink；
- inherited FD；
- network；
- process tree；
- syscall；
- resource；
- credentials；
- kernel compatibility。
