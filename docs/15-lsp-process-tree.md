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

应该一致。

## 5. Process Tree 的继承

一个重要问题：

> child process 是否自动继承父进程的 Sandbox？

OS-level sandbox 的价值就在这里。

例如：

    sandboxed bash
       ↓
    python
       ↓
    node

只要 OS policy 作用于整个进程树，就不需要为每个语言 runtime 单独写一套安全系统。

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
