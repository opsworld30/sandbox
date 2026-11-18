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

Snapshot 是把某个时间点的环境状态保存下来，之后恢复或从它创建新的实例。

    Prepared Environment
       ↓
    Snapshot
       ↓
    Restore / Clone
       ↓
    New Sandbox

Snapshot 的粒度依实现而不同：可能只是磁盘 / 文件系统状态，也可能是 VM 的内存和磁盘状态。不能默认所有产品的 Snapshot 都保存了进程内存、网络连接和完整 Session 状态。

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

一个有用的抽象：

    Environment
      ↓
    image + workspace + dependencies + execution policy

    Agent Session
      ↓
    conversation + agent config + tool state

这样可以先准备 Environment，再将它关联到 Agent Session。但 Environment 是否可以跨 Session 复用、能否并发挂载、是否允许写入，必须按平台能力定义；不要默认多个租户共享同一个可写工作区。

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


## 11. Prewarm、Snapshot、Pool 不能混为一谈

- **Prewarm**：提前做环境准备工作，降低任务到来后的等待时间。
- **Snapshot**：保存某个状态，供恢复或复制。
- **Pool**：预先准备可分配实例，降低创建延迟。

它们可以组合，但不是同一个机制。OpenAI Agents API 的 Pre-warm 公开流程是先准备 OpenAI-hosted environment（包、文件、setup commands），待 ready 后再 attach 到 Session；这不意味着它一定保存了 VM 内存快照。

## 12. 复用环境前的安全 Reset 清单

至少验证：

- 所有旧进程和后台进程已经退出；
- 临时目录和 writable layer 已清空；
- 凭证、环境变量和代理状态已清理；
- SSH Agent / Unix Socket / Browser Profile 不会跨租户复用；
- workspace 与 cache 的 owner / ACL 正确；
- 网络 namespace、路由和 egress policy 已重建；
- 新 Session 使用新的身份、policy version 和 audit context。

如果不能证明 reset 完整，就销毁实例而不是放回共享 Pool。


## 13. OpenAI Pre-warmed Environment 的共享语义

OpenAI Agents API 当前提供两种需要区分的情况：

- 普通 OpenAI-hosted Session：每个 Session 有独立 workspace，文件在 Sandbox 存续期间跨 turns 保留。
- 通过 Pre-warm API 单独创建的共享 Environment：可以附加多个 Session；当前文档说明新建共享 Environment 最多支持 128 个 Session，附加的 Session 会共享同一工作区，包括文件、进程、已安装包和环境配置，而每个 Session 的对话历史仍独立。

因此，共享 Pre-warmed Environment 不是“每个 Session 自动得到一份隔离副本”。如果任务之间不能互相读取或修改状态，应分别创建 Environment，而不是只创建多个 Session。

参考：https://developers.openai.com/api/docs/guides/agents-api/environments/prewarmed


## 14. Pre-warm Environment 的生命周期也会影响 Pool 设计

截至 2026-11-18，OpenAI Pre-warm 文档还说明：

- Environment 未附加 Session 时，5 分钟后过期；预热应靠近任务开始时间。
- 预热阶段（附加前）不收取 Sandbox 容器使用费；附加 Session 后按标准容器价格计费。
- 第一个 Session 附加后开始 20 分钟 idle lifetime；任一 Session 活动或通过 Environment File API 操作会延长空闲期限。
- 没有活动任务时，Environment 可能进入 `suspended`，并保留 checkpoint 7 天；Suspended 会停止计算资源，但不会删除共享 workspace。
- 删除某个 Session 只会把该 Session 从共享 Environment 中移除，不会删除 workspace 或 checkpoint。

这些是 OpenAI 当前 API 的具体生命周期规则，不是所有 Sandbox Pool 的通用默认值。旧版 Environment 可能仍保持单 Session 生命周期。

参考：https://developers.openai.com/api/docs/guides/agents-api/environments/prewarmed

## 本讲实验代码

- [Git Worktree Snapshot](../labs/11-worktree-snapshot/README.md)
- [Prewarm / Snapshot / Pool 状态机](../labs/21-prewarm-pool/README.md)

这些是对应主题的可运行教学实验；具体操作系统要求和安全边界以各 Lab README 为准。
