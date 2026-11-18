# 第 39 讲：Resource Isolation——为什么 Sandbox 不只是权限问题

## 1. 一个很容易忽略的问题

假设 Agent 不能读：

    ~/.ssh

但它可以：

    fork()

无限创建进程。

或者：

    while true:
        allocate_memory()

或者：

    write huge_file

这时候：

> 它没有越权访问文件，但它可以把机器拖死。

这叫：

> Resource Exhaustion

## 2. Sandbox 至少需要限制

    CPU
    Memory
    Disk
    Processes
    File size
    Output
    Time
    Network bandwidth

## 3. Timeout

最简单：

    timeout = 30s

超过：

    terminate process tree

但注意：

> kill parent 不一定 kill children。

所以应该：

    timeout
      ↓
    terminate process group/tree
      ↓
    wait
      ↓
    force kill
      ↓
    verify cleanup

## 4. Process Limit

Fork Bomb：

    while true:
        fork()

如果没有：

    process limit

就可能：

    PID exhausted
    CPU exhausted

Linux 可以结合：

    cgroups v2 pids.max
    RLIMIT_NPROC
    PID namespace

不同机制解决的问题不同。cgroup v2 的 `pids.max` 限制的是 cgroup 中的 tasks 数量（线程也计入），不只是传统意义上的进程数。注意 `RLIMIT_NPROC` 通常按 real UID 统计进程 / 线程数，不是天然的 per-Session 限额；多个 Sandbox 共用 UID 时，使用 cgroup pids controller 通常更适合做 Session 级限制。

## 5. Memory

例如：

    data = "x" * 10GB

需要：

    memory.max

或者其他资源控制。

关键：

> Memory limit 应该由 Runtime / OS enforce，而不是 Agent 自己承诺。

## 6. CPU

死循环：

    while True:
        pass

不需要访问任何敏感资源，也能占满 CPU。

因此：

    CPU quota
    CPU shares
    runtime timeout

都需要考虑。

## 7. Disk

Agent 可以：

    dd if=/dev/zero of=huge

即使：

    filesystem path

完全正确，也可能把磁盘写满。

所以：

    workspace quota
    tmp quota
    inode quota

也属于 Sandbox。

## 8. Output Limit

一个程序可以：

    print("A" * 100GB)

即使：

    CPU
    filesystem

都没越权。

它仍然可能：

    memory exhaustion
    log storage exhaustion
    network exhaustion

因此 Runtime 应限制：

    stdout bytes
    stderr bytes

例如：

    1 MB

超过：

    truncate
    terminate
    or stream-to-limited-store

## 9. cgroups

Linux cgroups 解决：

> 对一组进程进行资源控制和统计。

典型 cgroup v2 控制器：

    Sandbox cgroup
       ├── cpu
       ├── memory
       ├── pids
       └── io

注意：`io` 控制器主要控制 I/O 带宽 / IOPS 等资源，不等于磁盘容量配额。磁盘空间上限通常需要文件系统 quota、project quota 或独立受限 volume。

Process tree：

    Agent
      ├── bash
      ├── node
      └── compiler

在可信 Host 将 Session 进程放入 cgroup、且不向不可信进程开放迁移权限的前提下，子进程会继承该 cgroup，资源限制作用于整个受控进程集合。不要把“创建了 cgroup”误认为所有后续进程自动无法逃离；还必须保护 cgroupfs 的写权限和生命周期。

## 10. Resource Policy

可以设计：

    ResourcePolicy {
        timeout: 30s
        memory: 2GB
        cpu: 2 cores
        pids: 256
        disk: 5GB
        stdout: 10MB
    }

然后：

    Policy
      ↓
    Resource Backend
      ↓
    cgroup / rlimit / runtime

## 11. 为什么 Resource Isolation 也是安全

因为：

> Availability 本身就是安全目标。

攻击者不一定要：

    steal secret

也可以：

    destroy availability

所以 Sandbox 需要同时防：

    Confidentiality
    Integrity
    Availability

也就是：

    C
    I
    A

## 12. 实验

安全测试程序：

    infinite_cpu
    infinite_fork
    huge_memory
    huge_output
    huge_file

每个都只在 disposable VM / test host 运行。

然后测试：

    timeout
    memory
    process
    disk
    output

## 13. 面试题

为什么 cgroups 和 seccomp 都需要？

seccomp 控制 syscall 能力，cgroups 控制资源消耗。一个限制“能请求什么”，一个限制“最多消耗多少”。


## 14. cgroup v2 与 RLIMIT 的职责边界

| 需求 | 常见机制 | 说明 |
|---|---|---|
| CPU 配额 | cgroup `cpu.max` | 限制一组进程的 CPU 使用比例 |
| 内存上限 | cgroup `memory.max` | 限制 cgroup 内存使用 |
| 进程 / task 数量 | cgroup `pids.max` | 限制 cgroup 中的 tasks（包含线程）；比共享 UID 下的 RLIMIT_NPROC 更适合 per-session |
| I/O 限制 | cgroup `io.max` / `io.weight` | 控制 I/O 速率或权重，不是磁盘容量 |
| 单文件大小 | `RLIMIT_FSIZE` | 限制单个文件可创建的最大大小 |
| 文件描述符 | `RLIMIT_NOFILE` | 限制进程可打开 FD 数量 |
| 磁盘容量 | filesystem quota / project quota | 需要文件系统或存储层支持 |

资源策略必须在 OS / 存储层强制执行，不应只靠应用层计数器。


## 参考

- Linux cgroup v2：https://docs.kernel.org/admin-guide/cgroup-v2.html
- Linux `getrlimit(2)` / `setrlimit(2)`：https://man7.org/linux/man-pages/man2/getrlimit.2.html

## 本讲实验代码

- [CPU / Memory / File Size Limits](../labs/14-resource-limits/README.md)

这些是对应主题的可运行教学实验；实际 OS 隔离能力和模拟策略的区别以各 Lab README 为准。
