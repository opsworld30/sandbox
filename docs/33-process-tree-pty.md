# 第 33 讲：Process Tree、PTY、子进程——为什么只 Sandbox 一个 PID 不够

## 1. AI Agent 是天然的进程树

例如：

    agent
      └── bash
            └── npm
                  └── node
                        └── child_process

如果只限制：

    agent

而没有限制：

    descendants

那么真正执行代码的可能已经跑出 Sandbox。

## 2. Sandbox 必须从 root process 向下传播

理想：

    Sandbox Root
        ↓
      Agent
        ↓
      Shell
        ↓
      Compiler
        ↓
      Test
        ↓
      Child

所有 descendants 都在：

    same policy boundary

## 3. 为什么 Process Tree 还和 cleanup 有关

Agent 执行：

    npm test

可能产生：

    npm
      ├── node
      ├── vite
      ├── worker
      └── browser

如果只 kill：

    npm

下面的进程可能继续存在。

所以 destroy session 时需要：

    terminate process tree
       ↓
    wait
       ↓
    force kill
       ↓
    verify no descendants

## 4. PID tracking

Session：

    session-123

记录：

    root_pid = 1000

然后追踪：

    1000
      ├── 1001
      ├── 1002
      │    └── 1003
      └── 1004

Destroy：

    kill tree(1000)

但注意：

> PID tracking 本身不是安全边界。

真正的隔离还需要 OS sandbox。

## 5. PTY 是什么

很多 CLI 程序需要：

    TTY

例如：

    top
    vim
    interactive shell
    npm progress

如果只是：

    stdout pipe

行为可能不同。

所以 AI Coding Runtime 可能需要：

    PTY
      ↓
    Shell
      ↓
    Agent

## 6. PTY 和 Sandbox 的关系

PTY 本身不是 Sandbox。

但 PTY 是：

> Agent Runtime 的执行接口。

因此需要确保：

    PTY process
      ↓
    same Sandbox

而不是：

    Agent
      ↓ sandbox
    PTY helper
      ↓ outside sandbox

## 7. stdin 是另一个风险面

如果用户输入：

    Ctrl-C
    Ctrl-Z
    interactive command

Runtime 要决定：

    stdin:
      allow
      deny
      synthetic

对于 Agent：

    stdin usually controlled by runtime

不要把宿主机终端的全部能力无条件传进去。

## 8. Background process

例如：

    python server.py &

Agent 认为命令结束：

    exit = 0

但：

    server.py

还在运行。

如果没有 Session Process Manager：

    process leak
    port leak
    resource leak

## 9. 实验

实现：

    ProcessTreeManager

接口：

    spawn()
    listChildren()
    terminateTree()
    waitTreeGone()

测试：

    python -c "import subprocess; subprocess.Popen(['sleep','60'])"

执行 destroy。

目标：

    parent gone
    child gone

## 10. 核心结论

Sandbox 的对象不是：

> 一个命令。

而是：

> 一个受约束的 Process Tree。


## 11. Process Group 与 cgroup 不是一回事

POSIX process group 可以帮助发送信号，但子进程可能通过 `setsid()` 等方式脱离原进程组。只记录 PID 或 kill 一个 process group 都不一定能覆盖整个 Session。

Linux 生产环境应优先使用 cgroup v2 将 Session 的全部进程纳入同一个控制组；销毁时终止整个 cgroup，并验证进程数归零。Windows 可使用 Job Object 管理进程树。具体平台要选能防止子进程脱离管理的机制。

## 12. PTY 不提供安全隔离

PTY 解决终端交互、控制字符和 TTY 语义；它本身不限制文件、网络、进程或资源。PTY helper、shell 和所有子进程都必须在正确的 Sandbox / cgroup / Job Object 中运行。
