# 第 1 讲：什么是 Sandbox

## 1. 先不要背定义

Sandbox 可以先理解成：

> 给一个程序划定一块“只能在这里活动”的能力边界。

普通进程：

    Program
      ↓
    OS
      ↓
    Files / Network / Process / Device

Sandbox：

    Program
      ↓
    Sandbox Policy
      ↓
    OS
      ↓
    Files / Network / Process / Device

真正改变的是：程序能向操作系统提出哪些请求，以及哪些请求最终会被允许。

## 2. 普通程序为什么有能力影响系统

程序运行在用户态，但它需要 Kernel 帮忙做事情。

例如：

    open file
        ↓
    system call
        ↓
    Kernel
        ↓
    filesystem

再比如：

    socket
        ↓
    system call
        ↓
    Kernel
        ↓
    network stack

所以一个进程真正拥有的能力来自：

- 用户身份
- 文件权限
- 已打开的文件描述符
- capabilities
- namespace
- system calls
- network
- inherited environment

## 3. Sandbox 到底限制什么

可以分成六类：

| 能力 | 示例 | Sandbox 目标 |
|---|---|---|
| 文件 | 读取 SSH key | 限制路径 |
| 网络 | 访问任意域名 | 限制出口 |
| 进程 | 查看其他进程 | namespace |
| syscall | mount / ptrace | seccomp |
| 资源 | fork / memory / disk | quota |
| 凭证 | AWS / GitHub token | 不暴露 |

## 4. 为什么 AI Agent 特别需要

传统程序通常由开发者提前写好控制流。

AI Agent：

    User goal
       ↓
    LLM
       ↓
    Reasoning
       ↓
    Tool Calling
       ↓
    Shell / MCP / Browser
       ↓
    OS

模型会根据代码、README、网页、工具结果继续决定下一步。

所以不能把：

> “模型应该不会这么做”

当成安全机制。

正确模型：

    LLM 可以犯错
        ↓
    Tool 可能被诱导
        ↓
    Sandbox 阻止越界

## 5. Permission 和 Sandbox

Permission：

> 这一次要不要批准？

Sandbox：

> 即使批准，最多能做到什么？

例如：

    Agent: 删除 project/test.log
    Policy: allow
    Sandbox: 文件在 workspace
    Result: success

而：

    Agent: 删除 ~/.ssh/id_rsa
    Policy: 即使误判 allow
    Sandbox: workspace 外不可写
    Result: denied

这就是 Defense in Depth。

## 6. Sandbox 和 Docker

Docker 是容器技术。

Sandbox 是安全目标。

因此：

    Sandbox
      ├── OS-level sandbox
      ├── Container
      ├── MicroVM
      └── VM

都可能实现隔离，但层次不同。

## 7. 本讲实验

创建：

    sandbox-demo/
      workspace/
        hello.txt
      secret.txt

先用普通 subprocess 运行：

    cat workspace/hello.txt
    cat secret.txt

然后问自己：

> 如果 Agent 只应该访问 workspace，subprocess 本身为什么做不到？

下一讲开始回答。

## 面试题

### Q1：Sandbox 是什么？

是一种运行时安全隔离机制，通过限制进程的文件、网络、进程、系统调用、资源或凭证等能力，让不可信代码只能在预定义边界内运行。

### Q2：为什么 AI Agent 更需要 Sandbox？

因为 Agent 会动态生成和执行工具调用，行为具有不确定性，必须把安全边界放在模型之外的运行时。
