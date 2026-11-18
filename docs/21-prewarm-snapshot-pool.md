# 第 21 讲：Prewarm、Snapshot 与 Sandbox Pool

## 1. 为什么性能突然变成核心问题

AI Agent 可能频繁创建 Sandbox：

    request
      ↓
    create
      ↓
    install
      ↓
    execute
      ↓
    destroy

如果每次都从零开始：

    image pull
    package install
    runtime start

延迟会非常高。

## 2. Prewarm

思路：

    Sandbox
       ↓
    prepare dependencies
       ↓
    ready
       ↓
    wait
       ↓
    attach Agent

也就是：

> 把用户等待时间提前到用户真正发起任务之前。

OpenAI 当前公开的 Pre-warm Sandbox 就是这个思路：先准备环境、包、文件和 setup commands，之后再把环境附加到 Agent Session。

## 3. Snapshot

另一种思路：

    Base Environment
       ↓
    Snapshot
       ↓
    New Sandbox

可以避免每次重新：

    install dependency

## 4. Copy-on-write

假设：

    Base
      ├── Python
      ├── Node
      └── dependencies

多个 Session：

    Session A
    Session B
    Session C

共享只读 Base。

写入时：

    Session A
       ↓
    private layer

这就是 Copy-on-write 的核心思路。

## 5. Sandbox Pool

可以提前准备：

    Ready Sandbox 1
    Ready Sandbox 2
    Ready Sandbox 3
    Ready Sandbox 4

请求来了：

    Agent
      ↓
    checkout Sandbox 2

使用结束：

    reset
      ↓
    pool

## 6. Pool 的最大问题

不能简单：

    destroy
      ↓
    reuse

因为可能残留：

- files；
- processes；
- sockets；
- environment variables；
- cache；
- credentials；
- browser state。

所以 reset 必须是：

> 安全重置，而不是简单删除几个文件。

## 7. Snapshot 安全问题

Snapshot 可能包含：

    token
    cookies
    SSH agent state
    private files
    process memory

因此：

> Snapshot 本身也是敏感数据。

需要：

- encryption；
- access control；
- tenant separation；
- retention policy。

## 8. Environment 和 Session

一个很好的抽象：

    Environment
      ↓
    workspace + dependencies

    Session
      ↓
    conversation + agent state

这样可以：

    prewarm Environment
         ↓
    attach Session

## 9. 课堂练习

设计三个状态：

    cold
    warm
    ready

然后计算：

    cold start = image + dependency + runtime
    warm start = runtime
    ready start = attach only

思考：

> 哪些资源可以提前准备？

## 10. 面试题

### Q：Prewarm 和 Snapshot 有什么区别？

Prewarm 是提前准备一个将要使用的环境；Snapshot 是保存某个环境状态，之后可以从这个状态恢复或复制。

### Q：为什么 Sandbox Pool 很难做？

因为复用环境会引入状态残留和跨 Session 数据泄露问题。
