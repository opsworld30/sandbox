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

本实验主要验证代码中明确列入 `handled_access_fs` 的文件系统权限。一般而言，未列入 handled 的访问类型不会自动按本规则集拒绝；但 `LANDLOCK_ACCESS_FS_REFER` 有特殊的默认限制语义，不能把这句话当作绝对规则。本 Demo 也没有覆盖所有 ABI 权限，因此仍然不是完整的生产级文件系统策略。

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

注意：本实验使用 flags=0，因此不会自动同步限制已经存在的其他线程。Landlock ABI v8 起可使用 `LANDLOCK_RESTRICT_SELF_TSYNC` 将规则同步到当前进程所有线程。实际程序应按运行中 ABI 明确选择在线程创建前安装策略，或使用 TSYNC。

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


### 多线程程序的额外说明

本实验调用 `landlock_restrict_self(ruleset_fd, 0)`，因此按单线程 Demo 设计。Landlock ABI v8 起提供 `LANDLOCK_RESTRICT_SELF_TSYNC`，可以把规则同步应用到调用进程的所有线程；生产实现应检测 ABI，并明确决定是在线程创建前安装，还是使用 TSYNC。