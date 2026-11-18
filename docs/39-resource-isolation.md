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

    cgroups
    RLIMIT_NPROC
    PID namespace

不同机制解决的问题不同。

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

> 资源控制和统计。

典型：

    Sandbox cgroup
       ├── cpu
       ├── memory
       ├── pids
       ├── io
       └── ...

Process tree：

    Agent
      ├── bash
      ├── node
      └── compiler

都进入同一个 cgroup。

于是资源限制天然作用于整个 Session。

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
