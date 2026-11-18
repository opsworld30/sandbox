# 第 15 讲：LSP、Tool 与 Process Tree

## 1. 为什么要讲 Process Tree

Agent 很少直接执行一个最终程序。

例如：

    Agent
      ↓
    bash
      ↓
    npm
      ↓
    node
      ↓
    child process

或者：

    Agent
      ↓
    Python
      ↓
    subprocess
      ↓
    compiler

如果只保护第一层：

    Agent

后面的 child process 就可能成为逃逸点。

## 2. Sandbox 应该覆盖 Process Tree

理想模型：

    Agent
      │
      └── Sandbox Boundary
            ├── bash
            ├── python
            ├── node
            ├── npm
            └── child processes

也就是：

> Sandbox 应该跟随执行树，而不是只保护某一个 PID。

## 3. LSP 为什么也值得保护

Language Server 可能：

    扫描项目
    读取文件
    分析依赖
    启动子进程
    使用缓存

例如：

    gopls
    pyright
    rust-analyzer
    typescript-language-server

它们虽然叫 Language Server，但实际上是长期运行的程序。

## 4. LSP 的风险

如果 LSP 可以：

    read /home/user

而 Agent 只允许：

    read /workspace

那么整体边界仍然被破坏。

因此：

    Agent Sandbox
       +
    LSP Sandbox

都需要独立且最小化的 Policy。LSP 通常只需要读取 Workspace 和有限的进程能力，不应因为 Agent Shell 可以写文件或联网，就自动继承同样宽泛的权限。

## 5. Process Tree 的继承

一个重要问题：

> child process 是否自动继承父进程的 Sandbox？

答案取决于具体 OS 机制和启动路径，不能只凭“它是 child”就下结论。

- Linux seccomp filter 会随 fork / clone / exec 继承；Landlock domain 也会限制调用线程及其未来子进程。
- Namespace 成员关系通常由子进程继承。
- macOS Seatbelt 受限进程启动的子进程通常继续处于相应约束中。
- 但由 IDE、Agent Host、MCP 管理器或其他独立服务启动的进程，可能不是这个进程树的一部分。

所以必须确认实际进程是从哪个 Host 启动的，以及该 Host 是否显式把它放入 Sandbox。

## 6. 为什么这比 Tool Blacklist 好

如果你写：

    deny curl
    deny nc

那么：

    python socket
    node net
    custom binary

仍然可能联网。

但如果：

    network policy
       ↓
    process tree

那么语言换了，安全边界仍然存在。

## 7. 本讲实验

在测试环境运行：

    bash
      ↓
    python
      ↓
    subprocess

观察 PID。

然后思考：

> 如果 bash 被 Sandbox 保护，python 是否还应该拥有更高权限？

正确答案：

> 不应该自动提升。

## 8. 面试题

### Q：为什么 Sandbox 必须考虑 child process？

因为 Agent 的工具经常通过 shell、runtime、build system 启动二级和三级进程。只保护入口进程会留下绕过路径。

### Q：为什么 LSP 也需要 Sandbox？

因为它本身会访问文件、依赖和系统资源，是 Agent Runtime 的一部分，而不是“纯文本服务”。


## 9. Process Tree 不等于只记录 parent PID

仅保存 root PID 后递归查找子 PID，再逐个 kill，可能遇到进程退出、PID 重用、子进程重新建立 session 或脱离进程组等竞态。

生产系统应优先使用可对整个 Session 生效的 OS 资源边界，例如 Linux cgroup v2 的进程集合，或 Windows Job Object。销毁时先终止该边界，再验证其中没有残留进程。

PTY 只是终端交互设备，不是进程隔离机制；PTY helper、shell 和其子进程必须处在同一 Sandbox 边界中。

## 本讲实验代码

- [Process Tree 清理](../labs/09-process-tree/README.md)
- [LSP / Tool Capability 分权](../labs/15-tool-capabilities/README.md)

这些是对应主题的可运行教学实验；具体操作系统要求和安全边界以各 Lab README 为准。
