# Lab 02：亲手跑一次 Landlock

这个实验解决：

> seccomp 已经知道“哪些 syscall”，那怎么表达“只能访问 workspace”？

答案：Landlock。

## 环境

Linux 测试 VM。

建议：

    sudo apt-get update
    sudo apt-get install build-essential

需要启用 Landlock 的 Linux Kernel，以及包含 Landlock UAPI 定义的内核头文件。程序会先查询运行中 Kernel 的 Landlock ABI 版本；如果内核不支持或未启用 Landlock，会明确报错退出。

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
      → allow read

    secret.txt
      → deny read

    workspace/created.txt
      → allow create + write

本实验只验证代码中明确列入 `handled_access_fs` 的权限。Landlock 的规则集只会拒绝被标记为 handled 的访问类型；没有列入的权限不会自动变成 deny。因此它仍然不是完整的生产级文件系统策略。

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

> 调用线程进入 Landlock domain；之后由它创建的子进程/线程会继承限制。

注意：`landlock_restrict_self()` 不会自动追溯限制已经存在的其他线程。实际程序应在创建工作线程之前安装策略，或确保所有需要保护的线程都分别处于正确的 Landlock domain。

## 注意

这个程序是教学 Demo，不是生产 Sandbox。

生产环境还需要考虑：

- 按运行中 Kernel ABI 协商支持的访问权限；
- `REFER`、`TRUNCATE` 等不同 ABI 才提供的权限；
- symlink、hardlink、路径解析与 TOCTOU；
- 在进入 domain 前打开的 FD，以及继承/传递的 FD；
- 线程和子进程的继承关系；
- network（Landlock 的网络规则是端口级，不是域名白名单）；
- syscall、资源、凭证和 Unix socket；
- Kernel / headers 版本兼容性。

Landlock 是附加限制层，不会授予进程原本没有的权限。
